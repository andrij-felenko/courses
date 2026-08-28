// ambassador.go — Високорівнева реалізація Ambassador-проксі на Go
package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"math/rand"
	"net"
	"net/http"
	"os"
	"os/signal"
	"sync/atomic"
	"syscall"
	"time"
)

type CircuitState int32

const (
	StateClosed CircuitState = iota
	StateOpen
	StateHalfOpen
)

type CircuitBreaker struct {
	state          int32
	failures       int32
	threshold      int32
	recoveryTime   time.Duration
	lastStateShift int64
}

func NewCircuitBreaker(threshold int32, recovery time.Duration) *CircuitBreaker {
	return &CircuitBreaker{
		threshold:    threshold,
		recoveryTime: recovery,
	}
}

func (cb *CircuitBreaker) Allow() bool {
	st := CircuitState(atomic.LoadInt32(&cb.state))
	if st == StateOpen {
		lastShift := time.Unix(0, atomic.LoadInt64(&cb.lastStateShift))
		if time.Since(lastShift) >= cb.recoveryTime {
			if atomic.CompareAndSwapInt32(&cb.state, int32(StateOpen), int32(StateHalfOpen)) {
				atomic.StoreInt64(&cb.lastStateShift, time.Now().UnixNano())
				return true
			}
		}
		return false
	}
	return true
}

func (cb *CircuitBreaker) RecordSuccess() {
	atomic.StoreInt32(&cb.failures, 0)
	atomic.StoreInt32(&cb.state, int32(StateClosed))
}

func (cb *CircuitBreaker) RecordFailure() {
	fails := atomic.AddInt32(&cb.failures, 1)
	st := CircuitState(atomic.LoadInt32(&cb.state))
	if fails >= cb.threshold || st == StateHalfOpen {
		atomic.StoreInt32(&cb.state, int32(StateOpen))
		atomic.StoreInt64(&cb.lastStateShift, time.Now().UnixNano())
	}
}

type AmbassadorProxy struct {
	upstreamURL string
	client      *http.Client
	cb          *CircuitBreaker
}

func NewAmbassadorProxy(upstreamURL string) *AmbassadorProxy {
	transport := &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 20,
		IdleConnTimeout:     90 * time.Second,
		DialContext: (&net.Dialer{
			Timeout:   2 * time.Second,
			KeepAlive: 30 * time.Second,
		}).DialContext,
	}

	return &AmbassadorProxy{
		upstreamURL: upstreamURL,
		client:      &http.Client{Transport: transport, Timeout: 3 * time.Second},
		cb:          NewCircuitBreaker(5, 10*time.Second),
	}
}

func (p *AmbassadorProxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if !p.cb.Allow() {
		http.Error(w, "Circuit Breaker Open", http.StatusServiceUnavailable)
		return
	}

	var resp *http.Response
	var err error
	maxRetries := 3

	for attempt := 1; attempt <= maxRetries; attempt++ {
		req, _ := http.NewRequestWithContext(r.Context(), r.Method, p.upstreamURL+r.RequestURI, r.Body)
		for k, v := range r.Header {
			req.Header[k] = v
		}

		resp, err = p.client.Do(req)
		if err == nil && resp.StatusCode < 500 {
			break
		}

		if attempt < maxRetries {
			jitter := time.Duration(rand.Intn(25)) * time.Millisecond
			backoff := time.Duration(50*(1<<attempt))*time.Millisecond + jitter
			time.Sleep(backoff)
		}
	}

	if err != nil || (resp != nil && resp.StatusCode >= 500) {
		p.cb.RecordFailure()
		http.Error(w, "Upstream Gateway Error", http.StatusBadGateway)
		return
	}

	p.cb.RecordSuccess()
	defer resp.Body.Close()

	for k, v := range resp.Header {
		w.Header()[k] = v
	}
	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
}

func main() {
	proxy := NewAmbassadorProxy("http://127.0.0.1:9000")
	server := &http.Server{
		Addr:    "127.0.0.1:8081",
		Handler: proxy,
	}

	go func() {
		fmt.Println("[Ambassador-Go] Проксі запущено на 127.0.0.1:8081")
		if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			fmt.Printf("Помилка сервера: %v\n", err)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, syscall.SIGINT)
	<-stop

	fmt.Println("[Ambassador-Go] Плавна зупинка (Graceful Shutdown)...")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = server.Shutdown(ctx)
	fmt.Println("[Ambassador-Go] Проксі зупинено.")
}
