/* Inspector.c — Отримання даних контейнера nspawn через libsystemd sd-bus */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <systemd/sd-bus.h>

int main(int argc, char *argv[]) {
    const char *machine_name = (argc > 1) ? argv[1] : "web-node1";
    sd_bus *bus = NULL;
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    char *path = NULL;
    int r;

    /* 1. Підключення до системної шини D-Bus хоста */
    r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Помилка підключення до системної шини D-Bus: %s\n", strerror(-r));
        return EXIT_FAILURE;
    }

    /* 2. Виклик методу GetMachine(s) у служби org.freedesktop.machine1 */
    r = sd_bus_call_method(
        bus,
        "org.freedesktop.machine1",           /* Назва D-Bus сервісу */
        "/org/freedesktop/machine1",          /* Шлях до менеджера */
        "org.freedesktop.machine1.Manager",   /* Інтерфейс */
        "GetMachine",                         /* Назва методу */
        &error,                               /* Структура помилки */
        &m,                                   /* Повідомлення відповіді */
        "s",                                  /* Сигнатура вхідних даних */
        machine_name                          /* Назва контейнера */
    );

    if (r < 0) {
        fprintf(stderr, "Не вдалося знайти контейнер '%s': %s\n", machine_name, error.message);
        sd_bus_error_free(&error);
        sd_bus_unref(bus);
        return EXIT_FAILURE;
    }

    /* 3. Читання об'єктного шляху з отриманого повідомлення */
    r = sd_bus_message_read(m, "o", &path);
    if (r < 0) {
        fprintf(stderr, "Помилка розбору відповіді D-Bus: %s\n", strerror(-r));
        sd_bus_message_unref(m);
        sd_bus_unref(bus);
        return EXIT_FAILURE;
    }

    printf("Контейнер '%s' успішно зареєстровано у службі systemd-machined!\n", machine_name);
    printf("Об'єктний шлях D-Bus: %s\n", path);

    /* 4. Звільнення ресурсів */
    sd_bus_message_unref(m);
    sd_bus_unref(bus);
    return EXIT_SUCCESS;
}
