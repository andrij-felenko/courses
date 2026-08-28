/* Демон супервізії сторожового таймера на мові C (Linux POSIX API) */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/watchdog.h>

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

/* Перевірка стану ресурсів системи */
static int check_system_health(void) {
    FILE *fp = fopen("/proc/meminfo", "r");
    if (!fp) {
        perror("Не вдалося відкрити /proc/meminfo");
        return -1;
    }

    long mem_total = 0, mem_available = 0;
    char line[128];
    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "MemTotal: %ld kB", &mem_total) == 1) continue;
        if (sscanf(line, "MemAvailable: %ld kB", &mem_available) == 1) continue;
    }
    fclose(fp);

    if (mem_total > 0 && mem_available > 0) {
        double free_ratio = (double)mem_available / (double)mem_total;
        /* Якщо доступної пам'яті менше 2%, вважаємо стан системи критичним */
        if (free_ratio < 0.02) {
            fprintf(stderr, "Критична нестача пам'яті: %.2f%% вільно\n", free_ratio * 100.0);
            return 0;
        }
    }
    return 1; /* Система здорова */
}

int main(int argc, char *argv[]) {
    const char *dev_path = (argc > 1) ? argv[1] : "/dev/watchdog";
    int req_timeout = 30; /* Таймаут 30 секунд */

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);

    int fd = open(dev_path, O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", dev_path, strerror(errno));
        return EXIT_FAILURE;
    }

    struct watchdog_info info;
    if (ioctl(fd, WDIOC_GETSUPPORT, &info) == 0) {
        printf("Watchdog: %s, прошивка: %u, опції: 0x%X\n",
               info.identity, info.firmware_version, info.options);
    }

    if (ioctl(fd, WDIOC_SETTIMEOUT, &req_timeout) == 0) {
        printf("Встановлено таймаут %d секунд\n", req_timeout);
    } else {
        perror("Не вдалося встановити таймаут через WDIOC_SETTIMEOUT");
    }

    int ping_interval = req_timeout / 2;
    if (ping_interval < 1) ping_interval = 1;
    printf("Розпочато моніторинг з інтервалом пінгу %d с...\n", ping_interval);

    while (g_running) {
        if (check_system_health()) {
            if (ioctl(fd, WDIOC_KEEPALIVE, 0) < 0) {
                perror("Помилка WDIOC_KEEPALIVE");
            } else {
                printf("[OK] Heartbeat надіслано в %s\n", dev_path);
            }
        } else {
            fprintf(stderr, "[WARN] Зупинка пингу через критичні метрики системи!\n");
        }
        sleep((unsigned int)ping_interval);
    }

    /* Штатне зупинення за допомогою Magic Close */
    printf("Штатне завершення: надсилання Magic Close 'V'...\n");
    const char magic_v = 'V';
    if (write(fd, &magic_v, 1) < 0) {
        perror("Помилка запису Magic Close");
    }

    close(fd);
    printf("Сторожовий таймер зупинено.\n");
    return EXIT_SUCCESS;
}
