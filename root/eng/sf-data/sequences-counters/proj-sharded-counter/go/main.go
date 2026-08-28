package counter

import (
	"sync/atomic"
)

type shard struct {
	value uint64
	_     [56]byte // 64 байти кеш-лінії мінус 8 байтів uint64
}

type ShardedCounter struct {
	shards []shard
	mask   uint64
}

func NewShardedCounter(numShards int) *ShardedCounter {
	power := 1
	for power < numShards {
		power <<= 1
	}
	return &ShardedCounter{
		shards: make([]shard, power),
		mask:   uint64(power - 1),
	}
}

func (c *ShardedCounter) Add(threadID uint64, delta uint64) {
	slot := threadID & c.mask
	atomic.AddUint64(&c.shards[slot].value, delta)
}

func (c *ShardedCounter) Get() uint64 {
	var total uint64
	for i := range c.shards {
		total += atomic.LoadUint64(&c.shards[i].value)
	}
	return total
}
