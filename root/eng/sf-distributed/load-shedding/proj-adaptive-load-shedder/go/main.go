package loadshedder

import (
	"context"
	"errors"
	"math"
	"sync/atomic"
	"time"
)

type RequestTier uint8

const (
	Tier0System RequestTier = iota
	Tier1Critical
	Tier2Interactive
	Tier3Background
)

var (
	ErrDeadlineExpired    = errors.New("load_shedder: deadline expired before processing")
	ErrQueueDelayHigh     = errors.New("load_shedder: queue delay exceeded target (CoDel)")
	ErrPriorityShed       = errors.New("load_shedder: shed due to priority tiering")
	ErrCapacityExhausted  = errors.New("load_shedder: active capacity limit exhausted")
)

type Config struct {
	TargetSojourn time.Duration
	Interval      time.Duration
	MaxCapacity   int64
	MinCapacity   int64
}

type LoadShedder struct {
	cfg Config

	inflight         atomic.Int64
	dynamicCapacity  atomic.Int64
	intervalStartNs  atomic.Int64
	minSojournNs     atomic.Int64
	inDroppingState  atomic.Bool
	totalDrops       atomic.Uint64
}

func NewLoadShedder(cfg Config) *LoadShedder {
	if cfg.TargetSojourn == 0 {
		cfg.TargetSojourn = 20 * time.Millisecond
	}
	if cfg.Interval == 0 {
		cfg.Interval = 100 * time.Millisecond
	}
	if cfg.MaxCapacity == 0 {
		cfg.MaxCapacity = 1000
	}
	if cfg.MinCapacity == 0 {
		cfg.MinCapacity = 50
	}

	ls := &LoadShedder{
		cfg: cfg,
	}
	ls.dynamicCapacity.Store(cfg.MaxCapacity)
	ls.intervalStartNs.Store(time.Now().UnixNano())
	ls.minSojournNs.Store(math.MaxInt64)
	return ls
}

type Ticket struct {
	shedder  *LoadShedder
	released atomic.Bool
}

func (t *Ticket) Done() {
	if t != nil && t.released.CompareAndSwap(false, true) {
		t.shedder.inflight.Add(-1)
	}
}

func (ls *LoadShedder) TryAdmit(
	ctx context.Context,
	tier RequestTier,
	entryTime time.Time,
	minExecTime time.Duration,
) (*Ticket, error) {
	now := time.Now()

	// Рубіж 1: Перевірка залишкового дедлайну контексту
	if deadline, ok := ctx.Deadline(); ok {
		if deadline.Before(now.Add(minExecTime)) {
			ls.totalDrops.Add(1)
			return nil, ErrDeadlineExpired
		}
	}

	// Рубіж 2: Вимірювання часу очікування в черзі
	sojourn := now.Sub(entryTime)
	ls.updateCoDel(now.UnixNano(), sojourn.Nanoseconds())

	// Рубіж 3: Скидання за рівнем пріоритету в режимі Dropping
	if ls.inDroppingState.Load() {
		if tier == Tier3Background {
			ls.totalDrops.Add(1)
			return nil, ErrPriorityShed
		}
		if tier == Tier2Interactive && sojourn > ls.cfg.TargetSojourn {
			ls.totalDrops.Add(1)
			return nil, ErrQueueDelayHigh
		}
	}

	// Рубіж 4: Перевірка ліміту активної конкурентності
	limit := ls.dynamicCapacity.Load()
	curr := ls.inflight.Load()

	for curr < limit {
		if ls.inflight.CompareAndSwap(curr, curr+1) {
			return &Ticket{shedder: ls}, nil
		}
		curr = ls.inflight.Load()
	}

	// Резерв для критичних системних операцій
	if tier == Tier0System {
		ls.inflight.Add(1)
		return &Ticket{shedder: ls}, nil
	}

	ls.totalDrops.Add(1)
	return nil, ErrCapacityExhausted
}

func (ls *LoadShedder) updateCoDel(nowNs, sojournNs int64) {
	for {
		oldMin := ls.minSojournNs.Load()
		if sojournNs >= oldMin {
			break
		}
		if ls.minSojournNs.CompareAndSwap(oldMin, sojournNs) {
			break
		}
	}

	start := ls.intervalStartNs.Load()
	intervalNs := ls.cfg.Interval.Nanoseconds()

	if nowNs-start > intervalNs {
		minSojourn := ls.minSojournNs.Swap(sojournNs)
		ls.intervalStartNs.Store(nowNs)

		targetNs := ls.cfg.TargetSojourn.Nanoseconds()
		if minSojourn > targetNs {
			ls.inDroppingState.Store(true)
			// Мультиплікативне зниження місткості
			curr := ls.dynamicCapacity.Load()
			newCap := int64(float64(curr) * 0.85)
			if newCap < ls.cfg.MinCapacity {
				newCap = ls.cfg.MinCapacity
			}
			ls.dynamicCapacity.Store(newCap)
		} else {
			ls.inDroppingState.Store(false)
			// Адитивне відновлення місткості
			curr := ls.dynamicCapacity.Load()
			newCap := curr + 10
			if newCap > ls.cfg.MaxCapacity {
				newCap = ls.cfg.MaxCapacity
			}
			ls.dynamicCapacity.Store(newCap)
		}
	}
}
