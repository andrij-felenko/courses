package main

import (
	"context"
	"errors"
	"math/rand"
	"net/http"
	"sync/atomic"
	"time"
)

// ChaosConfig визначає параметри впорскування збоїв під час Game Day.
type ChaosConfig struct {
	LatencyMs   int32 // Додаткова затримка у мс
	ErrorRate   int32 // Відсоток генерації 500 Internal Error (0-100)
	ReadyStatus int32 // 1 - ready, 0 - degraded (fail readiness)
}

type ChaosMiddleware struct {
	config atomic.Pointer[ChaosConfig]
}

func NewChaosMiddleware() *ChaosMiddleware {
	m := &ChaosMiddleware{}
	m.config.Store(&ChaosConfig{ReadyStatus: 1})
	return m
}

func (m *ChaosMiddleware) Handler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		cfg := m.config.Load()

		// Перевірка заголовку Game Day канарки
		if r.Header.Get("X-Chaos-Target") == "twin-cache" {
			if cfg.LatencyMs > 0 {
				time.Sleep(time.Duration(cfg.LatencyMs) * time.Millisecond)
			}

			if cfg.ErrorRate > 0 && rand.Int32n(100) < cfg.ErrorRate {
				http.Error(w, "Chaos Injector: Simulated Cache Stampede Error", http.StatusInternalServerError)
				return
			}
		}

		next.ServeHTTP(w, r)
	})
}

// LivenessHandler перевіряє лише базову життєздатність процесів (event loop).
func (m *ChaosMiddleware) LivenessHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}

// ReadinessHandler відключає под від трафіку при збоях downstream без вбивання процесів.
func (m *ChaosMiddleware) ReadinessHandler(w http.ResponseWriter, r *http.Request) {
	cfg := m.config.Load()
	if atomic.LoadInt32(&cfg.ReadyStatus) == 0 {
		http.Error(w, "Service Degraded: Readiness Failed", http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("READY"))
}
