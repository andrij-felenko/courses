#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

/* Зріз рядка без копіювання пам'яті */
typedef struct {
    const char *ptr;
    size_t len;
} url_view_t;

typedef struct {
    url_view_t scheme;
    url_view_t userinfo;
    url_view_t host;
    int port;
    url_view_t path;
    url_view_t query;
    url_view_t fragment;
} parsed_url_t;

/* Друк зрізу рядка у стандартний вивід */
void print_view(const char *label, url_view_t v) {
    printf("%-10s: %.*s\n", label, (int)v.len, v.ptr ? v.ptr : "");
}

/* Розбір URL на компоненти за RFC 3986 */
bool parse_url(const char *raw, size_t len, parsed_url_t *out) {
    if (!raw || !out) return false;
    memset(out, 0, sizeof(*out));

    const char *cur = raw;
    const char *end = raw + len;

    /* 1. Пошук схеми: починається з букви, завершується ':' */
    const char *colon = memchr(cur, ':', end - cur);
    if (colon && colon != cur) {
        /* Перевіряємо, чи немає перед ':' символів '/', '?', '#' */
        const char *p = cur;
        bool valid_scheme = isalpha((unsigned char)*p);
        p++;
        while (p < colon && valid_scheme) {
            char c = *p++;
            if (!isalnum((unsigned char)c) && c != '+' && c != '-' && c != '.') {
                valid_scheme = false;
            }
        }
        if (valid_scheme) {
            out->scheme.ptr = cur;
            out->scheme.len = colon - cur;
            cur = colon + 1;
        }
    }

    /* 2. Пошук Authority: починається з "//" */
    if (cur + 1 < end && cur[0] == '/' && cur[1] == '/') {
        cur += 2;
        const char *auth_start = cur;
        const char *auth_end = cur;
        while (auth_end < end && *auth_end != '/' && *auth_end != '?' && *auth_end != '#') {
            auth_end++;
        }

        /* Пошук userinfo за '@' */
        const char *at = memchr(auth_start, '@', auth_end - auth_start);
        const char *host_start = auth_start;
        if (at) {
            out->userinfo.ptr = auth_start;
            out->userinfo.len = at - auth_start;
            host_start = at + 1;
        }

        /* Пошук host і port (враховуючи IPv6 [::1]) */
        const char *host_end = auth_end;
        if (host_start < auth_end && *host_start == '[') {
            /* IPv6 адреса */
            const char *bracket_close = memchr(host_start, ']', auth_end - host_start);
            if (bracket_close) {
                host_end = bracket_close + 1;
                out->host.ptr = host_start;
                out->host.len = host_end - host_start;
                if (host_end < auth_end && *host_end == ':') {
                    out->port = atoi(host_end + 1);
                }
            } else {
                return false; /* Некоректний IPv6 */
            }
        } else {
            /* Звичайний хост (DNS або IPv4) */
            const char *port_colon = memchr(host_start, ':', auth_end - host_start);
            if (port_colon) {
                out->host.ptr = host_start;
                out->host.len = port_colon - host_start;
                out->port = atoi(port_colon + 1);
            } else {
                out->host.ptr = host_start;
                out->host.len = auth_end - host_start;
            }
        }
        cur = auth_end;
    }

    /* 3. Пошук Path (до '?' або '#') */
    const char *path_start = cur;
    while (cur < end && *cur != '?' && *cur != '#') {
        cur++;
    }
    out->path.ptr = path_start;
    out->path.len = cur - path_start;

    /* 4. Пошук Query (після '?') */
    if (cur < end && *cur == '?') {
        cur++;
        const char *query_start = cur;
        while (cur < end && *cur != '#') {
            cur++;
        }
        out->query.ptr = query_start;
        out->query.len = cur - query_start;
    }

    /* 5. Пошук Fragment (після '#') */
    if (cur < end && *cur == '#') {
        cur++;
        out->fragment.ptr = cur;
        out->fragment.len = end - cur;
    }

    return true;
}
