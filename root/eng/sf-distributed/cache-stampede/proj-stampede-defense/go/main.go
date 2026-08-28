package main

import (
	"context"
	"math"
	"math/rand"
	"sync"
	"time"
)

type cacheEntry struct {
	value     interface{}
	expiry    time.Time
	deltaSec  float64
}

type call struct {
	wg  sync.WaitGroup
	val interface{}
	err error
}

type StampedeGuard struct {
	mu       sync.RWMutex
	cache    map[string]cacheEntry
	flightMu sync.Mutex
	inFlight map[string]*call
	beta     float64
}

func NewStampedeGuard(beta float64) *StampedeGuard {
	return &StampedeGuard{
		cache:    make(map[string]cacheEntry),
		inFlight: make(map[string]*call),
		beta:     beta,
	}
}

func (g *StampedeGuard) shouldRecomputeXFetch(e cacheEntry) bool {
	now := time.Now()
	if now.After(e.expiry) {
		return true
	}
	if e.deltaSec <= 0 {
		return false
	}
	u := rand.Float64()
	if u == 0 {
		u = 0.0001
	}
	shift := -e.deltaSec * g.beta * math.Log(u)
	threshold := now.Add(time.Duration(shift * float64(time.Second)))
	return threshold.After(e.expiry)
}

func (g *StampedeGuard) Get(ctx context.Context, key string, ttl time.Duration, fetcher func() (interface{}, error)) (interface{}, error) {
	// 1. Читання з кешу
	g.mu.RLock()
	entry, found := g.cache[key]
	g.mu.RUnlock()

	if found && !g.shouldRecomputeXFetch(entry) {
		return entry.value, nil
	}

	// 2. Single-Flight дедуплікація
	g.flightMu.Lock()
	if c, ok := g.inFlight[key]; ok {
		g.flightMu.Unlock()
		c.wg.Wait()
		return c.val, c.err
	}

	c := new(call)
	c.wg.Add(1)
	g.inFlight[key] = c
	g.flightMu.Unlock()

	// 3. Виконання обчислення лідером
	start := time.Now()
	c.val, c.err = fetcher()
	delta := time.Since(start).Seconds()

	if c.err == nil {
		g.mu.Lock()
		g.cache[key] = cacheEntry{
			value:    c.val,
			expiry:   time.Now().Add(ttl),
			deltaSec: delta,
		}
		g.mu.Unlock()
	}

	c.wg.Done()

	g.flightMu.Lock()
	delete(g.inFlight, key)
	g.flightMu.Unlock()

	return c.val, c.err
}
