package main

import (
	"context"
	"fmt"
	"hash/fnv"
	"math"
	"math/rand"
	"sort"
	"strconv"
	"sync"
	"time"
)

// ── 1. Структура кешованого запису ──────────────────────────────────────────
type CacheItem struct {
	Value              string
	Expiry             time.Time
	ComputeDurationSec float64
}

// ── 2. Кільце узгодженого гешування (Consistent Hash Ring) ──────────────────
type ConsistentHashRing struct {
	mu             sync.RWMutex
	vnodesPerNode  int
	ring           []uint32
	vnodeToNodeMap map[uint32]string
}

func NewConsistentHashRing(vnodesPerNode int) *ConsistentHashRing {
	return &ConsistentHashRing{
		vnodesPerNode:  vnodesPerNode,
		vnodeToNodeMap: make(map[uint32]string),
	}
}

func hashKey(key string) uint32 {
	h := fnv.New32a()
	h.Write([]byte(key))
	return h.Sum32()
}

func (r *ConsistentHashRing) AddNode(nodeID string) {
	r.mu.Lock()
	defer r.mu.Unlock()

	for v := 0; v < r.vnodesPerNode; v++ {
		vnodeKey := nodeID + "#vnode_" + strconv.Itoa(v)
		h := hashKey(vnodeKey)
		r.ring = append(r.ring, h)
		r.vnodeToNodeMap[h] = nodeID
	}
	sort.Slice(r.ring, func(i, j int) bool { return r.ring[i] < r.ring[j] })
}

func (r *ConsistentHashRing) GetNode(key string) string {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if len(r.ring) == 0 {
		return ""
	}
	h := hashKey(key)
	idx := sort.Search(len(r.ring), func(i int) bool { return r.ring[i] >= h })
	if idx == len(r.ring) {
		idx = 0 // Wrap-around
	}
	return r.vnodeToNodeMap[r.ring[idx]]
}

// ── 3. Singleflight координатор дедуплікації ────────────────────────────────
type call struct {
	wg  sync.WaitGroup
	val string
	err error
}

type SingleflightGroup struct {
	mu sync.Mutex
	m  map[string]*call
}

func NewSingleflightGroup() *SingleflightGroup {
	return &SingleflightGroup{m: make(map[string]*call)}
}

func (g *SingleflightGroup) Do(key string, fn func() (string, error)) (string, error) {
	g.mu.Lock()
	if c, ok := g.m[key]; ok {
		g.mu.Unlock()
		c.wg.Wait()
		return c.val, c.err
	}
	c := new(call)
	c.wg.Add(1)
	g.m[key] = c
	g.mu.Unlock()

	c.val, c.err = fn()
	c.wg.Done()

	g.mu.Lock()
	delete(g.m, key)
	g.mu.Unlock()

	return c.val, c.err
}

// ── 4. Клієнт стійкого розподіленого кешу ──────────────────────────────────
type ResilientCacheClient struct {
	ring         *ConsistentHashRing
	singleflight *SingleflightGroup
	beta         float64
	storageMu    sync.RWMutex
	mockStorage  map[string]map[string]CacheItem
}

func NewResilientCacheClient(ring *ConsistentHashRing, beta float64) *ResilientCacheClient {
	return &ResilientCacheClient{
		ring:         ring,
		singleflight: NewSingleflightGroup(),
		beta:         beta,
		mockStorage:  make(map[string]map[string]CacheItem),
	}
}

func (c *ResilientCacheClient) shouldEarlyRefresh(item CacheItem, now time.Time) bool {
	if now.After(item.Expiry) {
		return true
	}
	u := rand.Float64()
	if u <= 0 {
		u = 0.0001
	}
	// XFetch: now - beta * delta * ln(u) > expiry
	earlyMargin := time.Duration(-c.beta * item.ComputeDurationSec * math.Log(u) * float64(time.Second))
	return now.Add(earlyMargin).After(item.Expiry)
}

func (c *ResilientCacheClient) GetOrCompute(
	ctx context.Context,
	key string,
	ttl time.Duration,
	dbLoader func() (string, error),
) (string, error) {
	targetNode := c.ring.GetNode(key)
	now := time.Now()

	c.storageMu.RLock()
	nodeData, existsNode := c.mockStorage[targetNode]
	item, existsItem := nodeData[key]
	c.storageMu.RUnlock()

	if existsNode && existsItem {
		if !c.shouldEarlyRefresh(item, now) {
			return item.Value, nil
		}
	}

	return c.singleflight.Do(key, func() (string, error) {
		start := time.Now()
		freshVal, err := dbLoader()
		if err != nil {
			return "", err
		}
		durationSec := time.Since(start).Seconds()

		c.storageMu.Lock()
		if _, ok := c.mockStorage[targetNode]; !ok {
			c.mockStorage[targetNode] = make(map[string]CacheItem)
		}
		c.mockStorage[targetNode][key] = CacheItem{
			Value:              freshVal,
			Expiry:             time.Now().Add(ttl),
			ComputeDurationSec: durationSec,
		}
		c.storageMu.Unlock()

		return freshVal, nil
	})
}

func main() {
	ring := NewConsistentHashRing(100)
	ring.AddNode("cache-01.internal:6379")
	ring.AddNode("cache-02.internal:6379")
	ring.AddNode("cache-03.internal:6379")

	client := NewResilientCacheClient(ring, 1.0)

	val, err := client.GetOrCompute(context.Background(), "user:100:profile", 30*time.Second, func() (string, error) {
		fmt.Println("-> [СУБД] Читання профілю користувача 100")
		return `{"id":100,"name":"Bob","role":"admin"}`, nil
	})

	if err == nil {
		fmt.Printf("<- Отримано: %s\n", val)
	}
}
