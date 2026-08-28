#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <poll.h>
#include <errno.h>

/* Запис текстового значення у псевдофайл cgroupfs */
static int write_control_file(const char *path, const char *value) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        return -1;
    }
    ssize_t len = (ssize_t)strlen(value);
    ssize_t written = write(fd, value, (size_t)len);
    close(fd);
    return (written == len) ? 0 : -1;
}

int main(void) {
    const char *cgroup_root = "/sys/fs/cgroup";
    const char *child_dir = "/sys/fs/cgroup/demo_workload";
    char path_buf[512];

    /* 1. Активація контролерів для дочірніх cgroups */
    snprintf(path_buf, sizeof(path_buf), "%s/cgroup.subtree_control", cgroup_root);
    if (write_control_file(path_buf, "+cpu +memory\n") < 0) {
        perror("Не вдалося увімкнути subtree_control (потрібні права root)");
        return EXIT_FAILURE;
    }

    /* 2. Створення нової cgroup через mkdir */
    if (mkdir(child_dir, 0755) < 0 && errno != EEXIST) {
        perror("Помилка створення каталогу cgroup");
        return EXIT_FAILURE;
    }

    /* 3. Встановлення ліміту пам'яті (512 МіБ = 536870912 байтів) */
    snprintf(path_buf, sizeof(path_buf), "%s/memory.max", child_dir);
    if (write_control_file(path_buf, "536870912\n") < 0) {
        perror("Не вдалося встановити memory.max");
        return EXIT_FAILURE;
    }

    /* 4. Встановлення ліміту CPU (квота 50 мс на період 100 мс = 0.5 ядра CPU) */
    snprintf(path_buf, sizeof(path_buf), "%s/cpu.max", child_dir);
    if (write_control_file(path_buf, "50000 100000\n") < 0) {
        perror("Не вдалося встановити cpu.max");
        return EXIT_FAILURE;
    }

    /* 5. Додавання поточного процесу у cgroup.procs */
    snprintf(path_buf, sizeof(path_buf), "%s/cgroup.procs", child_dir);
    char pid_str[32];
    snprintf(pid_str, sizeof(pid_str), "%d\n", getpid());
    if (write_control_file(path_buf, pid_str) < 0) {
        perror("Не вдалося додати PID у cgroup.procs");
        return EXIT_FAILURE;
    }

    printf("Процес C [PID %d] успішно додано до %s\n", getpid(), child_dir);

    /* 6. Очікування подій зміни стану cgroup через poll() */
    snprintf(path_buf, sizeof(path_buf), "%s/cgroup.events", child_dir);
    int ev_fd = open(path_buf, O_RDONLY);
    if (ev_fd >= 0) {
        struct pollfd pfd = { .fd = ev_fd, .events = POLLPRI | POLLERR, .revents = 0 };
        printf("Моніторинг cgroup.events (таймаут 1000 мс)...\n");
        poll(&pfd, 1, 1000);
        close(ev_fd);
    }

    return EXIT_SUCCESS;
}
