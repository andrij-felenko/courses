package main

import (
	"fmt"
	"math"
	"math/rand"
	"sync"
	"time"
)

// BackoffCalculator розраховує затримку з Full Jitter.
type BackoffCalculator struct {
	Base float64
	Max  float64
	rnd  *rand.Rand
	mu   sync.Mutex
}

func NewBackoff(base, max time.Duration) *BackoffCalculator {
	return &BackoffCalculator{
		Base: base.Seconds(),
		Max:  max.Seconds(),
		rnd:  rand.New(rand.NewSource(time.Now().UnixNano())),
	}
}

func (b *BackoffCalculator) Calculate(attempt int) time.Duration {
	b.mu.Lock()
	defer b.mu.Unlock()

	temp := math.Min(b.Max, b.Base*math.Pow(2, float64(attempt)))
	sleepSeconds := b.rnd.Float64() * temp
	return time.Duration(sleepSeconds * float64(time.Second))
}

// AdmissionGate регулює покроковий допуск вузлів через Token Bucket.
type AdmissionGate struct {
	rate       float64 // токенів на секунду
	capacity   float64 // максимальна ємність
	tokens     float64
	lastUpdate time.Time
	mu         sync.Mutex
}

func NewAdmissionGate(rate, capacity float64) *AdmissionGate {
	return &AdmissionGate{
		rate:       rate,
		capacity:   capacity,
		tokens:     capacity,
		lastUpdate: time.Now(),
	}
}

func (g *AdmissionGate) Allow() bool {
	g.mu.Lock()
	defer g.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(g.lastUpdate).Seconds()
	g.lastUpdate = now

	g.tokens = math.Min(g.capacity, g.tokens+elapsed*g.rate)
	if g.tokens >= 1.0 {
		g.tokens -= 1.0
		return true
	}
	return false
}

func main() {
	backoff := NewBackoff(100*time.Millisecond, 10*time.Second)
	gate := NewAdmissionGate(50.0, 100.0) // 50 вузлів/сек

	fmt.Println("--- (Go) Розрахунок інтервалів Backoff з Full Jitter ---")
	for i := 0; i < 5; i++ {
		d := backoff.Calculate(i)
		fmt.Printf("Спроба %d: затримка %v\n", i, d)
	}

	fmt.Println("\n--- (Go) Перевірка шлюзу допуску ---")
	allowed, rejected := 0, 0
	for i := 0; i < 120; i++ {
		if gate.Allow() {
			allowed++
		} else {
			rejected++
		}
	}
	fmt.Printf("Дозволено запитів: %d, Відхилено (перелито): %d\n", allowed, rejected)
}
