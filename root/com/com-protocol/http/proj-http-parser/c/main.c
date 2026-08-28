#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <ctype.h>

typedef enum {
    HTTP_METHOD_GET,
    HTTP_METHOD_POST,
    HTTP_METHOD_PUT,
    HTTP_METHOD_DELETE,
    HTTP_METHOD_HEAD,
    HTTP_METHOD_OPTIONS,
    HTTP_METHOD_PATCH,
    HTTP_METHOD_UNKNOWN
} http_method_t;

typedef enum {
    PARSE_NEED_MORE_DATA,
    PARSE_COMPLETE,
    PARSE_ERROR_INVALID_METHOD,
    PARSE_ERROR_INVALID_URI,
    PARSE_ERROR_INVALID_VERSION,
    PARSE_ERROR_INVALID_HEADER,
    PARSE_ERROR_SMUGGLING_CONFLICT
} parse_res_t;

typedef struct {
    const char *name;
    size_t name_len;
    const char *value;
    size_t value_len;
} http_header_c_t;

typedef struct {
    http_method_t method;
    const char *uri;
    size_t uri_len;
    int version_major;
    int version_minor;
    http_header_c_t headers[32];
    size_t num_headers;
    const char *body;
    size_t body_len;
    bool is_chunked;
    size_t content_length;
} http_request_c_t;

static bool str_equals_icase(const char *s, size_t len, const char *target) {
    if (len != strlen(target)) return false;
    for (size_t i = 0; i < len; ++i) {
        if (tolower((unsigned char)s[i]) != tolower((unsigned char)target[i])) {
            return false;
        }
    }
    return true;
}

parse_res_t parse_http_request_c(const char *buf, size_t len, http_request_c_t *req) {
    memset(req, 0, sizeof(*req));
    const char *cur = buf;
    const char *end = buf + len;

    // 1. Парсинг методу
    const char *space1 = memchr(cur, ' ', end - cur);
    if (!space1) return PARSE_NEED_MORE_DATA;
    size_t mlen = space1 - cur;
    if (mlen == 3 && memcmp(cur, "GET", 3) == 0) req->method = HTTP_METHOD_GET;
    else if (mlen == 4 && memcmp(cur, "POST", 4) == 0) req->method = HTTP_METHOD_POST;
    else if (mlen == 3 && memcmp(cur, "PUT", 3) == 0) req->method = HTTP_METHOD_PUT;
    else if (mlen == 6 && memcmp(cur, "DELETE", 6) == 0) req->method = HTTP_METHOD_DELETE;
    else return PARSE_ERROR_INVALID_METHOD;

    cur = space1 + 1;

    // 2. Парсинг URI
    const char *space2 = memchr(cur, ' ', end - cur);
    if (!space2) return PARSE_NEED_MORE_DATA;
    req->uri = cur;
    req->uri_len = space2 - cur;
    if (req->uri_len == 0 || req->uri[0] != '/') return PARSE_ERROR_INVALID_URI;

    cur = space2 + 1;

    // 3. Версія HTTP
    const char *crlf1 = strstr(cur, "\r\n");
    if (!crlf1 || crlf1 >= end) return PARSE_NEED_MORE_DATA;
    if (crlf1 - cur == 8 && memcmp(cur, "HTTP/1.1", 8) == 0) {
        req->version_major = 1; req->version_minor = 1;
    } else {
        return PARSE_ERROR_INVALID_VERSION;
    }
    cur = crlf1 + 2;

    // 4. Заголовки
    bool has_cl = false, has_te = false;
    while (cur < end) {
        if (cur + 2 <= end && memcmp(cur, "\r\n", 2) == 0) {
            cur += 2;
            break; // Кінець блоку заголовків
        }
        const char *colon = memchr(cur, ':', end - cur);
        const char *line_end = strstr(cur, "\r\n");
        if (!line_end || line_end >= end) return PARSE_NEED_MORE_DATA;
        if (!colon || colon > line_end) return PARSE_ERROR_INVALID_HEADER;

        // Заборона пробілів перед двокрапкою
        if (colon > cur && (*(colon - 1) == ' ' || *(colon - 1) == '\t')) {
            return PARSE_ERROR_INVALID_HEADER;
        }

        if (req->num_headers < 32) {
            http_header_c_t *h = &req->headers[req->num_headers++];
            h->name = cur;
            h->name_len = colon - cur;
            
            const char *val_start = colon + 1;
            while (val_start < line_end && (*val_start == ' ' || *val_start == '\t')) val_start++;
            const char *val_end = line_end;
            while (val_end > val_start && (*(val_end - 1) == ' ' || *(val_end - 1) == '\t')) val_end--;
            
            h->value = val_start;
            h->value_len = val_end - val_start;

            if (str_equals_icase(h->name, h->name_len, "Content-Length")) {
                has_cl = true;
                req->content_length = (size_t)strtoul(h->value, NULL, 10);
            } else if (str_equals_icase(h->name, h->name_len, "Transfer-Encoding")) {
                has_te = true;
                if (strstr(h->value, "chunked")) req->is_chunked = true;
            }
        }
        cur = line_end + 2;
    }

    // Захист від Request Smuggling (RFC 9112)
    if (has_cl && has_te) return PARSE_ERROR_SMUGGLING_CONFLICT;

    // 5. Тіло
    if (req->content_length > 0) {
        if ((size_t)(end - cur) < req->content_length) return PARSE_NEED_MORE_DATA;
        req->body = cur;
        req->body_len = req->content_length;
    }

    return PARSE_COMPLETE;
}
