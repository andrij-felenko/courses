package main

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

type Lsn uint64

func ParseLsn(s string) (Lsn, error) {
	parts := strings.Split(strings.TrimSpace(s), "/")
	if len(parts) != 2 {
		return 0, errors.New("невірний формат LSN (очікується X/Y)")
	}
	high, err := strconv.ParseUint(parts[0], 16, 32)
	if err != nil {
		return 0, err
	}
	low, err := strconv.ParseUint(parts[1], 16, 32)
	if err != nil {
		return 0, err
	}
	return Lsn((high << 32) | low), nil
}

func (l Lsn) String() string {
	high := uint32(l >> 32)
	low := uint32(l & 0xFFFFFFFF)
	return fmt.Sprintf("%X/%X", high, low)
}

type ReplicaNode struct {
	Endpoint   string
	IsAlive    atomic.Bool
	AppliedLsn atomic.Uint64
	LagMs      atomic.Uint32
}

type LagAwareRouter struct {
	primaryEndpoint   string
	replicas          []*ReplicaNode
	maxLagMs          uint32
	maxFallbackRps    uint32
	rrCounter         atomic.Uint64
	fallbackWindowSec atomic.Uint64
	fallbackCounter   atomic.Uint32
	mu                sync.RWMutex
}

func NewLagAwareRouter(primary string, replicas []string, maxLagMs uint32, maxFallbackRps uint32) *LagAwareRouter {
	r := &LagAwareRouter{
		primaryEndpoint: primary,
		maxLagMs:        maxLagMs,
		maxFallbackRps:  maxFallbackRps,
	}
	for _, ep := range replicas {
		node := &ReplicaNode{Endpoint: ep}
		node.IsAlive.Store(true)
		r.replicas = append(r.replicas, node)
	}
	return r
}

func (r *LagAwareRouter) ClassifyQuery(sql string) bool {
	trimmed := strings.ToUpper(strings.TrimSpace(sql))
	if strings.HasPrefix(trimmed, "SELECT") {
		if strings.Contains(trimmed, "FOR UPDATE") || strings.Contains(trimmed, "FOR SHARE") {
			return false // Запис
		}
		return true // Читання
	}
	return false
}

func (r *LagAwareRouter) Route(sql string, requiredLsn Lsn) (string, error) {
	if !r.ClassifyQuery(sql) {
		return r.primaryEndpoint, nil
	}

	r.mu.RLock()
	var candidates []string
	for _, rep := range r.replicas {
		if !rep.IsAlive.Load() {
			continue
		}
		if rep.LagMs.Load() > r.maxLagMs {
			continue
		}
		if requiredLsn > 0 && Lsn(rep.AppliedLsn.Load()) < requiredLsn {
			continue
		}
		candidates = append(candidates, rep.Endpoint)
	}
	r.mu.RUnlock()

	if len(candidates) > 0 {
		idx := r.rrCounter.Add(1) % uint64(len(candidates))
		return candidates[idx], nil
	}

	// Fallback на Primary
	nowSec := uint64(time.Now().Unix())
	if nowSec != r.fallbackWindowSec.Load() {
		r.fallbackWindowSec.Store(nowSec)
		r.fallbackCounter.Store(0)
	}

	if r.fallbackCounter.Add(1) <= r.maxFallbackRps {
		return r.primaryEndpoint, nil
	}

	return "", errors.New("усі репліки відстають, ліміт fallback на primary перевищено")
}

func main() {
	router := NewLagAwareRouter(
		"postgres-primary:5432",
		[]string{"postgres-replica-1:5432", "postgres-replica-2:5432"},
		2000,
		500,
	)

	// Імітація стану
	router.replicas[0].AppliedLsn.Store(0x16B3C00)
	router.replicas[0].LagMs.Store(15)

	router.replicas[1].AppliedLsn.Store(0x16B3800)
	router.replicas[1].LagMs.Store(600)

	sessionLsn, _ := ParseLsn("0/16B3A40")
	target, _ := router.Route("SELECT * FROM users WHERE id = 42", sessionLsn)
	fmt.Printf("Запит читання з LSN %s скеровано на: %s\n", sessionLsn, target)
}
