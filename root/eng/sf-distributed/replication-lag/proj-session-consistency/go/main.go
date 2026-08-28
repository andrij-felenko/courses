package main

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

type LSN uint64

type DatabaseReplica struct {
	id         string
	appliedLSN atomic.Uint64
	mu         sync.Mutex
	cond       *sync.Cond
}

func NewDatabaseReplica(id string) *DatabaseReplica {
	r := &DatabaseReplica{id: id}
	r.cond = sync.NewCond(&r.mu)
	return r
}

func (r *DatabaseReplica) UpdateAppliedLSN(newLSN LSN) {
	r.mu.Lock()
	r.appliedLSN.Store(uint64(newLSN))
	r.mu.Unlock()
	r.cond.Broadcast()
}

func (r *DatabaseReplica) WaitForLSN(ctx context.Context, targetLSN LSN) bool {
	if LSN(r.appliedLSN.Load()) >= targetLSN {
		return true
	}

	done := make(chan struct{})
	go func() {
		r.mu.Lock()
		defer r.mu.Unlock()
		for LSN(r.appliedLSN.Load()) < targetLSN {
			r.cond.Wait()
			select {
			case <-ctx.Done():
				return
			default:
			}
		}
		close(done)
	}()

	select {
	case <-done:
		return true
	case <-ctx.Done():
		return false
	}
}

func (r *DatabaseReplica) ExecuteRead(query string) string {
	return fmt.Sprintf("Читання [%s] з репліки %s (LSN: %d)", query, r.id, r.appliedLSN.Load())
}

type DatabasePrimary struct {
	currentLSN atomic.Uint64
}

func (p *DatabasePrimary) ExecuteWrite(query string) LSN {
	newLSN := p.currentLSN.Add(1)
	fmt.Printf("[Primary] Запис: %s -> LSN: %d\n", query, newLSN)
	return LSN(newLSN)
}

func (p *DatabasePrimary) ExecuteRead(query string) string {
	return fmt.Sprintf("Читання [%s] з PRIMARY (LSN: %d)", query, p.currentLSN.Load())
}

type ClientSession struct {
	SessionID string
	MinLSN    LSN
}

func (s *ClientSession) ObserveLSN(lsn LSN) {
	if lsn > s.MinLSN {
		s.MinLSN = lsn
	}
}

type SessionRouter struct {
	primary        *DatabasePrimary
	replicas       []*DatabaseReplica
	maxReplicaWait time.Duration
}

func (router *SessionRouter) HandleWrite(session *ClientSession, query string) {
	commitLSN := router.primary.ExecuteWrite(query)
	session.ObserveLSN(commitLSN)
}

func (router *SessionRouter) HandleRead(session *ClientSession, query string) string {
	requiredLSN := session.MinLSN

	// 1. Пошук готової репліки
	var bestReplica *DatabaseReplica
	var bestLSN LSN

	for _, rep := range router.replicas {
		curLSN := LSN(rep.appliedLSN.Load())
		if curLSN >= requiredLSN {
			session.ObserveLSN(curLSN)
			return rep.ExecuteRead(query)
		}
		if curLSN > bestLSN {
			bestLSN = curLSN
			bestReplica = rep
		}
	}

	// 2. Очікування на найсвіжішій репліці
	if bestReplica != nil {
		ctx, cancel := context.WithTimeout(context.Background(), router.maxReplicaWait)
		defer cancel()
		if bestReplica.WaitForLSN(ctx, requiredLSN) {
			session.ObserveLSN(LSN(bestReplica.appliedLSN.Load()))
			return bestReplica.ExecuteRead(query)
		}
	}

	// 3. Fallback на Primary
	fmt.Printf("[Router] Репліки відстають. Fallback на Primary для LSN %d\n", requiredLSN)
	session.ObserveLSN(LSN(router.primary.currentLSN.Load()))
	return router.primary.ExecuteRead(query)
}
