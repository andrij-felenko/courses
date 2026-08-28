#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>

/* Допоміжна функція запису рядка у файл-атрибут configfs */
static int write_attr(const char *path, const char *val) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття атрибута %s: %s\n", path, strerror(errno));
        return -1;
    }
    ssize_t len = strlen(val);
    if (write(fd, val, len) != len) {
        fprintf(stderr, "Помилка запису у %s: %s\n", path, strerror(errno));
        close(fd);
        return -1;
    }
    close(fd);
    return 0;
}

int main(void) {
    const char *subsys_dir = "/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage";
    const char *ns_dir     = "/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage/namespaces/1";
    const char *port_dir   = "/sys/kernel/config/nvmet/ports/1";
    const char *link_dir   = "/sys/kernel/config/nvmet/ports/1/subsystems/nqn.2026-08.org.example:target-storage";

    printf("Розпочинаємо конфігурацію NVMe Target через C API...\n");

    /* 1. Створення підсистеми */
    if (mkdir(subsys_dir, 0755) < 0 && errno != EEXIST) {
        perror("mkdir subsys failed");
        return 1;
    }
    if (write_attr("/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage/attr_allow_any_host", "1\n") < 0)
        goto cleanup_subsys;

    /* 2. Налаштування простору імен */
    if (mkdir(ns_dir, 0755) < 0 && errno != EEXIST) {
        perror("mkdir namespace failed");
        goto cleanup_subsys;
    }
    if (write_attr("/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage/namespaces/1/device_path", "/dev/ram0\n") < 0)
        goto cleanup_ns;
    if (write_attr("/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage/namespaces/1/enable", "1\n") < 0)
        goto cleanup_ns;

    /* 3. Створення та конфігурація порту */
    if (mkdir(port_dir, 0755) < 0 && errno != EEXIST) {
        perror("mkdir port failed");
        goto cleanup_ns;
    }
    if (write_attr("/sys/kernel/config/nvmet/ports/1/addr_trtype", "tcp\n") < 0) goto cleanup_port;
    if (write_attr("/sys/kernel/config/nvmet/ports/1/addr_traddr", "192.168.1.50\n") < 0) goto cleanup_port;
    if (write_attr("/sys/kernel/config/nvmet/ports/1/addr_trsvcid", "4420\n") < 0) goto cleanup_port;
    if (write_attr("/sys/kernel/config/nvmet/ports/1/addr_adrfam", "ipv4\n") < 0) goto cleanup_port;

    /* 4. Прив'язка підсистеми до порту через symlink (Активація) */
    if (symlink(subsys_dir, link_dir) < 0 && errno != EEXIST) {
        perror("symlink failed");
        goto cleanup_port;
    }

    printf("NVMe Target успішно сконфігуровано та запущено через C API!\n");
    return 0;

/* Політика відкату при виникненні помилок */
cleanup_port:
    rmdir(port_dir);
cleanup_ns:
    write_attr("/sys/kernel/config/nvmet/subsystems/nqn.2026-08.org.example:target-storage/namespaces/1/enable", "0\n");
    rmdir(ns_dir);
cleanup_subsys:
    rmdir(subsys_dir);
    return 1;
}
