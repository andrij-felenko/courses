// Створення тимчасового Scope через C API (libsystemd sd-bus)
#include <systemd/sd-bus.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>

int create_scoped_cgroup(const char *scope_name, uint64_t mem_bytes) {
    sd_bus *bus = NULL;
    sd_bus_message *m = NULL;
    sd_bus_error error = SD_BUS_ERROR_NULL;
    int r;

    r = sd_bus_open_system(&bus);
    if (r < 0) return r;

    r = sd_bus_message_new_method_call(bus, &m,
        "org.freedesktop.systemd1",
        "/org/freedesktop/systemd1",
        "org.freedesktop.systemd1.Manager",
        "StartTransientUnit");
    if (r < 0) goto cleanup;

    r = sd_bus_message_append(m, "ss", scope_name, "fail");
    if (r < 0) goto cleanup;

    // Відкриваємо масив properties a(sv)
    r = sd_bus_message_open_container(m, 'a', "(sv)");
    if (r < 0) goto cleanup;

    // PIDs
    sd_bus_message_open_container(m, 'r', "sv");
    sd_bus_message_append(m, "s", "PIDs");
    sd_bus_message_open_container(m, 'v', "au");
    uint32_t pid = (uint32_t)getpid();
    sd_bus_message_append_array(m, 'u', &pid, sizeof(pid));
    sd_bus_message_close_container(m);
    sd_bus_message_close_container(m);

    // MemoryMax
    sd_bus_message_open_container(m, 'r', "sv");
    sd_bus_message_append(m, "s", "MemoryMax");
    sd_bus_message_open_container(m, 'v', "t");
    sd_bus_message_append(m, "t", mem_bytes);
    sd_bus_message_close_container(m);
    sd_bus_message_close_container(m);

    sd_bus_message_close_container(m); // close a(sv)

    r = sd_bus_message_append(m, "a(sa(sv))", 0); // aux units
    if (r < 0) goto cleanup;

    r = sd_bus_call(bus, m, 0, &error, NULL);

cleanup:
    sd_bus_error_free(&error);
    sd_bus_message_unref(m);
    sd_bus_unref(bus);
    return r;
}
