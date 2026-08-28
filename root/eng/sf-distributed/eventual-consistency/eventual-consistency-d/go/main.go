package main

import (
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
)

// DatabaseReplica представляє вузол бази даних
type DatabaseReplica struct {
	name       string
	mu         sync.RWMutex
	storage    map[string]string
	currentLSN uint64
}

func NewDatabaseReplica(name string) *DatabaseReplica {
	return &DatabaseReplica{
		name:    name,
		storage: make(map[string]string),
	}
}

func (r *DatabaseReplica) ApplyWrite(key, val string, lsn uint64) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.storage[key] = val
	atomic.StoreUint64(&r.currentLSN, lsn)
}

func (r *DatabaseReplica) Read(key string, minLSN uint64) (string, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	cur := atomic.LoadUint64(&r.currentLSN)
	if cur < minLSN {
		return "", fmt.Errorf("replica %s lagging: current LSN %d < required %d", r.name, cur, minLSN)
	}

	val, exists := r.storage[key]
	if !exists {
		return "", errors.New("key not found")
	}
	return val, nil
}

// SessionConsistentClient забезпечує Read-Your-Writes
type SessionConsistentClient struct {
	replicas   []*DatabaseReplica
	globalLSN  *uint64
	sessionLSN uint64
}

func NewSessionClient(replicas []*DatabaseReplica, globalLSN *uint64) *SessionConsistentClient {
	return &SessionConsistentClient{
		replicas:  replicas,
		globalLSN: globalLSN,
	}
}

func (c *SessionConsistentClient) Write(key, val string) {
	newLSN := atomic.AddUint64(c.globalLSN, 1)
	c.replicas[0].ApplyWrite(key, val, newLSN)
	c.sessionLSN = newLSN
	fmt.Printf("[Client Write] Записано '%s = %s'. Сесійний LSN: %d\n", key, val, c.sessionLSN)
}

func (c *SessionConsistentClient) Read(key string) (string, error) {
	for _, replica := range c.replicas {
		val, err := replica.Read(key, c.sessionLSN)
		if err == nil {
			fmt.Printf("[Client Read] Успішно прочитано з %s (LSN %d): %s\n", replica.name, replica.currentLSN, val)
			return val, nil
		}
		fmt.Printf("[Client Read Bypass] %s відстає. Пропускаємо...\n", replica.name)
	}
	return "", errors.New("all replicas lagging")
}

func main() {
	var globalLSN uint64

	primary := NewDatabaseReplica("Primary-EU")
	replicaFast := NewDatabaseReplica("Replica-Fast")
	replicaLagging := NewDatabaseReplica("Replica-Lagging")

	client := NewSessionClient([]*DatabaseReplica{primary, replicaFast, replicaLagging}, &globalLSN)

	fmt.Println("=== 1. Клієнт виконує оновлення даних ===")
	client.Write("user:101:status", "VIP-Tier")

	fmt.Println("\n=== 2. Асинхронна реплікація з лагом ===")
	replicaFast.ApplyWrite("user:101:status", "VIP-Tier", 1)
	// replicaLagging залишається на LSN = 0

	fmt.Println("\n=== 3. Клієнт читає свій запис із кластера ===")
	val, _ := client.Read("user:101:status")
	fmt.Printf("Підсумковий прочитаний результат: %s\n", val)
}
