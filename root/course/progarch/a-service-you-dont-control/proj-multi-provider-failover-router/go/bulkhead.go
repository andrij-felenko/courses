package main

import (
	"context"
	"errors"
	"sync"
	"time"
)

var (
	// ErrBulkheadFull повертається, коли ліміт паралелізму та черга вичерпані.
	ErrBulkheadFull = errors.New("bulkhead: черга та слоти паралелізму вичерпані (fail-fast)")
)

// BulkheadConfig задає конфігурацію семафорної перебірки.
type BulkheadConfig struct {
	MaxConcurrent int           // Максимальна кількість одночасних операцій
	MaxQueueSize  int           // Максимальний розмір черги очікування
	QueueTimeout  time.Duration // Максимальний час перебування в черзі
}

// Bulkhead реалізує семафорну перебірку для ізоляції паралелізму за законом Літтла.
type Bulkhead struct {
	config    BulkheadConfig
	semaphore chan struct{}
	queueSem  chan struct{}
	mu        sync.Mutex
	active    int
	inQueue   int
}

// NewBulkhead ініціалізує нову перебірку на Go-каналах.
func NewBulkhead(cfg BulkheadConfig) *Bulkhead {
	return &Bulkhead{
		config:    cfg,
		semaphore: make(chan struct{}, cfg.MaxConcurrent),
		queueSem:  make(chan struct{}, cfg.MaxQueueSize),
	}
}

// Execute виконує функцію fn під захистом перебірки.
func (b *Bulkhead) Execute(ctx context.Context, fn func(ctx context.Context) (Response, error)) (Response, error) {
	// 1. Спроба негайно захопити слот паралелізму без очікування
	select {
	case b.semaphore <- struct{}{}:
		b.incActive()
		defer b.release()
		return fn(ctx)
	default:
	}

	// 2. Спроба стати в чергу очікування
	select {
	case b.queueSem <- struct{}{}:
		b.incQueue()
		defer b.decQueue()
	default:
		// Черга повна — негайний fail-fast без блокування ресурсів
		return Response{}, ErrBulkheadFull
	}

	// 3. Очікуємо звільнення робочого слота або завершення таймауту черги/контексту
	timer := time.NewTimer(b.config.QueueTimeout)
	defer timer.Stop()

	select {
	case b.semaphore <- struct{}{}:
		b.incActive()
		defer b.release()
		return fn(ctx)
	case <-timer.C:
		return Response{}, ErrBulkheadFull
	case <-ctx.Done():
		return Response{}, ctx.Err()
	}
}

func (b *Bulkhead) incActive() {
	b.mu.Lock()
	b.active++
	b.mu.Unlock()
}

func (b *Bulkhead) release() {
	<-b.semaphore
	b.mu.Lock()
	b.active--
	b.mu.Unlock()
}

func (b *Bulkhead) incQueue() {
	b.mu.Lock()
	b.inQueue++
	b.mu.Unlock()
}

func (b *Bulkhead) decQueue() {
	<-b.queueSem
	b.mu.Lock()
	b.inQueue--
	b.mu.Unlock()
}

// Stats повертає кількість активних викликів і розмір поточної черги.
func (b *Bulkhead) Stats() (active int, queued int) {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.active, b.inQueue
}\n
