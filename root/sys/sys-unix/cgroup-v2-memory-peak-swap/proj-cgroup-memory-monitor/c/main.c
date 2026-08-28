#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/epoll.h>
#include <errno.h>

#define CGROUP_PATH "/sys/fs/cgroup/test_memcg"
#define MAX_EVENTS 5
#define BUFFER_SIZE 1024

static int write_cgroup_file(const char *subpath, const char *value) {
    char fullpath[256];
    snprintf(fullpath, sizeof(fullpath), "%s/%s", CGROUP_PATH, subpath);
    
    int fd = open(fullpath, O_WRONLY);
    if (fd < 0) {
        perror("open for write failed");
        return -1;
    }
    
    ssize_t len = strlen(value);
    if (write(fd, value, len) != len) {
        perror("write to cgroup file failed");
        close(fd);
        return -1;
    }
    
    close(fd);
    return 0;
}

static void read_and_print_file(const char *subpath, const char *label) {
    char fullpath[256];
    char buf[BUFFER_SIZE];
    snprintf(fullpath, sizeof(fullpath), "%s/%s", CGROUP_PATH, subpath);
    
    int fd = open(fullpath, O_RDONLY);
    if (fd < 0) return;
    
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    if (bytes > 0) {
        buf[bytes] = '\0';
        printf("--- %s (%s) ---\n%s", label, subpath, buf);
    }
    close(fd);
}

int main(void) {
    // 1. Створення каталогу cgroup
    if (mkdir(CGROUP_PATH, 0755) < 0 && errno != EEXIST) {
        perror("mkdir cgroup failed");
        return EXIT_FAILURE;
    }
    printf("Cgroup створено: %s\n", CGROUP_PATH);

    // 2. Налаштування memory.high (50MB) та memory.max (100MB)
    if (write_cgroup_file("memory.high", "52428800") < 0 ||
        write_cgroup_file("memory.max", "104857600") < 0) {
        fprintf(stderr, "Помилка встановлення лімітів пам'яті\n");
        return EXIT_FAILURE;
    }

    // 3. Відкриття memory.events для моніторингу через epoll
    char events_path[256];
    snprintf(events_path, sizeof(events_path), "%s/memory.events", CGROUP_PATH);
    int events_fd = open(events_path, O_RDONLY | O_NONBLOCK);
    if (events_fd < 0) {
        perror("open memory.events failed");
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) {
        perror("epoll_create1 failed");
        close(events_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    ev.events = EPOLLPRI | EPOLLERR;
    ev.data.fd = events_fd;
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, events_fd, &ev) < 0) {
        perror("epoll_ctl failed");
        close(epoll_fd);
        close(events_fd);
        return EXIT_FAILURE;
    }

    printf("Монітор запущено. Очікування подій cgroup memory...\n");

    // 4. Цикл очікування подій
    struct epoll_event ready_events[MAX_EVENTS];
    int n = epoll_wait(epoll_fd, ready_events, MAX_EVENTS, 5000); // 5 секунд таймаут
    if (n < 0) {
        perror("epoll_wait failed");
    } else if (n == 0) {
        printf("Таймаут очікування подій. Опитування поточних показників:\n");
    } else {
        printf("Отримано сповіщення про зміну memory.events!\n");
    }

    // Зчитуємо та показуємо поточний стан
    read_and_print_file("memory.events", "Події пам'яті");
    read_and_print_file("memory.current", "Поточне споживання RAM");
    read_and_print_file("memory.peak", "Пікове споживання RAM");

    // Очищення ресурсів
    close(epoll_fd);
    close(events_fd);
    return EXIT_SUCCESS;
}
