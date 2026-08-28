package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"sync"
	"time"
)

// Ланка в Go — функція, що бере наступний обробник і повертає новий.
type Middleware func(http.Handler) http.Handler

// Зчіплюємо РАЗ, на старті: кожна ланка загортає в себе весь залишок ланцюга.
func chain(h http.Handler, mw ...Middleware) http.Handler {
	for i := len(mw) - 1; i >= 0; i-- { // з кінця — щоб mw[0] опинився найзовнішнім
		h = mw[i](h)
	}
	return h
}

// ResponseWriter не каже, який статус уже пішов, — доводиться запам'ятати самим.
type recorder struct {
	http.ResponseWriter
	status int
}

func (rec *recorder) WriteHeader(code int) {
	rec.status = code
	rec.ResponseWriter.WriteHeader(code)
}

func Logger(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		t0 := time.Now()                                 // time.Now() у Go уже несе монотонну складову
		rec := &recorder{ResponseWriter: w, status: 200} // 200 — бо Write без WriteHeader дасть саме його
		defer func() {                                   // defer — те саме, що finally: спрацює й на паніці
			ms := float64(time.Since(t0).Microseconds()) / 1000
			log.Printf("%s %s → %d за %.1f мс", r.Method, r.URL.Path, rec.status, ms)
		}()
		next.ServeHTTP(rec, r)
	})
}

var (
	mu   sync.Mutex
	hits = map[string]int{} // стан ЛАНЦЮГА: усі запити торкаються його РАЗОМ → потрібен замок
)

func RateLimit(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		mu.Lock()
		hits[r.RemoteAddr]++
		n := hits[r.RemoteAddr]
		mu.Unlock()
		if n > 3 { // квоту списано ВЖЕ ТУТ, до будь-яких перевірок
			http.Error(w, "Забагато запитів", http.StatusTooManyRequests)
			return // коротке замикання: ServeHTTP наступного не кличемо
		}
		next.ServeHTTP(w, r)
	})
}

type ctxKey string

const userKey ctxKey = "user"

func Auth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "good-token" {
			http.Error(w, "Потрібен токен", http.StatusUnauthorized)
			return // коротке замикання
		}
		// стан ЗАПИТУ живе в контексті запиту, не в самій ланці
		next.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), userKey, "olena")))
	})
}

func profile(w http.ResponseWriter, r *http.Request) {
	user, _ := r.Context().Value(userKey).(string)
	fmt.Fprintf(w, "Привіт, %s", user)
}

func main() {
	log.SetFlags(0)
	log.SetOutput(os.Stdout)
	handle := chain(http.HandlerFunc(profile), Logger, RateLimit, Auth) // зібрали РАЗ

	for _, token := range []string{"good-token", "bad", "good-token", "good-token"} {
		req := httptest.NewRequest("GET", "/profile", nil)
		req.RemoteAddr = "10.0.0.7"
		req.Header.Set("Authorization", token)
		rr := httptest.NewRecorder()
		handle.ServeHTTP(rr, req)
		fmt.Printf("   відповідь: %d %s\n", rr.Code, strings.TrimSpace(rr.Body.String()))
	}
}
