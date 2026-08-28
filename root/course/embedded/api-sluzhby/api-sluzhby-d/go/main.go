package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"
)

// VersionMeta описує стан депрекації версії API
type VersionMeta struct {
	Deprecated   bool
	SunsetDate   string
	MigrationURL string
}

var versionRegistry = map[string]VersionMeta{
	"v1": {
		Deprecated:   true,
		SunsetDate:   "Sun, 15 Nov 2026 00:00:00 GMT",
		MigrationURL: "https://api.iot-corp.com/docs/v1-to-v2",
	},
	"v2": {
		Deprecated: false,
	},
}

// MetricsStorage потокобезпечно збирає виклики старих версій
type MetricsStorage struct {
	mu     sync.Mutex
	counts map[string]int64
}

var metrics = &MetricsStorage{counts: make(map[string]int64)}

func (m *MetricsStorage) Inc(key string) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.counts[key]++
}

// DeprecationMiddleware впроваджує заголовки RFC 8594 та збирає телеметрію
func DeprecationMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		apiVersion := "v2"
		if strings.HasPrefix(r.URL.Path, "/v1/") {
			apiVersion = "v1"
		} else if strings.HasPrefix(r.URL.Path, "/v2/") {
			apiVersion = "v2"
		} else if v := r.Header.Get("X-API-Version"); v != "" {
			apiVersion = v
		}

		// Фіксація метрики звернення
		ua := r.UserAgent()
		if ua == "" {
			ua = "unknown-device"
		}
		metrics.Inc(fmt.Sprintf("%s:%s:%s", apiVersion, r.Method, ua))

		// Додавання заголовків депрекації
		if meta, exists := versionRegistry[apiVersion]; exists && meta.Deprecated {
			w.Header().Set("Deprecation", "true")
			if meta.SunsetDate != "" {
				w.Header().Set("Sunset", meta.SunsetDate)
			}
			if meta.MigrationURL != "" {
				w.Header().Set("Link", fmt.Sprintf("<%s>; rel=\"deprecation\"; type=\"text/html\"", meta.MigrationURL))
			}
		}

		next.ServeHTTP(w, r)
	})
}

// Обробник v1 телеметрії
func handleTelemetryV1(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	resp := map[string]interface{}{
		"id": "dev-101",
		"v":  230.2,
		"a":  5.1,
		"ts": time.Now().Unix(),
	}
	json.NewEncoder(w).Encode(resp)
}

// Обробник v2 телеметрії
func handleTelemetryV2(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	resp := map[string]interface{}{
		"device_id": "dev-101",
		"metrics": map[string]int{
			"voltage_mv": 230200,
			"current_ma": 5100,
		},
		"timestamp_iso": time.Now().UTC().Format(time.RFC3339),
	}
	json.NewEncoder(w).Encode(resp)
}

// Обробник асинхронного створення команд
func handleCreateCommandV2(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	cmdID := fmt.Sprintf("cmd_%d", time.Now().UnixNano()/1e6)
	location := fmt.Sprintf("/v2/devices/dev-101/commands/%s", cmdID)

	w.Header().Set("Location", location)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted) // 202 Accepted

	resp := map[string]interface{}{
		"id":         cmdID,
		"device_id":  "dev-101",
		"status":     "PENDING",
		"created_at": time.Now().UTC().Format(time.RFC3339),
	}
	json.NewEncoder(w).Encode(resp)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/v1/devices/dev-101/telemetry", handleTelemetryV1)
	mux.HandleFunc("/v2/devices/dev-101/telemetry", handleTelemetryV2)
	mux.HandleFunc("/v2/devices/dev-101/commands", handleCreateCommandV2)

	server := &http.Server{
		Addr:         ":8080",
		Handler:      DeprecationMiddleware(mux),
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 5 * time.Second,
	}

	log.Println("IoT API Gateway запущено на порту :8080")
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Помилка сервера: %v", err)
	}
}
