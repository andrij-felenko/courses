package snowflake

import (
	"errors"
	"sync"
	"time"
)

const (
	Epoch          = int64(1288834974657)
	WorkerBits     = 5
	DatacenterBits = 5
	SequenceBits   = 12

	MaxWorkerId     = -1 ^ (-1 << WorkerBits)
	MaxDatacenterId = -1 ^ (-1 << DatacenterBits)
	SequenceMask    = -1 ^ (-1 << SequenceBits)

	WorkerShift    = SequenceBits
	DatacenterShift = SequenceBits + WorkerBits
	TimestampShift = SequenceBits + WorkerBits + DatacenterBits
)

var ErrClockRegression = errors.New("clock moved backwards beyond threshold")

type Generator struct {
	mu            sync.Mutex
	workerID      int64
	datacenterID  int64
	sequence      int64
	lastTimestamp int64
}

func NewGenerator(workerID, datacenterID int64) (*Generator, error) {
	if workerID < 0 || workerID > MaxWorkerId || datacenterID < 0 || datacenterID > MaxDatacenterId {
		return nil, errors.New("worker or datacenter ID out of range")
	}
	return &Generator{
		workerID:     workerID,
		datacenterID: datacenterID,
	}, nil
}

func (g *Generator) NextID() (int64, error) {
	g.mu.Lock()
	defer g.mu.Unlock()

	now := time.Now().UnixMilli()

	if now < g.lastTimestamp {
		drift := g.lastTimestamp - now
		if drift < 5 {
			for now <= g.lastTimestamp {
				now = time.Now().UnixMilli()
			}
		} else {
			return 0, ErrClockRegression
		}
	}

	if now == g.lastTimestamp {
		g.sequence = (g.sequence + 1) & SequenceMask
		if g.sequence == 0 {
			for now <= g.lastTimestamp {
				now = time.Now().UnixMilli()
			}
		}
	} else {
		g.sequence = 0
	}

	g.lastTimestamp = now

	id := ((now - Epoch) << TimestampShift) |
		(g.datacenterID << DatacenterShift) |
		(g.workerID << WorkerShift) |
		g.sequence

	return id, nil
}
