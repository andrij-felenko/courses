package tracing

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"net/http"
	"strings"
)

type contextKey struct{}

var traceContextKey = contextKey{}

type TraceContext struct {
	Version [1]byte
	TraceID [16]byte
	SpanID  [8]byte
	Flags   byte
}

func (tc TraceContext) IsSampled() bool {
	return (tc.Flags & 0x01) != 0
}

func ExtractTraceparent(header string) (TraceContext, error) {
	if len(header) < 55 {
		return TraceContext{}, errors.New("traceparent header too short")
	}
	parts := strings.Split(header, "-")
	if len(parts) < 4 || len(parts[0]) != 2 || len(parts[1]) != 32 || len(parts[2]) != 16 || len(parts[3]) != 2 {
		return TraceContext{}, errors.New("malformed traceparent format")
	}

	var ctx TraceContext
	if _, err := hex.Decode(ctx.Version[:], []byte(parts[0])); err != nil || ctx.Version[0] == 0xFF {
		return TraceContext{}, errors.New("invalid version")
	}
	if ctx.Version[0] == 0x00 && len(header) != 55 {
		return TraceContext{}, errors.New("invalid length for version 00")
	}

	if _, err := hex.Decode(ctx.TraceID[:], []byte(parts[1])); err != nil || ctx.TraceID == [16]byte{} {
		return TraceContext{}, errors.New("invalid trace ID")
	}
	if _, err := hex.Decode(ctx.SpanID[:], []byte(parts[2])); err != nil || ctx.SpanID == [8]byte{} {
		return TraceContext{}, errors.New("invalid span ID")
	}

	var flags [1]byte
	if _, err := hex.Decode(flags[:], []byte(parts[3])); err != nil {
		return TraceContext{}, errors.New("invalid flags")
	}
	ctx.Flags = flags[0]

	return ctx, nil
}

func (tc TraceContext) String() string {
	return fmt.Sprintf("%02x-%032x-%016x-%02x", tc.Version[0], tc.TraceID, tc.SpanID, tc.Flags)
}

func GenerateSpanID() [8]byte {
	var id [8]byte
	rand.Read(id[:])
	return id
}

// HTTP Middleware для автоматичного поширення контексту
func TracingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		incomingHeader := r.Header.Get("traceparent")
		traceCtx, err := ExtractTraceparent(incomingHeader)
		if err != nil {
			// Якщо заголовок відсутній або пошкоджений, генеруємо новий кореневий трейс
			traceCtx = TraceContext{Version: [1]byte{0x00}, Flags: 0x01}
			rand.Read(traceCtx.TraceID[:])
		}

		// Створюємо дочірній спан для поточної операції
		traceCtx.SpanID = GenerateSpanID()
		ctx := context.WithValue(r.Context(), traceContextKey, traceCtx)

		w.Header().Set("traceparent", traceCtx.String())
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
