#include <systemd/sd-bus.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h>

int main(void) {
    sd_bus *bus = NULL;
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    int r;

    // 1. Відкриття підключення до системної шини DBus
    r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Помилка підключення до системної шини DBus: %s\n", strerror(-r));
        goto finish;
    }

    // 2. Ініціалізація виклику методу StartTransientUnit
    r = sd_bus_message_new_method_call(
        bus, &m,
        "org.freedesktop.systemd1",
        "/org/freedesktop/systemd1",
        "org.freedesktop.systemd1.Manager",
        "StartTransientUnit"
    );
    if (r < 0) {
        fprintf(stderr, "Помилка створення об'єкта повідомлення: %s\n", strerror(-r));
        goto finish;
    }

    // Аргумент 1: Назва створюваного юніта (Scope)
    // Аргумент 2: Режим обробки конфліктів ("fail" повертає помилку, якщо юніт існує)
    r = sd_bus_message_append(m, "ss", "custom-app-worker.scope", "fail");
    if (r < 0) goto finish;

    // Аргумент 3: Відкриваємо масив властивостей a(sv)
    r = sd_bus_message_open_container(m, 'a', "(sv)");
    if (r < 0) goto finish;

    // Властивість 1: PIDs — масив uint32 з PID поточного процесу
    r = sd_bus_message_open_container(m, 'r', "sv");
    if (r < 0) goto finish;
    r = sd_bus_message_append(m, "s", "PIDs");
    if (r < 0) goto finish;
    r = sd_bus_message_open_container(m, 'v', "au");
    if (r < 0) goto finish;
    uint32_t current_pid = (uint32_t)getpid();
    r = sd_bus_message_append_array(m, 'u', &current_pid, sizeof(current_pid));
    if (r < 0) goto finish;
    sd_bus_message_close_container(m); // закриваємо 'v'
    sd_bus_message_close_container(m); // закриваємо 'r'

    // Властивість 2: MemoryMax = 512MB (536870912 байтів)
    r = sd_bus_message_open_container(m, 'r', "sv");
    if (r < 0) goto finish;
    r = sd_bus_message_append(m, "s", "MemoryMax");
    if (r < 0) goto finish;
    r = sd_bus_message_open_container(m, 'v', "t");
    if (r < 0) goto finish;
    uint64_t mem_limit = 512ULL * 1024ULL * 1024ULL;
    r = sd_bus_message_append(m, "t", mem_limit);
    if (r < 0) goto finish;
    sd_bus_message_close_container(m); // закриваємо 'v'
    sd_bus_message_close_container(m); // закриваємо 'r'

    // Властивість 3: TasksMax = 64
    r = sd_bus_message_open_container(m, 'r', "sv");
    if (r < 0) goto finish;
    r = sd_bus_message_append(m, "s", "TasksMax");
    if (r < 0) goto finish;
    r = sd_bus_message_open_container(m, 'v', "t");
    if (r < 0) goto finish;
    r = sd_bus_message_append(m, "t", (uint64_t)64);
    if (r < 0) goto finish;
    sd_bus_message_close_container(m); // закриваємо 'v'
    sd_bus_message_close_container(m); // закриваємо 'r'

    sd_bus_message_close_container(m); // закриваємо масив 'a(sv)'

    // Аргумент 4: Порожній масив aux units a(sa(sv))
    r = sd_bus_message_append(m, "a(sa(sv))", 0);
    if (r < 0) goto finish;

    // 3. Синхронна відправка виклику через шину DBus
    r = sd_bus_call(bus, m, 0, &error, NULL);
    if (r < 0) {
        fprintf(stderr, "Помилка виконання DBus виклику: %s\n", error.message);
        goto finish;
    }

    printf("Успішно створено Scope 'custom-app-worker.scope' для PID %d\n", getpid());

finish:
    sd_bus_error_free(&error);
    sd_bus_message_unref(m);
    sd_bus_unref(bus);
    return r < 0 ? EXIT_FAILURE : EXIT_SUCCESS;
}
