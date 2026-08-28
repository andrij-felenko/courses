package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"syscall"
	"time"
)

// TelemetryPayload представляє вхідний пакет даних від IoT-вузла.
type TelemetryPayload struct {
	DeviceID    string  `json:"device_id"`
	Timestamp   int64   `json:"timestamp"`
	Temperature float64 `json:"temperature"`
	Humidity    float64 `json:"humidity"`
	BatteryMV   uint16  `json:"battery_mv"`
	Checksum    uint16  `json:"checksum"`
}

// Validate перевіряє фізичну достовірність отриманих показників.
func (p *TelemetryPayload) Validate() error {
	if len(p.DeviceID) < 3 || len(p.DeviceID) > 32 {
		return errors.New("некоректна довжина device_id (має бути 3..32 символи)")
	}
	if p.Temperature < -40.0 || p.Temperature > 85.0 {
		return fmt.Errorf("температура %.2f поза робочим діапазоном [-40..85]", p.Temperature)
	}
	if p.Humidity < 0.0 || p.Humidity > 100.0 {
		return fmt.Errorf("вологість %.2f поза діапазоном [0..100]", p.Humidity)
	}
	if p.BatteryMV < 2000 || p.BatteryMV > 4500 {
		return fmt.Errorf("напруга батареї %d мВ поза діапазоном [2000..4500]", p.BatteryMV)
	}
	return nil
}

// MetricsTracker забезпечує потокобезпечний облік телеметрії.
type MetricsTracker struct {
	totalReceived atomic.Uint64
	totalErrors   atomic.Uint64
	mu            sync.RWMutex
	lastSeen      map[string]time.Time
}

func NewMetricsTracker() *MetricsTracker {
	return &MetricsTracker{
		lastSeen: make(map[string]time.Time),
	}
}

func (m *MetricsTracker) RecordSuccess(deviceID string) {
	m.totalReceived.Add(1)
	m.mu.Lock()
	m.lastSeen[deviceID] = time.Now()
	m.mu.Unlock()
}

func (m *MetricsTracker) RecordError() {
	m.totalErrors.Add(1)
}

// Server містить стан HTTP-служби.
type Server struct {
	tracker *MetricsTracker
}

func (s *Server) handleTelemetry(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, `{"error":"дозволено лише POST"}`, http.StatusMethodNotAllowed)
		return
	}

	// Обмежуємо розмір тіла запиту 4 КБ для захисту від атак вичерпання пам'яті
	r.Body = http.MaxBytesReader(w, r.Body, 4096)

	var payload TelemetryPayload
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()

	if err := decoder.Decode(&payload); err != nil {
		s.tracker.RecordError()
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "некоректний JSON: " + err.Error()})
		return
	}

	if err := payload.Validate(); err != nil {
		s.tracker.RecordError()
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "помилка валідації: " + err.Error()})
		return
	}

	s.tracker.RecordSuccess(payload.DeviceID)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]any{
		"status":      "ok",
		"received_at": time.Now().Unix(),
		"device_id":   payload.DeviceID,
	})
}

func main() {
	tracker := NewMetricsTracker()
	srv := &Server{tracker: tracker}

	mux := http.NewServeMux()
	mux.HandleFunc("/api/v1/telemetry", srv.handleTelemetry)

	httpServer := &http.Server{
		Addr:         ":8080",
		Handler:      mux,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 5 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Штатна зупинка (Graceful Shutdown)
	stopChan := make(chan os.Signal, 1)
	signal.Notify(stopChan, os.Interrupt, syscall.SIGTERM)

	go func() {
		log.Printf("Служба прийому телеметрії слухає http://localhost:8080")
		if err := httpServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("Помилка HTTP сервера: %v", err)
		}
	}()

	<-stopChan
	log.Println("Отримано сигнал зупинки, завершуємо активні з'єднання...")

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := httpServer.Shutdown(shutdownCtx); err != nil {
		log.Fatalf("Помилка примусової зупинки: %v", err)
	}

	log.Println("Службу успішно зупинено.")
}
