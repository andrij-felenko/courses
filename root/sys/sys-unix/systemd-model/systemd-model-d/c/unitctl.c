// Те саме, що робить systemctl start, але вручну: підписка на сигнали менеджера,
// виклик StartUnit і очікування JobRemoved саме нашої роботи. Показує, що
// systemctl — звичайний клієнт D-Bus без жодних особливих прав на PID 1.
#include <systemd/sd-bus.h>

#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MANAGER_SERVICE "org.freedesktop.systemd1"
#define MANAGER_PATH    "/org/freedesktop/systemd1"
#define MANAGER_IFACE   "org.freedesktop.systemd1.Manager"
#define UNIT_IFACE      "org.freedesktop.systemd1.Unit"

#define JOB_TIMEOUT_USEC (60ULL * 1000000ULL)

struct job_watch {
    const char *job_path;   // об'єктний шлях роботи, на яку чекаємо
    char result[64];        // done, failed, canceled, timeout, dependency, skipped
    bool finished;
};

static uint64_t now_usec(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)ts.tv_nsec / 1000ULL;
}

// Сигнатура сигналу JobRemoved — "uoss": номер роботи, її об'єктний шлях,
// ім'я юніта й результат. На завантаженні таких сигналів ідуть сотні,
// тому фільтруємо за шляхом своєї роботи.
static int on_job_removed(sd_bus_message *m, void *userdata, sd_bus_error *ret_error)
{
    struct job_watch *watch = userdata;
    const char *path = NULL, *unit = NULL, *result = NULL;
    uint32_t id = 0;
    int r;

    (void)ret_error;

    r = sd_bus_message_read(m, "uoss", &id, &path, &unit, &result);
    if (r < 0) {
        fprintf(stderr, "Не вдалося розібрати JobRemoved: %s\n", strerror(-r));
        return 0;   // від'ємне значення тут обірвало б обробку шини
    }

    if (strcmp(path, watch->job_path) != 0)
        return 0;

    snprintf(watch->result, sizeof watch->result, "%s", result);
    watch->finished = true;
    return 0;
}

static int print_active_state(sd_bus *bus, const char *unit)
{
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *reply = NULL;
    const char *unit_path = NULL;
    char *state = NULL;
    int r;

    // Об'єктний шлях юніта екранований: nginx.service → nginx_2eservice.
    r = sd_bus_call_method(bus, MANAGER_SERVICE, MANAGER_PATH, MANAGER_IFACE,
                           "GetUnit", &error, &reply, "s", unit);
    if (r < 0) {
        fprintf(stderr, "GetUnit(%s): %s\n", unit,
                error.message ? error.message : strerror(-r));
        goto finish;
    }

    r = sd_bus_message_read(reply, "o", &unit_path);
    if (r < 0)
        goto finish;

    r = sd_bus_get_property_string(bus, MANAGER_SERVICE, unit_path, UNIT_IFACE,
                                   "ActiveState", &error, &state);
    if (r < 0) {
        fprintf(stderr, "ActiveState: %s\n",
                error.message ? error.message : strerror(-r));
        goto finish;
    }

    printf("Стан юніта %s: %s\n", unit, state);

finish:
    free(state);
    sd_bus_message_unref(reply);
    sd_bus_error_free(&error);
    return r;
}

int main(int argc, char *argv[])
{
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *reply = NULL;
    sd_bus_slot *slot = NULL;
    sd_bus *bus = NULL;
    struct job_watch watch;
    const char *method, *unit, *job_path = NULL;
    uint64_t deadline;
    int r;

    if (argc != 3) {
        fprintf(stderr, "Використання: %s start|stop|restart <юніт>\n", argv[0]);
        return 2;
    }

    if (strcmp(argv[1], "start") == 0)
        method = "StartUnit";
    else if (strcmp(argv[1], "stop") == 0)
        method = "StopUnit";
    else if (strcmp(argv[1], "restart") == 0)
        method = "RestartUnit";
    else {
        fprintf(stderr, "Невідома дія: %s\n", argv[1]);
        return 2;
    }

    unit = argv[2];
    memset(&watch, 0, sizeof watch);

    r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Не вдалося відкрити системну шину: %s\n", strerror(-r));
        goto finish;
    }

    // Без Subscribe менеджер не розсилає сигнали про роботи тим клієнтам,
    // які про них не просили: інакше шина потонула б у трафіку завантаження.
    r = sd_bus_call_method(bus, MANAGER_SERVICE, MANAGER_PATH, MANAGER_IFACE,
                           "Subscribe", &error, NULL, NULL);
    if (r < 0) {
        fprintf(stderr, "Subscribe: %s\n",
                error.message ? error.message : strerror(-r));
        goto finish;
    }

    // Правило зіставлення ставимо ДО виклику StartUnit: коротка робота встигає
    // завершитися раніше, ніж повернеться відповідь на виклик.
    r = sd_bus_match_signal(bus, &slot, MANAGER_SERVICE, MANAGER_PATH,
                            MANAGER_IFACE, "JobRemoved", on_job_removed, &watch);
    if (r < 0) {
        fprintf(stderr, "Не вдалося підписатися на JobRemoved: %s\n", strerror(-r));
        goto finish;
    }

    // Другий аргумент — режим розв'язання транзакції: replace витісняє
    // конфліктні роботи, fail відхиляє запит за їх наявності.
    r = sd_bus_call_method(bus, MANAGER_SERVICE, MANAGER_PATH, MANAGER_IFACE,
                           method, &error, &reply, "ss", unit, "replace");
    if (r < 0) {
        fprintf(stderr, "%s(%s): %s\n", method, unit,
                error.message ? error.message : strerror(-r));
        goto finish;
    }

    r = sd_bus_message_read(reply, "o", &job_path);
    if (r < 0) {
        fprintf(stderr, "Відповідь без шляху роботи: %s\n", strerror(-r));
        goto finish;
    }

    watch.job_path = job_path;
    printf("Створено роботу: %s\n", job_path);

    deadline = now_usec() + JOB_TIMEOUT_USEC;
    while (!watch.finished) {
        uint64_t now;

        r = sd_bus_process(bus, NULL);
        if (r < 0) {
            fprintf(stderr, "Обробка шини: %s\n", strerror(-r));
            goto finish;
        }
        if (r > 0)
            continue;   // у черзі могло лишитися ще повідомлення

        now = now_usec();
        if (now >= deadline) {
            fprintf(stderr, "Робота %s не завершилась за хвилину\n", job_path);
            r = -ETIMEDOUT;
            goto finish;
        }

        r = sd_bus_wait(bus, deadline - now);
        if (r < 0) {
            fprintf(stderr, "Очікування шини: %s\n", strerror(-r));
            goto finish;
        }
    }

    printf("Робота завершилась з результатом: %s\n", watch.result);

    // Результат роботи й стан юніта — різні речі: робота може бути done,
    // а служба вже встигнути впасти й опинитися у failed.
    r = print_active_state(bus, unit);
    if (r < 0)
        goto finish;

    r = strcmp(watch.result, "done") == 0 ? 0 : -EIO;

finish:
    sd_bus_slot_unref(slot);
    sd_bus_message_unref(reply);
    sd_bus_error_free(&error);
    sd_bus_flush_close_unref(bus);
    return r < 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}
