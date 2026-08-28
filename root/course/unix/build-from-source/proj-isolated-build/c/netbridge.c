/* netbridge.c — C-реалізація з прямим викликом libuv API */
#include <stdio.h>
#include <stdlib.h>
#include <uv.h>

static void timer_callback(uv_timer_t *handle) {
    int64_t uptime = uv_now(handle->loop);
    printf("[netbridge] Сервіс працює стабільно. Поточний час циклу: %ld мс\n", (long)uptime);
    /* Зупиняємо таймер після першого спрацьовування для чистого виходу */
    uv_timer_stop(handle);
    uv_stop(handle->loop);
}

int main(int argc, char **argv) {
    printf("[netbridge] Ініціалізація демона...\n");
    uv_loop_t *loop = uv_default_loop();
    if (!loop) {
        fprintf(stderr, "Помилка: не вдалося створити uv_loop\n");
        return EXIT_FAILURE;
    }

    uv_timer_t timer_req;
    int status = uv_timer_init(loop, &timer_req);
    if (status < 0) {
        fprintf(stderr, "Помилка ініціалізації таймера: %s\n", uv_strerror(status));
        return EXIT_FAILURE;
    }

    /* Запуск таймера: спрацювати через 100 мс */
    uv_timer_start(&timer_req, timer_callback, 100, 0);

    /* Запуск основного циклу обробки подій */
    uv_run(loop, UV_RUN_DEFAULT);
    uv_loop_close(loop);

    printf("[netbridge] Роботу успішно завершено.\n");
    return EXIT_SUCCESS;
}
