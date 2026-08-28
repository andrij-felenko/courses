#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>

/* Отримання абсолютного шляху до файлу конфігурації програми */
int get_app_config_path(const char *app_name, char *out_path, size_t out_size) {
    if (!app_name || !out_path || out_size == 0) {
        return -1;
    }

    /* Якщо процес запущено від root або як системну службу — дивимось у /etc */
    if (geteuid() == 0) {
        int written = snprintf(out_path, out_size, "/etc/%s/config.toml", app_name);
        return (written > 0 && (size_t)written < out_size) ? 0 : -1;
    }

    /* Для звичайного користувача перевіряємо XDG_CONFIG_HOME */
    const char *xdg_config = getenv("XDG_CONFIG_HOME");
    if (xdg_config && *xdg_config) {
        int written = snprintf(out_path, out_size, "%s/%s/config.toml", xdg_config, app_name);
        return (written > 0 && (size_t)written < out_size) ? 0 : -1;
    }

    /* Резервний варіант: $HOME/.config */
    const char *home = getenv("HOME");
    if (!home || !*home) {
        return -1;
    }

    int written = snprintf(out_path, out_size, "%s/.config/%s/config.toml", home, app_name);
    return (written > 0 && (size_t)written < out_size) ? 0 : -1;
}
