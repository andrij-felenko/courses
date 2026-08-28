/* custom-generator.c - Системний генератор systemd мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <errno.h>

#define CONFIG_PATH "/etc/custom-app.conf"
#define DEFAULT_EXEC "/usr/local/bin/custom-app"
#define DEFAULT_PORT "8080"

static void parse_config(const char *path, char *exec_path, size_t exec_sz, char *port, size_t port_sz) {
    FILE *f = fopen(path, "r");
    if (!f) return;

    char line[256];
    while (fgets(line, sizeof(line), f)) {
        /* Видалення символу нового рядка */
        line[strcspn(line, "\r\n")] = 0;
        if (line[0] == '#' || line[0] == '\0') continue;

        if (strncmp(line, "EXEC=", 5) == 0) {
            snprintf(exec_path, exec_sz, "%s", line + 5);
        } else if (strncmp(line, "PORT=", 5) == 0) {
            snprintf(port, port_sz, "%s", line + 5);
        }
    }
    fclose(f);
}

int main(int argc, char *argv[]) {
    /* Перевірка аргументів контракту systemd */
    if (argc < 4) {
        fprintf(stderr, "Помилка: генератор вимагає 3 аргументи (normal, early, late dirs)\n");
        return EXIT_FAILURE;
    }

    const char *normal_dir = argv[1];

    /* Перевірка наявності конфігурації */
    if (access(CONFIG_PATH, F_OK) != 0) {
        /* Якщо конфіг відсутній - це нормально, просто виходимо */
        return EXIT_SUCCESS;
    }

    char exec_path[256] = DEFAULT_EXEC;
    char port[16] = DEFAULT_PORT;
    parse_config(CONFIG_PATH, exec_path, sizeof(exec_path), port, sizeof(port));

    /* Створення шляху до юніта: <normal_dir>/custom-app.service */
    char service_path[512];
    snprintf(service_path, sizeof(service_path), "%s/custom-app.service", normal_dir);

    FILE *sf = fopen(service_path, "w");
    if (!sf) {
        fprintf(stderr, "Не вдалося створити unit-файл %s: %s\n", service_path, strerror(errno));
        return EXIT_FAILURE;
    }

    fprintf(sf,
        "[Unit]\n"
        "Description=Динамічна служба Custom App (порт %s)\n"
        "After=network.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        "ExecStart=%s --port %s\n"
        "Restart=on-failure\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n",
        port, exec_path, port);
    fclose(sf);

    /* Створення каталогу <normal_dir>/multi-user.target.wants/ */
    char wants_dir[512];
    snprintf(wants_dir, sizeof(wants_dir), "%s/multi-user.target.wants", normal_dir);
    if (mkdir(wants_dir, 0755) < 0 && errno != EEXIST) {
        fprintf(stderr, "Не вдалося створити каталог %s: %s\n", wants_dir, strerror(errno));
        return EXIT_FAILURE;
    }

    /* Створення відносного символьного посилання */
    char symlink_path[512];
    snprintf(symlink_path, sizeof(symlink_path), "%s/custom-app.service", wants_dir);

    /* Видаляємо старе посилання, якщо існувало */
    unlink(symlink_path);
    if (symlink("../custom-app.service", symlink_path) < 0) {
        fprintf(stderr, "Не вдалося створити symlink %s: %s\n", symlink_path, strerror(errno));
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
