/* inspect_ns.c — Перевірка просторів імен процесу мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>

static int check_namespace_entry(const char *pid_str, const char *ns_name) {
    char path[256];
    snprintf(path, sizeof(path), "/proc/%s/ns/%s", pid_str, ns_name);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", path, strerror(errno));
        return -1;
    }

    printf("[C Inspector] Namespace %s для PID %s успішно відкрито (fd=%d)\n",
           ns_name, pid_str, fd);
    close(fd);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <PID>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *pid = argv[1];
    printf("=== Аналіз просторів імен процесу PID %s ===\n", pid);

    check_namespace_entry(pid, "mnt");
    check_namespace_entry(pid, "pid");
    check_namespace_entry(pid, "net");
    check_namespace_entry(pid, "uts");
    check_namespace_entry(pid, "ipc");
    check_namespace_entry(pid, "user");

    return EXIT_SUCCESS;
}
