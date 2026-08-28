// Go 1.22 / OpenTelemetry Go SDK / net/http
package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

type traceKey struct{}

type TraceContext struct {
	TraceID string
	SpanID  string
	Sampled bool
}

func generateHex(bytes int) string {
	b := make([]byte, bytes)
	rand.Read(b)
	return hex.EncodeToString(b)
}

func ExtractTraceContext(r *http.Request) TraceContext {
	header := r.Header.Get("traceparent")
	if strings.HasPrefix(header, "00-") {
		parts := strings.Split(header, "-")
		if len(parts) >= 4 {
			return TraceContext{
				TraceID: parts[1],
				SpanID:  parts[2],
				Sampled: parts[3] == "01",
			}
		}
	}
	return TraceContext{
		TraceID: generateHex(16),
		SpanID:  generateHex(8),
		Sampled: true,
	}
}

func TelemetryMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		tc := ExtractTraceContext(r)
		ctx := context.WithValue(r.Context(), traceKey{}, tc)

		w.Header().Set("traceparent", fmt.Sprintf("00-%s-%s-01", tc.TraceID, tc.SpanID))

		LogJSON(ctx, "INFO", "device-telemetry-svc", "Запит прийнято в HTTP middleware")
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func LogJSON(ctx context.Context, level, service, msg string) {
	tc, _ := ctx.Value(traceKey{}).(TraceContext)
	logData := map[string]interface{}{
		"timestamp": time.Now().UTC().Format(time.RFC3339Nano),
		"level":     level,
		"service":   service,
		"trace_id":  tc.TraceID,
		"span_id":   tc.SpanID,
		"message":   msg,
	}
	bytes, _ := json.Marshal(logData)
	fmt.Println(string(bytes))
}
