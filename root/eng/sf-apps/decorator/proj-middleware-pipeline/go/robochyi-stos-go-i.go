package main

import (
	"log"
	"net/http"
	"time"
)

// Обробник — це http.Handler (єдиний метод ServeHTTP(w, r)).
// Middleware — обгортка: бере наступний обробник, вертає новий.
type Middleware func(http.Handler) http.Handler

// Logger: «до» — пишемо вхід; делегуємо; «після» — пишемо вихід.
func Logger(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("→ %s %s", r.Method, r.URL.Path) // ДО делегації
		next.ServeHTTP(w, r)                         // делегація глибше
		log.Printf("← %s", r.URL.Path)               // ПІСЛЯ делегації
	})
}

// Timer: «до» — засікли старт; делегуємо; «після» — зміряли тривалість.
func Timer(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("⏱ %s за %s", r.URL.Path, time.Since(start))
	})
}
