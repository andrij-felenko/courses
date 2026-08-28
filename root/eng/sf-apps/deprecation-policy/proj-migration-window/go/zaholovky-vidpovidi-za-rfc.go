package migration

import (
	"fmt"
	"net/http"
	"strconv"
	"time"
)

// httpDate форматує HTTP-дату (для Sunset): "Sun, 30 Jun 2024 23:59:59 GMT".
// http.TimeFormat — це рівно RFC 1123 у GMT, стандартна форма для заголовків.
func httpDate(t time.Time) string {
	return t.UTC().Format(http.TimeFormat)
}

// markDeprecated ставить усі три заголовки застарілості узгоджено.
// deprecatedSince / sunsetAt — момент застарівання й вимкнення.
func markDeprecated(h http.Header,
	deprecatedSince, sunsetAt time.Time,
	successorURI, docsURI string) {

	// ЗАЛІЗНЕ правило RFC 9745: sunset не раніший за deprecation.
	// Ловимо помилку тут, а не в проді у вигляді дивних відповідей.
	if sunsetAt.Before(deprecatedSince) {
		sunsetAt = deprecatedSince // або повернути помилку — на смак команди
	}

	// RFC 9745: значення — структуроване поле-дата, Unix-час із префіксом '@'.
	// НЕ "true" (то була рання чернетка).
	h.Set("Deprecation", "@"+strconv.FormatInt(deprecatedSince.Unix(), 10))

	// RFC 8594: HTTP-дата.
	h.Set("Sunset", httpDate(sunsetAt))

	// Куди переходити (successor-version) + людські доки (deprecation).
	h.Set("Link", fmt.Sprintf(
		`<%s>; rel="successor-version", <%s>; rel="deprecation"`,
		successorURI, docsURI))
}
