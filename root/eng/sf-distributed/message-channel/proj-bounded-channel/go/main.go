package main

import (
	"context"
	"errors"
	"time"
)

var (
	ErrChannelClosed  = errors.New("channel is closed")
	ErrChannelFull    = errors.New("channel is full")
	ErrChannelEmpty   = errors.New("channel is empty")
	ErrChannelTimeout = errors.New("channel operation timed out")
)

type BoundedChannel[T any] struct {
	ch chan T
}

func NewBoundedChannel[T any](capacity int) *BoundedChannel[T] {
	return &BoundedChannel[T]{
		ch: make(chan T, capacity),
	}
}

// Блокуючий запис із підтримкою контексту
func (b *BoundedChannel[T]) Send(ctx context.Context, item T) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case b.ch <- item:
		return nil
	}
}

// Неблокуючий запис (Try-Send)
func (b *BoundedChannel[T]) TrySend(item T) error {
	select {
	case b.ch <- item:
		return nil
	default:
		return ErrChannelFull
	}
}

// Блокуюче вичитування
func (b *BoundedChannel[T]) Recv(ctx context.Context) (T, error) {
	var zero T
	select {
	case <-ctx.Done():
		return zero, ctx.Err()
	case item, ok := <-b.ch:
		if !ok {
			return zero, ErrChannelClosed
		}
		return item, nil
	}
}

// Вичитування з тайм-аутом
func (b *BoundedChannel[T]) RecvTimeout(d time.Duration) (T, error) {
	var zero T
	timer := time.NewTimer(d)
	defer timer.Stop()

	select {
	case item, ok := <-b.ch:
		if !ok {
			return zero, ErrChannelClosed
		}
		return item, nil
	case <-timer.C:
		return zero, ErrChannelTimeout
	}
}

// Закриття каналу
func (b *BoundedChannel[T]) Close() {
	close(b.ch)
}
