package cors

import (
	"net/http"
	"regexp"
	"strconv"
	"strings"
)

type Config struct {
	AllowedOrigins        []string
	AllowedOriginPatterns []*regexp.Regexp
	AllowedMethods        []string
	AllowedHeaders        []string
	ExposedHeaders        []string
	AllowCredentials      bool
	MaxAgeSeconds         int
}

func DefaultConfig(allowedOrigins []string) Config {
	return Config{
		AllowedOrigins:   allowedOrigins,
		AllowedMethods:   []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type", "Authorization", "X-Requested-With", "X-Request-Id"},
		ExposedHeaders:   []string{"X-Total-Count", "X-RateLimit-Remaining"},
		AllowCredentials: true,
		MaxAgeSeconds:    86400,
	}
}

func Middleware(cfg Config) func(http.Handler) http.Handler {
	originMap := make(map[string]struct{}, len(cfg.AllowedOrigins))
	for _, o := range cfg.AllowedOrigins {
		originMap[o] = struct{}{}
	}

	methodsHeader := strings.Join(cfg.AllowedMethods, ", ")
	allowedHeadersStr := strings.Join(cfg.AllowedHeaders, ", ")
	exposedHeadersStr := strings.Join(cfg.ExposedHeaders, ", ")
	maxAgeStr := strconv.Itoa(cfg.MaxAgeSeconds)

	isAllowed := func(origin string) bool {
		if _, ok := originMap[origin]; ok {
			return true
		}
		for _, re := range cfg.AllowedOriginPatterns {
			if re.MatchString(origin) {
				return true
			}
		}
		return false
	}

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			origin := r.Header.Get("Origin")
			if origin == "" {
				next.ServeHTTP(w, r)
				return
			}

			if isAllowed(origin) {
				h := w.Header()
				h.Set("Access-Control-Allow-Origin", origin)
				h.Add("Vary", "Origin")

				if cfg.AllowCredentials {
					h.Set("Access-Control-Allow-Credentials", "true")
				}

				if len(cfg.ExposedHeaders) > 0 {
					h.Set("Access-Control-Expose-Headers", exposedHeadersStr)
				}

				if r.Method == http.MethodOptions {
					h.Set("Access-Control-Allow-Methods", methodsHeader)
					h.Set("Access-Control-Allow-Headers", allowedHeadersStr)
					h.Set("Access-Control-Max-Age", maxAgeStr)
					h.Set("Content-Length", "0")
					w.WriteHeader(http.StatusNoContent)
					return
				}
			} else if r.Method == http.MethodOptions {
				w.WriteHeader(http.StatusForbidden)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}
