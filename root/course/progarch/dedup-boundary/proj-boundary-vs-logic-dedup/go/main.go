// Go 1.22: Гібридна дедуплікація на межі та в домені

package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

type EdgeFilter struct {
	mu    sync.Mutex
	cache map[string]time.Time
	ttl   time.Duration
}

func NewEdgeFilter(ttl time.Duration) *EdgeFilter {
	return &EdgeFilter{
		cache: make(map[string]time.Time),
		ttl:   ttl,
	}
}

func (f *EdgeFilter) Allow(key string) bool {
	f.mu.Lock()
	defer f.mu.Unlock()

	now := time.Now()
	if exp, exists := f.cache[key]; exists && exp.After(now) {
		return false // Дублікат на межі!
	}

	f.cache[key] = now.Add(f.ttl)
	return true
}

type DomainService struct {
	mu           sync.Mutex
	dbUniqueKeys map[string]bool
}

func (s *DomainService) ExecuteTransaction(ctx context.Context, orderID, key string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.dbUniqueKeys[key] {
		return fmt.Errorf("DB_UNIQUE_VIOLATION: key %s already processed", key)
	}

	s.dbUniqueKeys[key] = true
	fmt.Printf("[Domain Go] Processed order %s with key %s\n", orderID, key)
	return nil
}

func main() {
	edge := NewEdgeFilter(5 * time.Minute)
	domain := &DomainService{dbUniqueKeys: make(map[string]bool)}

	key := "IDEM-GO-1001"

	// Запит 1
	if edge.Allow(key) {
		_ = domain.ExecuteTransaction(context.Background(), "ORD-1", key)
	}

	// Запит 2 (Retry) — блокується на межі
	if !edge.Allow(key) {
		fmt.Println("[Edge Go] Blocked duplicate request at gateway boundary.")
	}
}
