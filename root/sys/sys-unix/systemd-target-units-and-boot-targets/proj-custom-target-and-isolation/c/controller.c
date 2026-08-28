/* controller.c — Програмна ізоляція станів через sd-bus (C) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <systemd/sd-bus.h>

/**
 * Виконує програмну ізоляцію вказаного target-юніта через D-Bus API.
 * @param target_name Назва target-юніта (наприклад, "kiosk.target")
 * @return EXIT_SUCCESS при успіху або EXIT_FAILURE при помилці
 */
int isolate_target(const char *target_name) {
    sd_bus *bus = NULL;
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    const char *job_path = NULL;
    int r;

    /* 1. Підключення до системної шини D-Bus (/run/systemd/system/bus) */
    r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Помилка: не вдалося підключитися до системної шини D-Bus: %s\n", strerror(-r));
        goto finish;
    }

    printf("Надсилання D-Bus запиту StartUnit(\"%s\", \"isolate\")...\n", target_name);

    /* 2. Відправка RPC виклику StartUnit до об'єкта PID 1 */
    r = sd_bus_call_method(
        bus,
        "org.freedesktop.systemd1",           /* Назва системного сервісу D-Bus */
        "/org/freedesktop/systemd1",          /* Шлях до головного об'єкта Manager */
        "org.freedesktop.systemd1.Manager",   /* Назва D-Bus інтерфейсу */
        "StartUnit",                          /* Метод для виклику */
        &error,                               /* Структура для повернення деталізації помилки */
        &m,                                   /* Відповідне повідомлення D-Bus */
        "ss",                                 /* Сигнатура вхідних типів: string, string */
        target_name,                          /* Аргумент 1: Назва цільового таргета */
        "isolate"                             /* Аргумент 2: Режим ізоляції */
    );

    if (r < 0) {
        fprintf(stderr, "Збій виклику StartUnit: %s\n", error.message ? error.message : strerror(-r));
        goto finish;
    }

    /* 3. Зчитування результату відповіді (ObjectPath створеної транзакції) */
    r = sd_bus_message_read(m, "o", &job_path);
    if (r < 0) {
        fprintf(stderr, "Помилка розбору відповіді D-Bus: %s\n", strerror(-r));
        goto finish;
    }

    printf("Успішно створено транзакційну роботу ізоляції: %s\n", job_path);

finish:
    /* Очищення ресурсів D-Bus */
    sd_bus_error_free(&error);
    sd_bus_message_unref(m);
    sd_bus_unref(bus);
    return r < 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}

int main(int argc, char *argv[]) {
    const char *target = (argc > 1) ? argv[1] : "kiosk.target";
    return isolate_target(target);
}
