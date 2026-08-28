#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>
#include <time.h>

#define MAX_ENDPOINTS 16
#define CONNECTION_ATTEMPT_DELAY_MS 250
#define TOTAL_TIMEOUT_MS 10000

typedef struct {
    struct sockaddr_storage addr;
    socklen_t addr_len;
    int family; /* AF_INET або AF_INET6 */
} Endpoint;

typedef struct {
    int fd;
    size_t endpoint_idx;
    int is_active;
    int is_connected;
} ConnectionAttempt;

typedef struct {
    Endpoint endpoints[MAX_ENDPOINTS];
    size_t endpoint_count;
    size_t next_endpoint_to_try;
    ConnectionAttempt attempts[MAX_ENDPOINTS];
    size_t active_attempts_count;
    int winner_fd;
} HappyEyeballsEngine;

static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

static long long current_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000LL + (ts.tv_nsec / 1000000LL);
}

/* Формування черги адрес зі строгим чергуванням родин IPv6 та IPv4 */
static size_t interleave_endpoints(const Endpoint* v6, size_t v6_cnt,
                                   const Endpoint* v4, size_t v4_cnt,
                                   Endpoint* out) {
    size_t i = 0, j = 0, k = 0;
    while (i < v6_cnt || j < v4_cnt) {
        if (i < v6_cnt && k < MAX_ENDPOINTS) {
            out[k++] = v6[i++];
        }
        if (j < v4_cnt && k < MAX_ENDPOINTS) {
            out[k++] = v4[j++];
        }
    }
    return k;
}

/* Ініціалізація спроби асинхронного підключення */
static int start_connection_attempt(HappyEyeballsEngine* engine) {
    if (engine->next_endpoint_to_try >= engine->endpoint_count) {
        return 0; /* Немає більше адрес для спроб */
    }

    size_t ep_idx = engine->next_endpoint_to_try++;
    Endpoint* ep = &engine->endpoints[ep_idx];

    int fd = socket(ep->family, SOCK_STREAM, 0);
    if (fd < 0) {
        return -1;
    }

    if (set_nonblocking(fd) < 0) {
        close(fd);
        return -1;
    }

    int rc = connect(fd, (struct sockaddr*)&ep->addr, ep->addr_len);
    if (rc == 0) {
        /* З'єднання відбулося миттєво (наприклад, loopback) */
        ConnectionAttempt* att = &engine->attempts[engine->active_attempts_count++];
        att->fd = fd;
        att->endpoint_idx = ep_idx;
        att->is_active = 1;
        att->is_connected = 1;
        engine->winner_fd = fd;
        return 1;
    }

    if (rc < 0 && errno == EINPROGRESS) {
        /* Нормальний асинхронний старт тристороннього рукостискання */
        ConnectionAttempt* att = &engine->attempts[engine->active_attempts_count++];
        att->fd = fd;
        att->endpoint_idx = ep_idx;
        att->is_active = 1;
        att->is_connected = 0;
        return 1;
    }

    /* Миттєва помилка (наприклад, ENETUNREACH) — закриваємо сокет */
    close(fd);
    return 0;
}

/* Скасування та закриття всіх невдалих або повільних спроб */
static void cleanup_losing_attempts(HappyEyeballsEngine* engine, int winning_fd) {
    for (size_t i = 0; i < engine->active_attempts_count; ++i) {
        ConnectionAttempt* att = &engine->attempts[i];
        if (att->is_active && att->fd != winning_fd) {
            close(att->fd);
            att->is_active = 0;
            att->fd = -1;
        }
    }
}

/* Головний цикл змагання з'єднань Happy Eyeballs v2 */
int happy_eyeballs_connect(const Endpoint* interleaved_endpoints, size_t count) {
    if (count == 0) return -1;

    HappyEyeballsEngine engine;
    memset(&engine, 0, sizeof(engine));
    memcpy(engine.endpoints, interleaved_endpoints, count * sizeof(Endpoint));
    engine.endpoint_count = count;
    engine.winner_fd = -1;

    long long start_time = current_time_ms();
    long long next_attempt_time = start_time;

    while (engine.winner_fd == -1) {
        long long now = current_time_ms();
        if (now - start_time >= TOTAL_TIMEOUT_MS) {
            cleanup_losing_attempts(&engine, -1);
            return -1; /* Загальний таймаут вичерпано */
        }

        /* Час для запуску наступної паралельної спроби */
        if (now >= next_attempt_time && engine.next_endpoint_to_try < engine.endpoint_count) {
            int res = start_connection_attempt(&engine);
            if (engine.winner_fd != -1) {
                break; /* Миттєве підключення */
            }
            if (res > 0) {
                next_attempt_time = now + CONNECTION_ATTEMPT_DELAY_MS;
            } else {
                /* Якщо спроба зазнала швидкої помилки, пробуємо наступну негайно */
                next_attempt_time = now;
                continue;
            }
        }

        /* Формування списку опитування дескрипторів для poll */
        struct pollfd pfd[MAX_ENDPOINTS];
        int pfd_map[MAX_ENDPOINTS];
        nfds_t nfds = 0;

        for (size_t i = 0; i < engine.active_attempts_count; ++i) {
            if (engine.attempts[i].is_active && !engine.attempts[i].is_connected) {
                pfd[nfds].fd = engine.attempts[i].fd;
                pfd[nfds].events = POLLOUT;
                pfd[nfds].revents = 0;
                pfd_map[nfds] = (int)i;
                nfds++;
            }
        }

        if (nfds == 0 && engine.next_endpoint_to_try >= engine.endpoint_count) {
            /* Усі адреси вичерпані й жоден сокет не активний */
            return -1;
        }

        int poll_timeout = 10; /* мс */
        if (engine.next_endpoint_to_try < engine.endpoint_count) {
            long long time_to_next = next_attempt_time - now;
            if (time_to_next < 0) time_to_next = 0;
            if (time_to_next < poll_timeout) poll_timeout = (int)time_to_next;
        }

        int prc = poll(pfd, nfds, poll_timeout);
        if (prc > 0) {
            for (nfds_t i = 0; i < nfds; ++i) {
                if (pfd[i].revents & (POLLOUT | POLLERR | POLLHUP)) {
                    int att_idx = pfd_map[i];
                    int fd = engine.attempts[att_idx].fd;
                    int sock_err = 0;
                    socklen_t err_len = sizeof(sock_err);

                    if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &sock_err, &err_len) == 0 && sock_err == 0) {
                        /* Переможець знайдений! */
                        engine.winner_fd = fd;
                        engine.attempts[att_idx].is_connected = 1;
                        break;
                    } else {
                        /* Помилка з'єднання на цьому дескрипторі */
                        close(fd);
                        engine.attempts[att_idx].is_active = 0;
                        engine.attempts[att_idx].fd = -1;
                    }
                }
            }
        }
    }

    int winner = engine.winner_fd;
    cleanup_losing_attempts(&engine, winner);
    return winner;
}
