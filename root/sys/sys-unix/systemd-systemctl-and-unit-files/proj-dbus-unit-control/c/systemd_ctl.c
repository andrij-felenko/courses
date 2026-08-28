/* systemd_ctl.c — Програмне управління юнітами C-бібліотекою sd-bus */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <systemd/sd-bus.h>

#define SYSTEMD_BUS_NAME "org.freedesktop.systemd1"
#define SYSTEMD_PATH     "/org/freedesktop/systemd1"
#define SYSTEMD_MANAGER  "org.freedesktop.systemd1.Manager"

static int query_unit_state(sd_bus *bus, const char *unit_name) {
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    char *unit_path = NULL;
    char *active_state = NULL;
    int r;

    /* 1. Отримати об'єктний шлях юніта через D-Bus метод GetUnit */
    r = sd_bus_call_method(bus,
                           SYSTEMD_BUS_NAME,
                           SYSTEMD_PATH,
                           SYSTEMD_MANAGER,
                           "GetUnit",
                           &error,
                           &m,
                           "s",
                           unit_name);
    if (r < 0) {
        fprintf(stderr, "Помилка виклику GetUnit: %s\n", error.message ? error.message : "невідомо");
        sd_bus_error_free(&error);
        return r;
    }

    r = sd_bus_message_read(m, "o", &unit_path);
    if (r < 0) {
        fprintf(stderr, "Помилка зчитування шляху об'єкта: %s\n", strerror(-r));
        sd_bus_message_unref(m);
        return r;
    }
    printf("Об'єктний шлях юніта %s: %s\n", unit_name, unit_path);

    /* 2. Прочитати властивість ActiveState з юніта */
    r = sd_bus_get_property_string(bus,
                                   SYSTEMD_BUS_NAME,
                                   unit_path,
                                   "org.freedesktop.systemd1.Unit",
                                   "ActiveState",
                                   &error,
                                   &active_state);
    if (r < 0) {
        fprintf(stderr, "Помилка читання ActiveState: %s\n", error.message ? error.message : "невідомо");
        sd_bus_error_free(&error);
        sd_bus_message_unref(m);
        return r;
    }

    printf("Поточний стан (ActiveState) юніта %s: %s\n", unit_name, active_state);

    free(active_state);
    sd_bus_message_unref(m);
    return 0;
}

static int start_unit(sd_bus *bus, const char *unit_name) {
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    char *job_path = NULL;
    int r;

    /* Викликати StartUnit із режимом транзакції "replace" */
    r = sd_bus_call_method(bus,
                           SYSTEMD_BUS_NAME,
                           SYSTEMD_PATH,
                           SYSTEMD_MANAGER,
                           "StartUnit",
                           &error,
                           &m,
                           "ss",
                           unit_name,
                           "replace");
    if (r < 0) {
        fprintf(stderr, "Не вдалося запустити юніт %s: %s\n", unit_name, error.message ? error.message : "невідомо");
        sd_bus_error_free(&error);
        return r;
    }

    r = sd_bus_message_read(m, "o", &job_path);
    if (r >= 0) {
        printf("Запит на запуск відправлено. Шлях транзакції Job: %s\n", job_path);
    }

    sd_bus_message_unref(m);
    return 0;
}

int main(int argc, char *argv[]) {
    sd_bus *bus = NULL;
    const char *unit_name = (argc > 1) ? argv[1] : "app@worker1.service";
    int r;

    /* Підключитися до системної шини D-Bus */
    r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Не вдалося підключитися до системної шини: %s\n", strerror(-r));
        return EXIT_FAILURE;
    }

    printf("Підключено до D-Bus systemd.\n");

    if (query_unit_state(bus, unit_name) >= 0) {
        printf("Надсилання команди StartUnit для %s...\n", unit_name);
        start_unit(bus, unit_name);
    }

    sd_bus_unref(bus);
    return EXIT_SUCCESS;
}
