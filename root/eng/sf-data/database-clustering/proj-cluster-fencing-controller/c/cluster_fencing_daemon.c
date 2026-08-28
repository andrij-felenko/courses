/* ============================================================================
 * cluster_fencing_daemon.c — C-реалізація контролера огородження та лізи
 * ============================================================================ */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <time.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/ioctl.h>
#include <linux/watchdog.h>

#define LOOP_WAIT_MS       2000   /* Інтервал циклу опитування (2 сек) */
#define RETRY_TIMEOUT_MS   4000   /* Таймаут зв'язку з координатором (4 сек) */
#define SAFETY_MARGIN_MS   5000   /* Запас безпеки до примусового огородження (5 сек) */
#define LEASE_TTL_MS       10000  /* Повний час життя лізи в DCS (10 сек) */
#define WATCHDOG_DEV       "/dev/watchdog"

typedef enum {
    NODE_STATE_FOLLOWER,
    NODE_STATE_LEADER_ACTIVE,
    NODE_STATE_LEASE_DEGRADED,
    NODE_STATE_FENCED
} node_state_t;

typedef struct {
    int watchdog_fd;
    int db_sock_fd;
    node_state_t state;
    uint64_t lease_acquired_at_ms;
    uint64_t last_successful_heartbeat_ms;
    bool is_leader;
} cluster_controller_t;

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

/* Отримання поточного монотонного часу в мілісекундах */
static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)(ts.tv_nsec / 1000000ULL);
}

/* Ініціалізація апаратного сторожового таймера Linux */
static int init_watchdog(void) {
    int fd = open(WATCHDOG_DEV, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "[WARN] Не вдалося відкрити %s: %s (працюємо в емуляції)\n",
                WATCHDOG_DEV, strerror(errno));
        return -1;
    }
    int timeout_sec = (LOOP_WAIT_MS + SAFETY_MARGIN_MS) / 1000;
    if (ioctl(fd, WDIOC_SETTIMEOUT, &timeout_sec) < 0) {
        fprintf(stderr, "[WARN] Не вдалося встановити таймаут watchdog: %s\n", strerror(errno));
    } else {
        printf("[INFO] Апаратний Watchdog активовано. Таймаут: %d сек\n", timeout_sec);
    }
    return fd;
}

/* Скидання апаратного сторожового таймера */
static void ping_watchdog(int fd) {
    if (fd >= 0) {
        int dummy = 0;
        if (ioctl(fd, WDIOC_KEEPALIVE, &dummy) < 0) {
            fprintf(stderr, "[ERR] Збій оновлення Watchdog: %s\n", strerror(errno));
        }
    }
}

/* Безпечне вимкнення Watchdog за допомогою 'магічного символу' 'V' */
static void disable_watchdog(int fd) {
    if (fd >= 0) {
        write(fd, "V", 1);
        close(fd);
        printf("[INFO] Watchdog коректно деактивовано.\n");
    }
}

/* Перевірка працездатності локальної СУБД через сокет */
static bool probe_local_db_health(const char *socket_path) {
    int sock = socket(AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK, 0);
    if (sock < 0) return false;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);

    int res = connect(sock, (struct sockaddr *)&addr, sizeof(addr));
    if (res < 0 && errno != EINPROGRESS) {
        close(sock);
        return false;
    }

    struct pollfd pfd = { .fd = sock, .events = POLLOUT, .revents = 0 };
    int poll_res = poll(&pfd, 1, 300); /* 300 мс таймаут на підключення */
    if (poll_res <= 0 || (pfd.revents & (POLLERR | POLLHUP))) {
        close(sock);
        return false;
    }

    int so_error = 0;
    socklen_t len = sizeof(so_error);
    getsockopt(sock, SOL_SOCKET, SO_ERROR, &so_error, &len);
    close(sock);
    return (so_error == 0);
}

/* Імітація продовження оренди лізи в розподіленому координаторі DCS (etcd) */
static bool renew_dcs_lease(bool simulate_network_drop) {
    if (simulate_network_drop) {
        return false;
    }
    /* У реальній системі: транзакція CAS в etcd v3 gRPC/HTTP API */
    return true;
}

/* Примусове огородження локального вузла (Emergency Fencing) */
static void execute_emergency_fencing(cluster_controller_t *ctrl) {
    printf("[CRITICAL] ОГОРОДЖЕННЯ! Ліза втрачена. Виконується екстрена ізоляція вузла!\n");
    ctrl->state = NODE_STATE_FENCED;
    ctrl->is_leader = false;

    /* 1. Обрив з'єднань і надсилання SIGTERM/SIGKILL процесам СУБД */
    system("pkill -9 -f postgres || true");

    /* 2. Якщо watchdog активний — не скидаємо його, дозволяючи ядру виконати reboot */
    if (ctrl->watchdog_fd >= 0) {
        fprintf(stderr, "[PANIC] Залишаємо Watchdog без подовження для апаратного скидання!\n");
    }
}

int main(int argc, char **argv) {
    (void)argc; (void)argv;
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    cluster_controller_t ctrl = {
        .watchdog_fd = init_watchdog(),
        .db_sock_fd = -1,
        .state = NODE_STATE_LEADER_ACTIVE,
        .lease_acquired_at_ms = get_monotonic_ms(),
        .last_successful_heartbeat_ms = get_monotonic_ms(),
        .is_leader = true
    };

    printf("[INFO] Контролер огородження запущено. Роль: LEADER. Моніторинг активний.\n");

    int iteration = 0;
    while (g_running && ctrl.state != NODE_STATE_FENCED) {
        uint64_t now = get_monotonic_ms();
        iteration++;

        /* Для тестування: на 6-й ітерації імітуємо мережевий збій із DCS */
        bool simulate_partition = (iteration >= 6 && iteration <= 8);

        bool db_ok = probe_local_db_health("/tmp/.s.PGSQL.5432");
        bool dcs_ok = renew_dcs_lease(simulate_partition);

        if (db_ok && dcs_ok) {
            ctrl.last_successful_heartbeat_ms = now;
            ctrl.state = NODE_STATE_LEADER_ACTIVE;
            ping_watchdog(ctrl.watchdog_fd);
            printf("[OK] Ітерація %d: СУБД здорова, лізу подовжено в DCS. Watchdog скинуто.\n", iteration);
        } else {
            uint64_t elapsed_since_hb = now - ctrl.last_successful_heartbeat_ms;
            ctrl.state = NODE_STATE_LEASE_DEGRADED;
            fprintf(stderr, "[WARN] Ітерація %d: Збій оновлення лізи (DB: %d, DCS: %d). "
                            "Минуло часу: %lu мс / Запас: %d мс\n",
                    iteration, db_ok, dcs_ok, (unsigned long)elapsed_since_hb, SAFETY_MARGIN_MS);

            if (elapsed_since_hb >= SAFETY_MARGIN_MS) {
                execute_emergency_fencing(&ctrl);
                break;
            }
        }

        struct timespec req = { .tv_sec = LOOP_WAIT_MS / 1000, .tv_nsec = (LOOP_WAIT_MS % 1000) * 1000000L };
        nanosleep(&req, NULL);
    }

    if (ctrl.state != NODE_STATE_FENCED) {
        disable_watchdog(ctrl.watchdog_fd);
    }
    printf("[INFO] Контролер завершив роботу.\n");
    return (ctrl.state == NODE_STATE_FENCED) ? 1 : 0;
}
