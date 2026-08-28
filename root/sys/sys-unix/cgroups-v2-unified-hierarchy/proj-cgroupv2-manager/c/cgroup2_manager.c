/* cgroup2_manager.c — Програмне керування cgroups v2 мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/epoll.h>
#include <sys/vfs.h>
#include <errno.h>

#define CGROUP_ROOT "/sys/fs/cgroup"
#define CGROUP_MAGIC 0x63677232 /* CGROUP2_SUPER_MAGIC */

/* Допоміжна функція відкриття та запису у файли керування cgroup */
static int write_file(const char *path, const char *val) {
    int fd = open(path, O_WRONLY | O_CLOEXEC);
    if (fd < 0) {
        perror("open failed");
        return -1;
    }
    ssize_t len = strlen(val);
    if (write(fd, val, len) != len) {
        perror("write failed");
        close(fd);
        return -1;
    }
    close(fd);
    return 0;
}

int main(void) {
    struct statfs st;
    if (statfs(CGROUP_ROOT, &st) != 0 || st.f_type != CGROUP_MAGIC) {
        fprintf(stderr, "Помилка: %s не є змонтованою cgroup2\n", CGROUP_ROOT);
        return EXIT_FAILURE;
    }

    /* 1. Створення батьківської cgroup */
    if (mkdir(CGROUP_ROOT "/myapp", 0755) != 0 && errno != EEXIST) {
        perror("mkdir myapp failed");
        return EXIT_FAILURE;
    }

    /* 2. Активація контролерів для дочірніх груп */
    if (write_file(CGROUP_ROOT "/myapp/cgroup.subtree_control", "+memory +cpu") != 0) {
        fprintf(stderr, "Не вдалося увімкнути контролери у subtree_control\n");
        return EXIT_FAILURE;
    }

    /* 3. Створення листової cgroup для процесів */
    if (mkdir(CGROUP_ROOT "/myapp/leaf", 0755) != 0 && errno != EEXIST) {
        perror("mkdir leaf failed");
        return EXIT_FAILURE;
    }

    /* 4. Встановлення ліміту пам'яті (256 МіБ) та квоти CPU (50% одного ядра) */
    if (write_file(CGROUP_ROOT "/myapp/leaf/memory.max", "268435456") != 0 ||
        write_file(CGROUP_ROOT "/myapp/leaf/cpu.max", "50000 100000") != 0) {
        fprintf(stderr, "Не вдалося встановити ресурсні ліміти\n");
        return EXIT_FAILURE;
    }

    /* 5. Переміщення поточного процесу у листовий вузол */
    char pid_str[32];
    snprintf(pid_str, sizeof(pid_str), "%d", getpid());
    if (write_file(CGROUP_ROOT "/myapp/leaf/cgroup.procs", pid_str) != 0) {
        fprintf(stderr, "Не вдалося перемістити процес у cgroup.procs\n");
        return EXIT_FAILURE;
    }

    printf("Процес %d успішно переміщено в " CGROUP_ROOT "/myapp/leaf\n", getpid());

    /* 6. Реєстрація PSI сповіщення через epoll */
    int press_fd = open(CGROUP_ROOT "/myapp/leaf/memory.pressure", O_RDWR | O_CLOEXEC);
    if (press_fd >= 0) {
        /* Тригер: Деякі процеси заблоковані (some) понад 150мс за вікно 1с */
        const char *trigger = "some 150000 1000000";
        if (write(press_fd, trigger, strlen(trigger)) > 0) {
            int epfd = epoll_create1(EPOLL_CLOEXEC);
            struct epoll_event ev = { .events = EPOLLPRI, .data.fd = press_fd };
            epoll_ctl(epfd, EPOLL_CTL_ADD, press_fd, &ev);

            printf("Моніторинг PSI тиску пам'яті запущено...\n");
            struct epoll_event events[1];
            int nfds = epoll_wait(epfd, events, 1, 2000); /* чекаємо 2 секунди */
            if (nfds > 0) {
                printf("УВАГА: Отримано PSI сповіщення про брак пам'яті!\n");
            } else {
                printf("Тиск пам'яті у нормі.\n");
            }
            close(epfd);
        }
        close(press_fd);
    }

    return EXIT_SUCCESS;
}
