// Go 1.22 / OpenTelemetry Go / Structured JSON Logging
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/trace"
)

type StructuredLog struct {
	Timestamp string `json:"timestamp"`
	Level     string `json:"level"`
	Service   string `json:"service"`
	TraceID   string `json:"trace_id"`
	SpanID    string `json:"span_id"`
	Message   string `json:"message"`
	Duration  int64  `json:"duration_ms"`
}

func ExecuteDatabaseQuery(ctx context.Context, tracer trace.Tracer, query string) error {
	// Створюємо новий спан у контексті Go
	ctx, span := tracer.Start(ctx, "db:pg_exec",
		trace.WithSpanKind(trace.SpanKindClient),
		trace.WithAttributes(attribute.String("db.system", "postgresql")),
	)
	defer span.End()

	sc := span.SpanContext()
	traceID := sc.TraceID().String()
	spanID := sc.SpanID().String()

	start := time.Now()
	// Симуляція повільного запиту
	err := simulateQueryExecution()
	duration := time.Since(start).Milliseconds()

	if err != nil {
		span.RecordError(err)

		// Формуємо лог із чітко прив'язаним TraceID та SpanID
		logEntry := StructuredLog{
			Timestamp: time.Now().UTC().Format(time.RFC3339),
			Level:     "ERROR",
			Service:   "device-telemetry-service",
			TraceID:   traceID,
			SpanID:    spanID,
			Message:   fmt.Sprintf("DB query failed: %v", err),
			Duration:  duration,
		}
		bytes, _ := json.Marshal(logEntry)
		fmt.Println(string(bytes))
		return err
	}

	return nil
}

func simulateQueryExecution() error {
	return fmt.Errorf("canceling statement due to statement timeout")
}
