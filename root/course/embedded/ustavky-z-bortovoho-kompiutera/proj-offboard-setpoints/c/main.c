#include <errno.h>
#include <math.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "streamer.h"

#define UART_PORT   "/dev/ttyAMA0"
#define UART_BAUD   B921600
#define OUR_SYS_ID  240   /* окремий системний ID супутнього комп'ютера */
#define OUR_COMP_ID 191   /* MAV_COMP_ID_ONBOARD_COMPUTER */
#define PLANNER_HZ  10

static offboard_streamer_t g_streamer;
static volatile sig_atomic_t g_stop = 0;

static void on_signal(int sig) {
    (void)sig;
    g_stop = 1;
}

/* Повільний контур планування. Тут була б обробка кадру нейромережею,
 * оновлення воксельної карти й побудова сплайна — усе зі змінною
 * тривалістю. Для генератора важливо лише те, що цілі приходять рідко
 * (10 Гц) і нерівномірно, а їхній штамп часу може будь-коли застаріти. */
static void *planner_thread(void *arg) {
    offboard_streamer_t *s = (offboard_streamer_t *)arg;
    const double dt = 1.0 / PLANNER_HZ;
    const float speed = 2.0f;   /* м/с */
    const float radius = 5.0f;  /* м */
    const float omega = speed / radius;
    double t = 0.0;

    while (!g_stop) {
        /* Обліт кола: вектор швидкості в горизонті, ніс за напрямком руху. */
        float vx = speed * cosf(omega * (float)t);
        float vy = speed * sinf(omega * (float)t);
        streamer_set_target(s, vx, vy, 0.0f, atan2f(vy, vx));

        t += dt;
        usleep((useconds_t)(dt * 1e6)); /* планувальник не в реальному часі */
    }
    return NULL;
}

int main(void) {
    /* Закріплюємо сторінки в RAM: жодного page fault усередині
     * такту 20 Гц, навіть коли зір з'їдає всю вільну пам'ять. */
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        fprintf(stderr, "[main] mlockall: %s — сторінки можуть піти в підкачку\n",
                strerror(errno));
    }

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = on_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    if (streamer_init(&g_streamer, UART_PORT, UART_BAUD, OUR_SYS_ID, OUR_COMP_ID) != 0) {
        return 1;
    }

    pthread_t rt_thread;
    pthread_t plan_thread;
    if (pthread_create(&rt_thread, NULL, streamer_thread, &g_streamer) != 0) {
        fprintf(stderr, "[main] не вдалося створити RT-потік: %s\n", strerror(errno));
        streamer_destroy(&g_streamer);
        return 1;
    }
    if (pthread_create(&plan_thread, NULL, planner_thread, &g_streamer) != 0) {
        fprintf(stderr, "[main] не вдалося створити потік планувальника: %s\n",
                strerror(errno));
        streamer_request_shutdown(&g_streamer);
        pthread_join(rt_thread, NULL);
        streamer_destroy(&g_streamer);
        return 1;
    }

    /* Даємо планувальнику видати першу ціль — і аж тоді просимо режим. */
    usleep(300000);
    streamer_begin_mission(&g_streamer);

    while (!g_stop && streamer_running(&g_streamer)) {
        sleep(1);
    }

    fprintf(stderr, "[main] зупинка: гальмуємо й віддаємо керування автопілоту\n");
    streamer_request_shutdown(&g_streamer);
    pthread_join(rt_thread, NULL);
    g_stop = 1;
    pthread_join(plan_thread, NULL);
    streamer_destroy(&g_streamer);
    return 0;
}
