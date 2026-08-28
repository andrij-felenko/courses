// deprecation_router.go — HTTP Middleware керування Sunset і Deprecation у Go
package main

import (
	"fmt"
	"net/http"
	"time"
)

type DeprecationPolicy struct {
	EndpointPath    string
	DeprecationTime time.Time
	SunsetTime      time.Time
	DocURL          string
	SuccessorPath   string
}

type DeprecationMiddleware struct {
	policies map[string]DeprecationPolicy
}

func NewDeprecationMiddleware() *DeprecationMiddleware {
	return &DeprecationMiddleware{
		policies: make(map[string]DeprecationPolicy),
	}
}

func (m *DeprecationMiddleware) RegisterPolicy(p DeprecationPolicy) {
	m.policies[p.EndpointPath] = p
}

func (m *DeprecationMiddleware) Handler(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		policy, exists := m.policies[r.URL.Path]
		if !exists {
			next.ServeHTTP(w, r)
			return
		}

		now := time.Now()
		if now.After(policy.SunsetTime) {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusGone) // 410 Gone
			fmt.Fprintf(w, `{"error":"Gone","message":"API disabled. Use %s"}`, policy.SuccessorPath)
			return
		}

		// Додавання RFC заголовків
		w.Header().Set("Deprecation", fmt.Sprintf("@%d", policy.DeprecationTime.Unix()))
		w.Header().Set("Sunset", policy.SunsetTime.Format(http.TimeFormat))
		w.Header().Set("Link", fmt.Sprintf("<%s>; rel=\"deprecation\", <%s>; rel=\"successor-version\"",
			policy.DocURL, policy.SuccessorPath))

		next.ServeHTTP(w, r)
	})
}

func main() {
	middleware := NewDeprecationMiddleware()
	now := time.Now()

	middleware.RegisterPolicy(DeprecationPolicy{
		EndpointPath:    "/api/v1/telemetry",
		DeprecationTime: now.AddDate(0, -1, 0),
		SunsetTime:      now.AddDate(0, 2, 0),
		DocURL:          "https://developer.dh.io/docs/v1-sunset",
		SuccessorPath:   "/api/v2/telemetry",
	})

	fmt.Println("Deprecation middleware успішно ініціалізовано.")
}
