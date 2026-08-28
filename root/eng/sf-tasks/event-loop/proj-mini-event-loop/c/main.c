#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <time.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define MAX_EVENTS 64

typedef void (*event_cb)(int fd, uint32_t events, void *user_data);
typedef void (*timer_cb)(void *user_data);

typedef struct {
    uint64_t deadline_ms;
    timer_cb callback;
    void *user_data;
    uint64_t timer_id;
} timer_entry_t;

typedef struct {
    int epoll_fd;
    bool running;
    timer_entry_t *timers;
    size_t timer_count;
    size_t timer_capacity;
    uint64_t next_timer_id;
} event_loop_t;

static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000 + (uint64_t)ts.tv_nsec / 1000000;
}

static void heap_swap(timer_entry_t *a, timer_entry_t *b) {
    timer_entry_t tmp = *a;
    *a = *b;
    *b = tmp;
}

static void heap_sift_up(event_loop_t *loop, size_t idx) {
    while (idx > 0) {
        size_t parent = (idx - 1) / 2;
        if (loop->timers[idx].deadline_ms < loop->timers[parent].deadline_ms) {
            heap_swap(&loop->timers[idx], &loop->timers[parent]);
            idx = parent;
        } else {
            break;
        }
    }
}

static void heap_sift_down(event_loop_t *loop, size_t idx) {
    while (2 * idx + 1 < loop->timer_count) {
        size_t left = 2 * idx + 1;
        size_t right = 2 * idx + 2;
        size_t smallest = idx;

        if (loop->timers[left].deadline_ms < loop->timers[smallest].deadline_ms) {
            smallest = left;
        }
        if (right < loop->timer_count && loop->timers[right].deadline_ms < loop->timers[smallest].deadline_ms) {
            smallest = right;
        }
        if (smallest != idx) {
            heap_swap(&loop->timers[idx], &loop->timers[smallest]);
            idx = smallest;
        } else {
            break;
        }
    }
}

event_loop_t* loop_create(void) {
    event_loop_t *loop = calloc(1, sizeof(event_loop_t));
    if (!loop) return NULL;

    loop->epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (loop->epoll_fd < 0) {
        free(loop);
        return NULL;
    }
    loop->running = false;
    loop->timer_capacity = 16;
    loop->timers = malloc(loop->timer_capacity * sizeof(timer_entry_t));
    return loop;
}

void loop_destroy(event_loop_t *loop) {
    if (!loop) return;
    if (loop->epoll_fd >= 0) close(loop->epoll_fd);
    free(loop->timers);
    free(loop);
}

int loop_add_fd(event_loop_t *loop, int fd, uint32_t events, event_cb cb, void *user_data) {
    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.events = events;
    void **binding = malloc(2 * sizeof(void*));
    binding[0] = (void*)cb;
    binding[1] = user_data;
    ev.data.ptr = binding;

    return epoll_ctl(loop->epoll_fd, EPOLL_CTL_ADD, fd, &ev);
}

uint64_t loop_add_timer(event_loop_t *loop, uint64_t delay_ms, timer_cb cb, void *user_data) {
    if (loop->timer_count == loop->timer_capacity) {
        loop->timer_capacity *= 2;
        loop->timers = realloc(loop->timers, loop->timer_capacity * sizeof(timer_entry_t));
    }
    size_t idx = loop->timer_count++;
    uint64_t id = ++loop->next_timer_id;
    loop->timers[idx] = (timer_entry_t){
        .deadline_ms = get_monotonic_ms() + delay_ms,
        .callback = cb,
        .user_data = user_data,
        .timer_id = id
    };
    heap_sift_up(loop, idx);
    return id;
}

void loop_run(event_loop_t *loop) {
    struct epoll_event events[MAX_EVENTS];
    loop->running = true;

    while (loop->running) {
        uint64_t now = get_monotonic_ms();

        // 1. Обчислюємо таймаут для epoll_wait
        int timeout_ms = -1;
        if (loop->timer_count > 0) {
            if (loop->timers[0].deadline_ms <= now) {
                timeout_ms = 0; // Вже збіг — негайний вихід
            } else {
                timeout_ms = (int)(loop->timers[0].deadline_ms - now);
            }
        }

        // 2. Спимо у демультиплексорі ядра
        int nfds = epoll_wait(loop->epoll_fd, events, MAX_EVENTS, timeout_ms);
        if (nfds < 0 && errno != EINTR) {
            break;
        }

        // 3. Обробляємо готові сокетні події
        for (int i = 0; i < nfds; ++i) {
            void **binding = (void**)events[i].data.ptr;
            event_cb cb = (event_cb)binding[0];
            void *ud = binding[1];
            if (cb) {
                cb(0, events[i].events, ud);
            }
        }

        // 4. Обробляємо всі таймери, що збігли на поточний момент
        now = get_monotonic_ms();
        while (loop->timer_count > 0 && loop->timers[0].deadline_ms <= now) {
            timer_entry_t expired = loop->timers[0];
            loop->timers[0] = loop->timers[--loop->timer_count];
            if (loop->timer_count > 0) {
                heap_sift_down(loop, 0);
            }
            if (expired.callback) {
                expired.callback(expired.user_data);
            }
        }
    }
}
