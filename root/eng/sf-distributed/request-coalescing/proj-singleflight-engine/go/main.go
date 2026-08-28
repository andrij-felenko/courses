package singleflight

import (
    "context"
    "errors"
    "fmt"
    "sync"
)

type Result[T any] struct {
    Val    T
    Err    error
    Shared bool
}

type call[T any] struct {
    wg      sync.WaitGroup
    val     T
    err     error
    waiters int
}

type Group[T any] struct {
    mu sync.Mutex
    m  map[string]*call[T]
}

func NewGroup[T any]() *Group[T] {
    return &Group[T]{
        m: make(map[string]*call[T]),
    }
}

// Do блокує виклик до завершення рейсу
func (g *Group[T]) Do(key string, fn func() (T, error)) (T, error, bool) {
    g.mu.Lock()
    if c, ok := g.m[key]; ok {
        c.waiters++
        g.mu.Unlock()
        c.wg.Wait()
        return c.val, c.err, true
    }

    c := new(call[T])
    c.wg.Add(1)
    g.m[key] = c
    g.mu.Unlock()

    g.execute(key, c, fn)

    return c.val, c.err, false
}

// DoChan повертає неблокуючий канал результату з підтримкою контексту
func (g *Group[T]) DoChan(ctx context.Context, key string, fn func() (T, error)) <-chan Result[T] {
    ch := make(chan Result[T], 1)

    g.mu.Lock()
    if c, ok := g.m[key]; ok {
        c.waiters++
        g.mu.Unlock()
        go func() {
            c.wg.Wait()
            ch <- Result[T]{Val: c.val, Err: c.err, Shared: true}
        }()
        return ch
    }

    c := new(call[T])
    c.wg.Add(1)
    g.m[key] = c
    g.mu.Unlock()

    go func() {
        g.execute(key, c, fn)
        ch <- Result[T]{Val: c.val, Err: c.err, Shared: false}
    }()

    return ch
}

func (g *Group[T]) execute(key string, c *call[T], fn func() (T, error)) {
    defer func() {
        if r := recover(); r != nil {
            c.err = fmt.Errorf("singleflight panic: %v", r)
        }
        g.mu.Lock()
        delete(g.m, key)
        g.mu.Unlock()
        c.wg.Done()
    }()

    c.val, c.err = fn()
}
