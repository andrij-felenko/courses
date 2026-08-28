package main

import (
	"context"
	"errors"
	"sync"
	"time"
)

// Database визначає інтерфейс первинного сховища
type Database interface {
	Get(key string) (string, bool)
	Set(key, value string)
	BatchSet(items map[string]string)
}

// MockDatabase імітує мережеві та дискові затримки
type MockDatabase struct {
	mu      sync.RWMutex
	storage map[string]string
}

func NewMockDatabase() *MockDatabase {
	return &MockDatabase{storage: make(map[string]string)}
}

func (db *MockDatabase) Get(key string) (string, bool) {
	time.Sleep(10 * time.Millisecond) // імітація IO
	db.mu.RLock()
	defer db.mu.RUnlock()
	val, ok := db.storage[key]
	return val, ok
}

func (db *MockDatabase) Set(key, value string) {
	time.Sleep(15 * time.Millisecond)
	db.mu.Lock()
	defer db.mu.Unlock()
	db.storage[key] = value
}

func (db *MockDatabase) BatchSet(items map[string]string) {
	time.Sleep(25 * time.Millisecond)
	db.mu.Lock()
	defer db.mu.Unlock()
	for k, v := range items {
		db.storage[k] = v
	}
}

// CacheStore — швидкий кеш у пам'яті
type CacheStore struct {
	mu  sync.RWMutex
	mem map[string]string
}

func NewCacheStore() *CacheStore {
	return &CacheStore{mem: make(map[string]string)}
}

func (c *CacheStore) Get(key string) (string, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	val, ok := c.mem[key]
	return val, ok
}

func (c *CacheStore) Set(key, value string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.mem[key] = value
}

func (c *CacheStore) Del(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	delete(c.mem, key)
}

// ── Singleflight Group для Read-Through ─────────────────────────────────────
type call struct {
	wg  sync.WaitGroup
	val string
	ok  bool
	err error
}

type SingleflightGroup struct {
	mu sync.Mutex
	m  map[string]*call
}

func NewSingleflightGroup() *SingleflightGroup {
	return &SingleflightGroup{m: make(map[string]*call)}
}

func (g *SingleflightGroup) Do(key string, fn func() (string, bool)) (string, bool) {
	g.mu.Lock()
	if c, ok := g.m[key]; ok {
		g.mu.Unlock()
		c.wg.Wait()
		return c.val, c.ok
	}
	c := new(call)
	c.wg.Add(1)
	g.m[key] = c
	g.mu.Unlock()

	c.val, c.ok = fn()
	c.wg.Done()

	g.mu.Lock()
	delete(g.m, key)
	g.mu.Unlock()

	return c.val, c.ok
}

// ── 1. Cache-Aside Manager ──────────────────────────────────────────────────
type CacheAsideManager struct {
	db    Database
	cache *CacheStore
}

func NewCacheAsideManager(db Database, cache *CacheStore) *CacheAsideManager {
	return &CacheAsideManager{db: db, cache: cache}
}

func (m *CacheAsideManager) Get(key string) (string, bool) {
	if val, ok := m.cache.Get(key); ok {
		return val, true // влучання
	}
	val, ok := m.db.Get(key)
	if ok {
		m.cache.Set(key, val) // наповнення на промах
	}
	return val, ok
}

func (m *CacheAsideManager) Update(key, value string) {
	m.db.Set(key, value) // спершу сховище правди
	m.cache.Del(key)    // інвалідація кешу (delete замість set)
}

// ── 2. Read-Through Manager ────────────────────────────────────────────────
type ReadThroughManager struct {
	db    Database
	cache *CacheStore
	sf    *SingleflightGroup
}

func NewReadThroughManager(db Database, cache *CacheStore) *ReadThroughManager {
	return &ReadThroughManager{
		db:    db,
		cache: cache,
		sf:    NewSingleflightGroup(),
	}
}

func (m *ReadThroughManager) Get(key string) (string, bool) {
	if val, ok := m.cache.Get(key); ok {
		return val, true
	}
	return m.sf.Do(key, func() (string, bool) {
		if val, ok := m.cache.Get(key); ok {
			return val, true
		}
		val, ok := m.db.Get(key)
		if ok {
			m.cache.Set(key, val)
		}
		return val, ok
	})
}

// ── 3. Write-Through Manager ────────────────────────────────────────────────
type WriteThroughManager struct {
	db    Database
	cache *CacheStore
}

func NewWriteThroughManager(db Database, cache *CacheStore) *WriteThroughManager {
	return &WriteThroughManager{db: db, cache: cache}
}

func (m *WriteThroughManager) Get(key string) (string, bool) {
	if val, ok := m.cache.Get(key); ok {
		return val, true
	}
	val, ok := m.db.Get(key)
	if ok {
		m.cache.Set(key, val)
	}
	return val, ok
}

func (m *WriteThroughManager) Set(key, value string) {
	m.db.Set(key, value)
	m.cache.Set(key, value)
}

// ── 4. Write-Behind Manager ─────────────────────────────────────────────────
var ErrBufferFull = errors.New("write buffer overflow: backpressure triggered")

type WriteBehindManager struct {
	db        Database
	cache     *CacheStore
	mu        sync.Mutex
	buffer    map[string]string
	maxBuffer int
	ctx       context.Context
	cancel    context.CancelFunc
	wg        sync.WaitGroup
}

func NewWriteBehindManager(db Database, cache *CacheStore, flushInterval time.Duration, maxBuffer int) *WriteBehindManager {
	ctx, cancel := context.WithCancel(context.Background())
	mgr := &WriteBehindManager{
		db:        db,
		cache:     cache,
		buffer:    make(map[string]string),
		maxBuffer: maxBuffer,
		ctx:       ctx,
		cancel:    cancel,
	}

	mgr.wg.Add(1)
	go mgr.worker(flushInterval)
	return mgr
}

func (m *WriteBehindManager) Set(key, value string) error {
	m.cache.Set(key, value) // миттєва доступність у кеші

	m.mu.Lock()
	defer m.mu.Unlock()

	if len(m.buffer) >= m.maxBuffer {
		return ErrBufferFull // захист оперативної пам'яті
	}

	m.buffer[key] = value // злиття мутацій в один запис
	return nil
}

func (m *WriteBehindManager) worker(interval time.Duration) {
	defer m.wg.Done()
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-m.ctx.Done():
			m.flush()
			return
		case <-ticker.C:
			m.flush()
		}
	}
}

func (m *WriteBehindManager) flush() {
	m.mu.Lock()
	if len(m.buffer) == 0 {
		m.mu.Unlock()
		return
	}
	batch := m.buffer
	m.buffer = make(map[string]string)
	m.mu.Unlock()

	m.db.BatchSet(batch)
}

func (m *WriteBehindManager) Close() {
	m.cancel()
	m.wg.Wait() // гарантований злив буфера перед завершенням
}
