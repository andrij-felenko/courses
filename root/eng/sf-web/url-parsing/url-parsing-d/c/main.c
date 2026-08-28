#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    const char *scheme;
    size_t      scheme_len;
    const char *host;
    size_t      host_len;
    int         port;
    const char *path;
    size_t      path_len;
    const char *query;
    size_t      query_len;
} url_parts_t;

/* Простий нуль-алокаційний виділювач компонентів */
bool parse_http_url(const char *url, url_parts_t *parts) {
    memset(parts, 0, sizeof(*parts));
    const char *p = url;

    /* Схема */
    const char *scheme_end = strstr(p, "://");
    if (!scheme_end) return false;
    parts->scheme = p;
    parts->scheme_len = scheme_end - p;
    p = scheme_end + 3;

    /* Хост і порт */
    const char *host_start = p;
    while (*p && *p != '/' && *p != '?' && *p != '#' && *p != ':') {
        p++;
    }
    parts->host = host_start;
    parts->host_len = p - host_start;

    if (*p == ':') {
        p++;
        parts->port = 0;
        while (*p >= '0' && *p <= '9') {
            parts->port = parts->port * 10 + (*p - '0');
            p++;
        }
    } else {
        parts->port = (parts->scheme_len == 5 && memcmp(parts->scheme, "https", 5) == 0) ? 443 : 80;
    }

    /* Шлях */
    if (*p == '/') {
        const char *path_start = p;
        while (*p && *p != '?' && *p != '#') p++;
        parts->path = path_start;
        parts->path_len = p - path_start;
    } else {
        parts->path = "/";
        parts->path_len = 1;
    }

    /* Запит */
    if (*p == '?') {
        p++;
        const char *q_start = p;
        while (*p && *p != '#') p++;
        parts->query = q_start;
        parts->query_len = p - q_start;
    }

    return true;
}
