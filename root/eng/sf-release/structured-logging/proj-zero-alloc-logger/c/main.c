#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#if defined(_WIN32)
  #include <windows.h>
  #include <io.h>
  #define WRITE_STDOUT(buf, len) _write(1, buf, (unsigned int)(len))
  #define THREAD_RET DWORD WINAPI
  #define THREAD_HANDLE HANDLE
  #define SLEEP_MS(ms) Sleep(ms)
#else
  #include <unistd.h>
  #include <pthread.h>
  #include <stdatomic.h>
  #define WRITE_STDOUT(buf, len) write(STDOUT_FILENO, buf, len)
  #define THREAD_RET void*
  #define THREAD_HANDLE pthread_t
  #define SLEEP_MS(ms) usleep((ms) * 1000)
#endif

#define MAX_MSG_SIZE 512
#define RING_SLOTS   4096
#define RING_MASK    (RING_SLOTS - 1)

typedef enum {
    LOG_DEBUG,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR
} LogLevel;

static const char* level_to_str(LogLevel lvl) {
    switch (lvl) {
        case LOG_DEBUG: return "DEBUG";
        case LOG_INFO:  return "INFO";
        case LOG_WARN:  return "WARN";
        case LOG_ERROR: return "ERROR";
        default:        return "UNKNOWN";
    }
}

typedef struct {
    uint16_t length;
    char data[MAX_MSG_SIZE];
} LogSlot;

typedef struct {
    char*  buf;
    size_t cap;
    size_t pos;
    bool   has_fields;
} FastJsonWriter;

static void json_init(FastJsonWriter* w, char* buf, size_t cap) {
    w->buf = buf;
    w->cap = cap;
    w->pos = 0;
    w->has_fields = false;
    if (cap > 0) {
        w->buf[0] = '{';
        w->pos = 1;
    }
}

static void json_append_char(FastJsonWriter* w, char c) {
    if (w->pos < w->cap) {
        w->buf[w->pos++] = c;
    }
}

static void json_append_bytes(FastJsonWriter* w, const char* src, size_len) {
    if (w->pos + src_len <= w->cap) {
        memcpy(w->buf + w->pos, src, src_len);
        w->pos += src_len;
    }
}

static void json_prepare_key(FastJsonWriter* w, const char* key, size_t klen) {
    if (w->has_fields) {
        json_append_char(w, ',');
    }
    w->has_fields = true;
    json_append_char(w, '"');
    json_append_bytes(w, key, klen);
    json_append_char(w, '"');
    json_append_char(w, ':');
}

static void json_add_string(FastJsonWriter* w, const char* key, const char* val) {
    size_t klen = strlen(key);
    json_prepare_key(w, key, klen);
    json_append_char(w, '"');
    for (size_t i = 0; val[i] != '\0'; ++i) {
        if (val[i] == '"' || val[i] == '\\') {
            json_append_char(w, '\\');
        }
        json_append_char(w, val[i]);
    }
    json_append_char(w, '"');
}

static void json_add_int(FastJsonWriter* w, const char* key, int64_t val) {
    size_t klen = strlen(key);
    json_prepare_key(w, key, klen);
    if (val < 0) {
        json_append_char(w, '-');
        val = -val;
    }
    char tmp[24];
    int tp = 0;
    uint64_t v = (uint64_t)val;
    if (v == 0) {
        json_append_char(w, '0');
        return;
    }
    while (v > 0) {
        tmp[tp++] = (char)('0' + (v % 10));
        v /= 10;
    }
    while (tp > 0) {
        json_append_char(w, tmp[--tp]);
    }
}

static size_t json_finish(FastJsonWriter* w) {
    if (w->pos + 2 <= w->cap) {
        w->buf[w->pos++] = '}';
        w->buf[w->pos++] = '\n';
    }
    return w->pos;
}

// Кільцевий буфер на C
typedef struct {
#if defined(_WIN32)
    volatile LONG head;
    volatile LONG tail;
    volatile LONG dropped;
#else
    atomic_size_t head;
    atomic_size_t tail;
    atomic_uint_fast64_t dropped;
#endif
    LogSlot slots[RING_SLOTS];
} CLogRing;

static void ring_init(CLogRing* r) {
    memset(r, 0, sizeof(*r));
}

static bool ring_try_push(CLogRing* r, const char* data, size_t len) {
    if (len > MAX_MSG_SIZE) return false;

#if defined(_WIN32)
    LONG head = InterlockedCompareExchange(&r->head, 0, 0);
    LONG tail = InterlockedCompareExchange(&r->tail, 0, 0);
    if ((head - tail) >= RING_SLOTS) {
        InterlockedIncrement(&r->dropped);
        return false;
    }
    size_t idx = (size_t)(head & RING_MASK);
    memcpy(r->slots[idx].data, data, len);
    r->slots[idx].length = (uint16_t)len;
    InterlockedIncrement(&r->head);
#else
    size_t head = atomic_load_explicit(&r->head, memory_order_relaxed);
    size_t tail = atomic_load_explicit(&r->tail, memory_order_acquire);
    if ((head - tail) >= RING_SLOTS) {
        atomic_fetch_add_explicit(&r->dropped, 1, memory_order_relaxed);
        return false;
    }
    size_t idx = head & RING_MASK;
    memcpy(r->slots[idx].data, data, len);
    r->slots[idx].length = (uint16_t)len;
    atomic_store_explicit(&r->head, head + 1, memory_order_release);
#endif
    return true;
}

static bool ring_try_pop(CLogRing* r, char* out_data, size_t* out_len) {
#if defined(_WIN32)
    LONG tail = InterlockedCompareExchange(&r->tail, 0, 0);
    LONG head = InterlockedCompareExchange(&r->head, 0, 0);
    if (tail == head) return false;
    size_t idx = (size_t)(tail & RING_MASK);
    *out_len = r->slots[idx].length;
    memcpy(out_data, r->slots[idx].data, *out_len);
    InterlockedIncrement(&r->tail);
#else
    size_t tail = atomic_load_explicit(&r->tail, memory_order_relaxed);
    size_t head = atomic_load_explicit(&r->head, memory_order_acquire);
    if (tail == head) return false;
    size_t idx = tail & RING_MASK;
    *out_len = r->slots[idx].length;
    memcpy(out_data, r->slots[idx].data, *out_len);
    atomic_store_explicit(&r->tail, tail + 1, memory_order_release);
#endif
    return true;
}

typedef struct {
    CLogRing ring;
    volatile bool running;
    THREAD_HANDLE thread;
} CAsyncLogger;

static THREAD_RET flush_worker(void* arg) {
    CAsyncLogger* logger = (CAsyncLogger*)arg;
    char batch_buf[MAX_MSG_SIZE * 32];
    size_t batch_len = 0;
    char item_buf[MAX_MSG_SIZE];
    size_t item_len = 0;

    while (logger->running) {
        bool found = false;
        while (ring_try_pop(&logger->ring, item_buf, &item_len)) {
            found = true;
            if (batch_len + item_len > sizeof(batch_buf)) {
                WRITE_STDOUT(batch_buf, batch_len);
                batch_len = 0;
            }
            memcpy(batch_buf + batch_len, item_buf, item_len);
            batch_len += item_len;
        }
        if (batch_len > 0) {
            WRITE_STDOUT(batch_buf, batch_len);
            batch_len = 0;
        }
        if (!found) {
            SLEEP_MS(5);
        }
    }
    return 0;
}

static void logger_init(CAsyncLogger* l) {
    ring_init(&l->ring);
    l->running = true;
#if defined(_WIN32)
    l->thread = CreateThread(NULL, 0, flush_worker, l, 0, NULL);
#else
    pthread_create(&l->thread, NULL, flush_worker, l);
#endif
}

static void logger_log(CAsyncLogger* l, LogLevel lvl, const char* msg, int64_t user_id, int64_t dur) {
    char buf[MAX_MSG_SIZE];
    FastJsonWriter w;
    json_init(&w, buf, sizeof(buf));
    json_add_string(&w, "level", level_to_str(lvl));
    json_add_string(&w, "msg", msg);
    json_add_int(&w, "user_id", user_id);
    json_add_int(&w, "duration_ms", dur);
    size_t len = json_finish(&w);
    ring_try_push(&l->ring, buf, len);
}

int main(void) {
    CAsyncLogger logger;
    logger_init(&logger);
    logger_log(&logger, LOG_INFO, "order_created", 84920, 14);
    logger_log(&logger, LOG_ERROR, "payment_timeout", 84920, 3004);

    SLEEP_MS(20);
    logger.running = false;
#if defined(_WIN32)
    WaitForSingleObject(logger.thread, INFINITE);
    CloseHandle(logger.thread);
#else
    pthread_join(logger.thread, NULL);
#endif
    return 0;
}
