package main

import (
	"context"
	"fmt"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"sync"
	"sync/atomic"
	"time"
)

type Backend struct {
	URL          *url.URL
	Alive        bool
	mux          sync.RWMutex
	ReverseProxy *httputil.ReverseProxy
	ActiveConns  int64
}

func (b *Backend) SetAlive(alive bool) {
	b.mux.Lock()
	b.Alive = alive
	b.mux.Unlock()
}

func (b *Backend) IsAlive() bool {
	b.mux.RLock()
	alive := b.Alive
	b.mux.RUnlock()
	return alive
}

type ServerPool struct {
	backends []*Backend
	current  uint64
}

func (s *ServerPool) AddBackend(b *Backend) {
	s.backends = append(s.backends, b)
}

// Вибір за алгоритмом Least Connections серед живих вузлів
func (s *ServerPool) GetLeastConnectedBackend() *Backend {
	var minBackend *Backend
	minConns := int64(1000000)

	for _, b := range s.backends {
		if b.IsAlive() {
			conns := atomic.LoadInt64(&b.ActiveConns)
			if conns < minConns {
				minConns = conns
				minBackend = b
			}
		}
	}
	return minBackend
}

func (s *ServerPool) HealthCheck() {
	for _, b := range s.backends {
		status := "up"
		alive := isBackendAlive(b.URL)
		b.SetAlive(alive)
		if !alive {
			status = "down"
		}
		fmt.Printf("Health probe: %s [%s] (active: %d)\n", b.URL, status, atomic.LoadInt64(&b.ActiveConns))
	}
}

func isBackendAlive(u *url.URL) bool {
	timeout := 1 * time.Second
	conn, err := net.DialTimeout("tcp", u.Host, timeout)
	if err != nil {
		return false
	}
	_ = conn.Close()
	return true
}

func main() {
	pool := &ServerPool{}

	targetURLs := []string{
		"http://127.0.0.1:8081",
		"http://127.0.0.1:8082",
	}

	transport := &http.Transport{
		MaxIdleConns:        1000,
		MaxIdleConnsPerHost: 100,
		IdleConnTimeout:     90 * time.Second,
	}

	for _, target := range targetURLs {
		u, err := url.Parse(target)
		if err != nil {
			panic(err)
		}

		proxy := httputil.NewSingleHostReverseProxy(u)
		proxy.Transport = transport

		backend := &Backend{
			URL:          u,
			Alive:        true,
			ReverseProxy: proxy,
		}

		originalDirector := proxy.Director
		proxy.Director = func(req *http.Request) {
			originalDirector(req)
			req.Header.Set("X-Forwarded-Host", req.Host)
		}

		pool.AddBackend(backend)
	}

	// Фоновий цикл перевірки здоров'я
	go func() {
		t := time.NewTicker(time.Second * 5)
		for range t.C {
			pool.HealthCheck()
		}
	}()

	server := http.Server{
		Addr: ":8080",
		Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			peer := pool.GetLeastConnectedBackend()
			if peer != nil {
				atomic.AddInt64(&peer.ActiveConns, 1)
				defer atomic.AddInt64(&peer.ActiveConns, -1)
				peer.ReverseProxy.ServeHTTP(w, r)
				return
			}
			http.Error(w, "Service Unavailable: No healthy backends", http.StatusServiceUnavailable)
		}),
	}

	fmt.Println("L7 Reverse Proxy запущено на :8080")
	if err := server.ListenAndServe(); err != nil {
		panic(err)
	}
}
