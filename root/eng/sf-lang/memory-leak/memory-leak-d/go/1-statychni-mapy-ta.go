// Go
package main

import "sync"

type Registry struct {
	mu    sync.Mutex
	cache map[string][]byte
}

func (r *Registry) Store(key string, data []byte) {
	r.mu.Lock()
	defer r.mu.Unlock()
	// Мапа ніколи не видаляє старі ключі -> необмежене розбухання купи
	r.cache[key] = data
}
