#include <ctime>

struct Response {                              // спрощений вигляд відповіді
    int status = 200;
    std::string body;
    void set_header(const std::string& k, const std::string& v);
    // …
};

// Форматуємо HTTP-дату (для Sunset): "Sun, 30 Jun 2024 23:59:59 GMT".
static std::string http_date(std::time_t t) {
    char buf[40];
    std::tm gmt{};
#if defined(_WIN32)
    gmtime_s(&gmt, &t);
#else
    gmtime_r(&t, &gmt);
#endif
    std::strftime(buf, sizeof buf, "%a, %d %b %Y %H:%M:%S GMT", &gmt);
    return buf;
}

// Ставимо всі три заголовки застарілості узгоджено.
// deprecated_since / sunset_at — Unix-час (секунди епохи).
static void mark_deprecated(Response& res,
                            std::time_t deprecated_since,
                            std::time_t sunset_at,
                            const std::string& successor_uri,
                            const std::string& docs_uri) {
    // ЗАЛІЗНЕ правило RFC 9745: sunset не раніший за deprecation.
    // Ловимо помилку тут, а не в проді у вигляді дивних відповідей.
    if (sunset_at < deprecated_since)
        sunset_at = deprecated_since;          // або кинути виняток — на смак команди

    // RFC 9745: значення — структуроване поле-дата, Unix-час із префіксом '@'.
    // НЕ "true" (то була рання чернетка).
    res.set_header("Deprecation", "@" + std::to_string(deprecated_since));

    // RFC 8594: HTTP-дата.
    res.set_header("Sunset", http_date(sunset_at));

    // Куди переходити (successor-version) + людські доки (deprecation).
    res.set_header("Link",
        "<" + successor_uri + ">; rel=\"successor-version\", "
        "<" + docs_uri     + ">; rel=\"deprecation\"");
}
