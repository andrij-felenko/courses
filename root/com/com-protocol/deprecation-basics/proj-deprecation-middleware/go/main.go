package deprecation

import (
	"fmt"
	"net/http"
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

// Один лічильник; різні маршрути — різні значення мітки route.
var deprCalls = prometheus.NewCounterVec(
	prometheus.CounterOpts{
		Name: "deprecated_route_calls_total",
		Help: "Виклики застарілих маршрутів за клієнтом",
	},
	[]string{"route", "client"},
)

func init() { prometheus.MustRegister(deprCalls) }

var knownClients = map[string]string{ // ключ API -> людська назва клієнта
	"ak_live_9f3…": "acme-mobile",
	"ak_live_2b7…": "partner-erp",
}

// Deprecated повертає обгортку хендлера. Дати розбираються й форматуються один
// раз, при конфігурації; panic при суперечливому контракті валить старт.
func Deprecated(route, announced, sunset, docs string) func(http.Handler) http.Handler {
	announcedAt, err := time.Parse("2006-01-02", announced)
	if err != nil {
		panic(fmt.Sprintf("deprecated(%s): announced %q: %v", route, announced, err))
	}
	sunsetAt, err := time.Parse("2006-01-02", sunset)
	if err != nil {
		panic(fmt.Sprintf("deprecated(%s): sunset %q: %v", route, sunset, err))
	}
	sunsetAt = sunsetAt.Add(24*time.Hour - time.Second) // кінець доби зняття

	// Контракт — до старту.
	if !sunsetAt.After(announcedAt) {
		panic(fmt.Sprintf("deprecated(%s): sunset %s не пізніше за announced %s",
			route, sunset, announced))
	}

	deprValue := fmt.Sprintf("@%d", announcedAt.Unix())   // Structured Field Date (RFC 9745)
	sunsetValue := sunsetAt.UTC().Format(http.TimeFormat) // HTTP-date, завжди GMT/англ. (RFC 8594)
	linkValue := fmt.Sprintf("<%s>; rel=\"deprecation\"; type=\"text/html\"", docs)

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			h := w.Header()
			h.Set("Deprecation", deprValue) // заголовки — ДО запису тіла
			h.Set("Sunset", sunsetValue)
			h.Set("Link", linkValue)
			deprCalls.WithLabelValues(route, clientID(r)).Inc()
			next.ServeHTTP(w, r)
		})
	}
}

func clientID(r *http.Request) string {
	if name, ok := knownClients[r.Header.Get("X-Api-Key")]; ok {
		return name
	}
	return "unknown"
}

// вмикається на ОДИН маршрут:
//   mux.Handle("/v1/orders",
//       Deprecated("orders.v1", "2024-06-30", "2025-12-31", docs)(listOrdersV1))
