package main

import (
	"context"
	"crypto/fnv"
	"errors"
	"fmt"
	"sort"
	"strconv"
	"sync"
	"sync/atomic"
	"time"
)

// Модель запису
type Record struct {
	Key       string
	Value     string
	Timestamp int64
}

// 64-бітний хеш FNV-1a
func fnv1a64(key string) uint64 {
	h := fnv.New64a()
	_, _ = h.Write([]byte(key))
	return h.Sum64()
}

// Фізичний клієнт шарду
type ShardClient struct {
	ShardID  string
	Endpoint string
}

func (c *ShardClient) Put(key, value string) error {
	if key == "" || value == "" {
		return errors.New("invalid key or value")
	}
	return nil
}

func (c *ShardClient) Get(key string) (string, error) {
	return fmt.Sprintf("val_from_%s_for_%s", c.ShardID, key), nil
}

func (c *ShardClient) Scan(ctx context.Context, filter string) ([]Record, error) {
	select {
	case <-time.After(10 * time.Millisecond):
		return []Record{
			{Key: "k1_" + c.ShardID, Value: "payload", Timestamp: 100 + int64(len(c.ShardID))},
			{Key: "k2_" + c.ShardID, Value: "payload", Timestamp: 200 + int64(len(c.ShardID))},
		}, nil
	case <-ctx.Done():
		return nil, ctx.Err()
	}
}

// Кільце консистентного хешування
type ConsistentHashRing struct {
	virtualNodes int
	sortedTokens []uint64
	tokenToShard map[uint64]string
}

func NewConsistentHashRing(vnodes int) *ConsistentHashRing {
	return &ConsistentHashRing{
		virtualNodes: vnodes,
		tokenToShard: make(map[uint64]string),
	}
}

func (r *ConsistentHashRing) AddShard(shardID string) {
	for i := 0; i < r.virtualNodes; i++ {
		token := fnv1a64(shardID + "#vnode_" + strconv.Itoa(i))
		r.sortedTokens = append(r.sortedTokens, token)
		r.tokenToShard[token] = shardID
	}
	sort.Slice(r.sortedTokens, func(i, j int) bool {
		return r.sortedTokens[i] < r.sortedTokens[j]
	})
}

func (r *ConsistentHashRing) GetShard(key string) (string, error) {
	if len(r.sortedTokens) == 0 {
		return "", errors.New("hash ring is empty")
	}
	token := fnv1a64(key)
	idx := sort.Search(len(r.sortedTokens), func(i int) bool {
		return r.sortedTokens[i] >= token
	})
	if idx == len(r.sortedTokens) {
		idx = 0 // Wrap-around
	}
	return r.tokenToShard[r.sortedTokens[idx]], nil
}

// Топологія кластера
type ClusterTopology struct {
	Version uint64
	Ring    *ConsistentHashRing
	Shards  map[string]*ShardClient
}

// Маршрутизатор шардингу
type ShardRouter struct {
	topology atomic.Pointer[ClusterTopology]
}

func NewShardRouter() *ShardRouter {
	r := &ShardRouter{}
	initTop := &ClusterTopology{
		Version: 1,
		Ring:    NewConsistentHashRing(128),
		Shards:  make(map[string]*ShardClient),
	}
	r.topology.Store(initTop)
	return r
}

func (r *ShardRouter) UpdateTopology(shards map[string]string) {
	newTop := &ClusterTopology{
		Ring:   NewConsistentHashRing(128),
		Shards: make(map[string]*ShardClient),
	}
	for id, ep := range shards {
		newTop.Shards[id] = &ShardClient{ShardID: id, Endpoint: ep}
		newTop.Ring.AddShard(id)
	}

	oldTop := r.topology.Load()
	if oldTop != nil {
		newTop.Version = oldTop.Version + 1
	} else {
		newTop.Version = 1
	}

	r.topology.Store(newTop)
	fmt.Printf("[Router] Topology atomically updated to version %d with %d shards\n", newTop.Version, len(shards))
}

func (r *ShardRouter) Put(key, value string) error {
	top := r.topology.Load()
	shardID, err := top.Ring.GetShard(key)
	if err != nil {
		return err
	}
	client, ok := top.Shards[shardID]
	if !ok {
		return fmt.Errorf("shard %s not found", shardID)
	}
	return client.Put(key, value)
}

func (r *ShardRouter) Get(key string) (string, error) {
	top := r.topology.Load()
	shardID, err := top.Ring.GetShard(key)
	if err != nil {
		return "", err
	}
	client, ok := top.Shards[shardID]
	if !ok {
		return "", fmt.Errorf("shard %s not found", shardID)
	}
	return client.Get(key)
}

// Scatter-Gather опитування з паралельними горутинами
func (r *ShardRouter) ScatterGatherScan(ctx context.Context, filter string, timeout time.Duration) ([]Record, error) {
	top := r.topology.Load()
	shards := top.Shards

	if len(shards) == 0 {
		return nil, nil
	}

	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	type result struct {
		records []Record
		err     error
	}

	resChan := make(chan result, len(shards))
	var wg sync.WaitGroup

	for _, client := range shards {
		wg.Add(1)
		go func(c *ShardClient) {
			defer wg.Done()
			recs, err := c.Scan(ctx, filter)
			resChan <- result{records: recs, err: err}
		}(client)
	}

	wg.Wait()
	close(resChan)

	var aggregated []Record
	for res := range resChan {
		if res.err == nil {
			aggregated = append(aggregated, res.records...)
		} else {
			fmt.Printf("[Router] Shard scan error: %v\n", res.err)
		}
	}

	sort.Slice(aggregated, func(i, j int) bool {
		return aggregated[i].Timestamp > aggregated[j].Timestamp
	})

	return aggregated, nil
}

func main() {
	router := NewShardRouter()

	router.UpdateTopology(map[string]string{
		"shard-0": "10.0.1.10:3306",
		"shard-1": "10.0.1.11:3306",
		"shard-2": "10.0.1.12:3306",
	})

	_ = router.Put("user_10842", "{ name: 'Alice' }")
	_ = router.Put("user_99214", "{ name: 'Bob' }")

	v1, _ := router.Get("user_10842")
	v2, _ := router.Get("user_99214")
	fmt.Printf("[Client] Read user_10842: %s\n", v1)
	fmt.Printf("[Client] Read user_99214: %s\n", v2)

	fmt.Println("[Client] Executing Scatter-Gather scan...")
	records, _ := router.ScatterGatherScan(context.Background(), "status = 'ACTIVE'", 100*time.Millisecond)
	fmt.Printf("[Client] Total records returned: %d\n", len(records))
	for _, rec := range records {
		fmt.Printf("  - Key: %s | TS: %d\n", rec.Key, rec.Timestamp)
	}
}
