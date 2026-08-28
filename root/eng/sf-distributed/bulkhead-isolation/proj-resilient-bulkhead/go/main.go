package resilience

import (
	"context"
	"errors"
	"sync/atomic"
	"time"
)

var (
	ErrBulkheadFull    = errors.New("bulkhead capacity exceeded")
	ErrBulkheadTimeout = errors.New("bulkhead acquisition timeout")
)

type Metrics struct {
	AvailablePermits int64
	MaxPermits       int64
	TotalAcquired    uint64
	TotalRejected    uint64
}

type Bulkhead struct {
	name            string
	maxPermits      int64
	semaphore       chan struct{}
	maxWaitDuration time.Duration
	totalAcquired   uint64
	totalRejected   uint64
}

type Permit struct {
	bulkhead *Bulkhead
	released uint32
}

func (p *Permit) Release() {
	if atomic.CompareAndSwapUint32(&p.released, 0, 1) {
		<-p.bulkhead.semaphore
	}
}

func NewBulkhead(name string, maxConcurrentCalls int, maxWait time.Duration) *Bulkhead {
	return &Bulkhead{
		name:            name,
		maxPermits:      int64(maxConcurrentCalls),
		semaphore:       make(chan struct{}, maxConcurrentCalls),
		maxWaitDuration: maxWait,
	}
}

func (b *Bulkhead) Acquire(ctx context.Context) (*Permit, error) {
	if b.maxWaitDuration <= 0 {
		select {
		case b.semaphore <- struct{}{}:
			atomic.AddUint64(&b.totalAcquired, 1)
			return &Permit{bulkhead: b}, nil
		default:
			atomic.AddUint64(&b.totalRejected, 1)
			return nil, ErrBulkheadFull
		}
	}

	timer := time.NewTimer(b.maxWaitDuration)
	defer timer.Stop()

	select {
	case b.semaphore <- struct{}{}:
		atomic.AddUint64(&b.totalAcquired, 1)
		return &Permit{bulkhead: b}, nil
	case <-timer.C:
		atomic.AddUint64(&b.totalRejected, 1)
		return nil, ErrBulkheadTimeout
	case <-ctx.Done():
		atomic.AddUint64(&b.totalRejected, 1)
		return nil, ctx.Err()
	}
}

func (b *Bulkhead) Execute(ctx context.Context, action func() error, fallback func(err error) error) error {
	permit, err := b.Acquire(ctx)
	if err != nil {
		if fallback != nil {
			return fallback(err)
		}
		return err
	}
	defer permit.Release()

	return action()
}

func (b *Bulkhead) GetMetrics() Metrics {
	currentInFlight := int64(len(b.semaphore))
	return Metrics{
		AvailablePermits: b.maxPermits - currentInFlight,
		MaxPermits:       b.maxPermits,
		TotalAcquired:    atomic.LoadUint64(&b.totalAcquired),
		TotalRejected:    atomic.LoadUint64(&b.totalRejected),
	}
}
