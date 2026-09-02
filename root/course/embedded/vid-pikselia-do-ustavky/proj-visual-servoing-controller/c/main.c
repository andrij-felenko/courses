#define _GNU_SOURCE

#include <errno.h>
#include <pthread.h>
#include <signal.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/timerfd.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>

#include "guidance.h"
#include "mavlink_link.h"
#include "spsc_queue.h"

/* Бортовий контролер візуального наведення.
 *
 * Потік зору      — блокувальне читання детекцій з UNIX-сокета (нейромережа
 *                   крутиться окремим процесом на NPU й шле центр рамки та
 *                   АПАРАТНУ мітку початку експозиції);
 * контур керування — головний потік, SCHED_FIFO, timerfd на 100 Гц: гіроскопи
 *                   з MAVLink, крок регулятора, уставки в автопілот.
 *
 * Між ними — черга без замків. Спільної пам'яті більше немає жодної. */

#define CONTROL_HZ 100
#define HOVER_THRUST 0.55f

/* Дротовий формат детектора: сталий розмір, без вирівнювальних дір. */
typedef struct __attribute__((packed)) {
    uint64_t t_capture_us;   /* CLOCK_MONOTONIC тієї самої машини */
    float    u;
    float    v;
    float    width;
    float    height;
    uint8_t  valid;
} DetectionWire;

static volatile sig_atomic_t g_stop = 0;

static void on_signal(int sig)
{
    (void)sig;
    g_stop = 1;
}

static uint64_t now_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000u + (uint64_t)(ts.tv_nsec / 1000);
}

/* ── Потік зору ─────────────────────────────────────────────────────────── */

typedef struct {
    int             fd;
    DetectionQueue *queue;
} VisionArgs;

static void *vision_thread(void *arg)
{
    VisionArgs *va = (VisionArgs *)arg;

    for (;;) {
        DetectionWire wire;
        const ssize_t n = recv(va->fd, &wire, sizeof(wire), 0);

        if (g_stop) {
            break;
        }
        if (n < 0) {
            if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK) {
                continue;   /* спрацював SO_RCVTIMEO — перевіряємо прапорець виходу */
            }
            perror("vision: recv");
            break;
        }
        if (n != (ssize_t)sizeof(wire)) {
            fprintf(stderr, "vision: пакет %zd Б замість %zu\n", n, sizeof(wire));
            continue;
        }
        if (!wire.valid) {
            continue;       /* кадр без цілі: мовчимо, таймаут розбереться */
        }

        TargetDetection det = {
            .u = wire.u,
            .v = wire.v,
            .width = wire.width,
            .height = wire.height,
            .t_capture_us = wire.t_capture_us,
        };
        detq_push(va->queue, &det);
    }

    return NULL;
}

static int open_detector_socket(const char *path)
{
    const int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) {
        perror("detector: socket");
        return -1;
    }

    unlink(path);   /* залишок від попереднього запуску */

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    if (strlen(path) >= sizeof(addr.sun_path)) {
        fprintf(stderr, "detector: задовгий шлях сокета\n");
        close(fd);
        return -1;
    }
    strncpy(addr.sun_path, path, sizeof(addr.sun_path) - 1);

    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        perror("detector: bind");
        close(fd);
        return -1;
    }

    /* Таймаут читання — єдиний спосіб розбудити потік на зупинці. */
    struct timeval tv = { .tv_sec = 0, .tv_usec = 200000 };
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    return fd;
}

/* ── Контур керування ───────────────────────────────────────────────────── */

static void promote_to_realtime(void)
{
    struct sched_param param = { .sched_priority = 80 };
    if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &param) != 0) {
        /* Без CAP_SYS_NICE це звичайна ситуація на столі розробника:
         * працювати можна, але джитер такту вимірювати немає сенсу. */
        fprintf(stderr, "увага: SCHED_FIFO недоступний, контур піде як SCHED_OTHER\n");
    }
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        fprintf(stderr, "увага: mlockall не вдався, можливі затримки на сторінкових збоях\n");
    }
}

int main(int argc, char **argv)
{
    const char *device = (argc > 1) ? argv[1] : "/dev/ttyUSB0";
    const int baud = (argc > 2) ? atoi(argv[2]) : 921600;
    const char *sock_path = (argc > 3) ? argv[3] : "/run/vision/detections.sock";

    signal(SIGINT, on_signal);
    signal(SIGTERM, on_signal);
    signal(SIGPIPE, SIG_IGN);

    const CameraIntrinsics cam = {
        .fx = 812.4f, .fy = 811.9f,
        .cx = 319.6f, .cy = 241.2f,
        .img_width = 640.0f, .img_height = 480.0f,
    };

    VisualGuidance guidance;
    visual_guidance_init(&guidance, &cam);

    DetectionQueue queue;
    detq_init(&queue);

    MavlinkLink link;
    if (mavlink_link_open(&link, device, baud) != 0) {
        return EXIT_FAILURE;
    }

    const int sock = open_detector_socket(sock_path);
    if (sock < 0) {
        mavlink_link_close(&link);
        return EXIT_FAILURE;
    }

    VisionArgs va = { .fd = sock, .queue = &queue };
    pthread_t vision;
    if (pthread_create(&vision, NULL, vision_thread, &va) != 0) {
        perror("pthread_create");
        close(sock);
        mavlink_link_close(&link);
        return EXIT_FAILURE;
    }

    promote_to_realtime();

    const int timer = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC);
    if (timer < 0) {
        perror("timerfd_create");
        g_stop = 1;
    } else {
        const long period_ns = 1000000000L / CONTROL_HZ;
        struct itimerspec its = {
            .it_interval = { .tv_sec = 0, .tv_nsec = period_ns },
            .it_value    = { .tv_sec = 0, .tv_nsec = period_ns },
        };
        if (timerfd_settime(timer, 0, &its, NULL) != 0) {
            perror("timerfd_settime");
            g_stop = 1;
        }
    }

    const uint64_t boot_us = now_us();
    uint64_t last_report_us = boot_us;
    unsigned overruns = 0;
    unsigned tx_errors = 0;

    while (!g_stop) {
        uint64_t ticks = 0;
        const ssize_t n = read(timer, &ticks, sizeof(ticks));
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("timerfd: read");
            break;
        }
        if (ticks > 1) {
            /* Такт проґавлено — це рівно те, чого не має бути в контурі
             * реального часу, тож рахуємо й показуємо. */
            overruns += (unsigned)(ticks - 1);
        }

        const uint64_t t = now_us();

        /* 1. Свіжі гіроскопи від автопілота. */
        mavlink_link_poll(&link);

        /* 2. Усі детекції, що встигли накопичитися. */
        TargetDetection det;
        while (detq_pop(&queue, &det)) {
            visual_guidance_on_detection(&guidance, &det);
        }

        /* 3. Крок контуру. */
        GuidanceSetpoints sp;
        visual_guidance_update(&guidance, t, link.gyro_yaw, link.gyro_pitch, &sp);

        /* 4. Уставки в автопілот. Уставки шлемо КОЖЕН такт, зокрема й нульові:
         * мовчання довше за пів секунди автопілот трактує як зрив offboard. */
        const uint32_t boot_ms = (uint32_t)((t - boot_us) / 1000u);
        if (mavlink_link_send_rates(&link, &sp, HOVER_THRUST, boot_ms) != 0) {
            tx_errors++;
        }

        /* 5. Телеметрія раз на секунду. Поздовжня уставка йде контуру позиції
         * апарата — це вже не наш модуль, тут вона лише в звіті. */
        if (t - last_report_us >= 1000000u) {
            last_report_us = t;
            fprintf(stderr,
                    "супровід=%d кадрів=%u відкинуто=%u черга_втрат=%u такти=%u tx_err=%u "
                    "| yaw=%+.3f pitch=%+.3f рад/с vf=%+.2f м/с\n",
                    (int)sp.target_acquired, guidance.frames_used,
                    guidance.frames_rejected, detq_dropped(&queue),
                    overruns, tx_errors,
                    (double)sp.yaw_rate_rad_s, (double)sp.pitch_rate_rad_s,
                    (double)sp.forward_vel_m_s);
        }
    }

    g_stop = 1;
    pthread_join(vision, NULL);

    if (timer >= 0) {
        close(timer);
    }
    close(sock);
    unlink(sock_path);
    mavlink_link_close(&link);
    return EXIT_SUCCESS;
}
