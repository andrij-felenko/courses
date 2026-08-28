#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define MQTT_MAX_TOKENS      8
#define MQTT_MAX_ROUTES      16

typedef struct {
    const char *ptr;
    size_t      len;
} mqtt_token_t;

typedef struct {
    const char         *topic;
    size_t              topic_len;
    const uint8_t      *payload;
    size_t              payload_len;
    const mqtt_token_t *tokens;
    size_t              token_count;
} mqtt_message_t;

typedef void (*mqtt_handler_t)(const mqtt_message_t *msg, void *user_ctx);

typedef struct {
    const char     *pattern;
    mqtt_handler_t  handler;
    void           *user_ctx;
} mqtt_route_t;

typedef struct {
    mqtt_route_t routes[MQTT_MAX_ROUTES];
    size_t       count;
} mqtt_router_t;

/* Порівняння сегмента шаблону з сегментом теми */
static bool match_segment(const char *pat_seg, size_t pat_len,
                          const char *top_seg, size_t top_len) {
    if (pat_len == 1 && pat_seg[0] == '+') {
        return true;
    }
    if (pat_len != top_len) {
        return false;
    }
    return memcmp(pat_seg, top_seg, pat_len) == 0;
}

/* Перевірка збігу теми з шаблоном та витягнення токенів на місці */
bool mqtt_topic_matches(const char *pattern, const char *topic,
                        mqtt_token_t *tokens, size_t max_tokens,
                        size_t *out_token_count) {
    const char *p = pattern;
    const char *t = topic;
    size_t token_idx = 0;

    while (*p != '\0' && *t != '\0') {
        if (*p == '#') {
            /* '#' має бути останнім символом у шаблоні */
            if (*(p + 1) != '\0') {
                return false; /* Невалідний шаблон за специфікацією MQTT */
            }
            if (tokens && token_idx < max_tokens) {
                tokens[token_idx].ptr = t;
                tokens[token_idx].len = strlen(t);
                token_idx++;
            }
            if (out_token_count) *out_token_count = token_idx;
            return true;
        }

        /* Знаходимо межі поточного сегмента для шаблону */
        const char *p_slash = strchr(p, '/');
        size_t p_seg_len = p_slash ? (size_t)(p_slash - p) : strlen(p);

        /* Знаходимо межі поточного сегмента для теми */
        const char *t_slash = strchr(t, '/');
        size_t t_seg_len = t_slash ? (size_t)(t_slash - t) : strlen(t);

        if (!match_segment(p, p_seg_len, t, t_seg_len)) {
            return false;
        }

        /* Якщо в шаблоні стоїть '+', зберігаємо фактичний токен теми */
        if (p_seg_len == 1 && p[0] == '+' && tokens && token_idx < max_tokens) {
            tokens[token_idx].ptr = t;
            tokens[token_idx].len = t_seg_len;
            token_idx++;
        }

        p += p_seg_len;
        t += t_seg_len;

        if (*p == '/' && *t == '/') {
            p++;
            t++;
        } else if (*p != *t) {
            /* Дозволено, якщо шаблон завершився на '/#', а тема на слеші */
            if (*p == '/' && *(p + 1) == '#' && *t == '\0') {
                if (out_token_count) *out_token_count = token_idx;
                return true;
            }
            return false;
        }
    }

    /* Обробка кінцевого багаторівневого символу '/#' */
    if (*p == '/' && *(p + 1) == '#' && *(p + 2) == '\0' && *t == '\0') {
        if (out_token_count) *out_token_count = token_idx;
        return true;
    }

    if (*p == '\0' && *t == '\0') {
        if (out_token_count) *out_token_count = token_idx;
        return true;
    }

    return false;
}

void mqtt_router_init(mqtt_router_t *router) {
    if (!router) return;
    router->count = 0;
}

bool mqtt_router_add(mqtt_router_t *router, const char *pattern,
                     mqtt_handler_t handler, void *user_ctx) {
    if (!router || !pattern || !handler || router->count >= MQTT_MAX_ROUTES) {
        return false;
    }
    router->routes[router->count].pattern = pattern;
    router->routes[router->count].handler = handler;
    router->routes[router->count].user_ctx = user_ctx;
    router->count++;
    return true;
}

bool mqtt_router_dispatch(const mqtt_router_t *router,
                          const char *topic, size_t topic_len,
                          const uint8_t *payload, size_t payload_len) {
    if (!router || !topic) return false;

    /* Робота з нуль-термінованим рядком теми без динамічної пам'яті */
    char topic_buf[128];
    if (topic_len >= sizeof(topic_buf)) return false;
    memcpy(topic_buf, topic, topic_len);
    topic_buf[topic_len] = '\0';

    mqtt_token_t tokens[MQTT_MAX_TOKENS];
    size_t token_count = 0;

    for (size_t i = 0; i < router->count; i++) {
        if (mqtt_topic_matches(router->routes[i].pattern, topic_buf,
                               tokens, MQTT_MAX_TOKENS, &token_count)) {
            mqtt_message_t msg = {
                .topic = topic_buf,
                .topic_len = topic_len,
                .payload = payload,
                .payload_len = payload_len,
                .tokens = tokens,
                .token_count = token_count
            };
            router->routes[i].handler(&msg, router->routes[i].user_ctx);
            return true;
        }
    }
    return false;
}
