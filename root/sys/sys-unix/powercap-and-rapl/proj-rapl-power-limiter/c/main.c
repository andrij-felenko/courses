#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>
#include <signal.h>

#define RAPL_BASE_PATH "/sys/class/powercap/intel-rapl/intel-rapl:0"
#define BUFFER_SIZE 64

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

typedef struct {
    int fd_energy;
    int fd_limit;
    uint64_t max_range_uj;
    uint64_t prev_energy_uj;
    struct timespec prev_time;
} rapl_zone_t;

/* Отримання поточного монотонного часу у мікросекундах */
static inline uint64_t get_time_us(const struct timespec *ts) {
    return (uint64_t)ts->tv_sec * 1000000ULL + (uint64_t)ts->tv_nsec / 1000ULL;
}

/* Ініціалізація дескрипторів зони керування RAPL */
int rapl_zone_init(rapl_zone_t *zone, const char *base_path) {
    char path[256];
    char buf[BUFFER_SIZE];
    
    // 1. Зчитування діапазону переповнення
    snprintf(path, sizeof(path), "%s/max_energy_range_uj", base_path);
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття max_energy_range_uj");
        return -1;
    }
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (bytes <= 0) return -1;
    buf[bytes] = '\0';
    zone->max_range_uj = strtoull(buf, NULL, 10);

    // 2. Відкриття файлу енергії (потрібні права root / CAP_SYS_RAWIO)
    snprintf(path, sizeof(path), "%s/energy_uj", base_path);
    zone->fd_energy = open(path, O_RDONLY);
    if (zone->fd_energy < 0) {
        perror("Помилка відкриття energy_uj (потрібен запуск із sudo)");
        return -1;
    }

    // 3. Відкриття файлу встановлення ліміту PL1
    snprintf(path, sizeof(path), "%s/constraint_0_power_limit_uw", base_path);
    zone->fd_limit = open(path, O_WRONLY);
    if (zone->fd_limit < 0) {
        perror("Помилка відкриття constraint_0_power_limit_uw");
        close(zone->fd_energy);
        return -1;
    }

    // Початкове калібрувальне читання
    bytes = pread(zone->fd_energy, buf, sizeof(buf) - 1, 0);
    if (bytes > 0) {
        buf[bytes] = '\0';
        zone->prev_energy_uj = strtoull(buf, NULL, 10);
    }
    clock_gettime(CLOCK_MONOTONIC_RAW, &zone->prev_time);
    return 0;
}

/* Розрахунок середньої потужності за інтервал у ватах */
double rapl_read_power_watts(rapl_zone_t *zone) {
    char buf[BUFFER_SIZE];
    struct timespec now;
    
    ssize_t bytes = pread(zone->fd_energy, buf, sizeof(buf) - 1, 0);
    if (bytes <= 0) return -1.0;
    buf[bytes] = '\0';
    
    clock_gettime(CLOCK_MONOTONIC_RAW, &now);
    uint64_t curr_energy = strtoull(buf, NULL, 10);

    // Розрахунок дельти енергії з урахуванням переповнення
    uint64_t delta_energy;
    if (curr_energy >= zone->prev_energy_uj) {
        delta_energy = curr_energy - zone->prev_energy_uj;
    } else {
        delta_energy = curr_energy + zone->max_range_uj - zone->prev_energy_uj;
    }

    uint64_t time_prev_us = get_time_us(&zone->prev_time);
    uint64_t time_now_us = get_time_us(&now);
    uint64_t delta_time_us = time_now_us - time_prev_us;

    zone->prev_energy_uj = curr_energy;
    zone->prev_time = now;

    if (delta_time_us == 0) return 0.0;
    // Потужність: uJ / us = Watts
    return (double)delta_energy / (double)delta_time_us;
}

/* Встановлення апаратного ліміту PL1 у ватах */
int rapl_set_power_limit_watts(rapl_zone_t *zone, double watts) {
    char buf[BUFFER_SIZE];
    uint64_t limit_uw = (uint64_t)(watts * 1000000.0);
    
    int len = snprintf(buf, sizeof(buf), "%llu\n", (unsigned long long)limit_uw);
    ssize_t bytes = pwrite(zone->fd_limit, buf, len, 0);
    return (bytes == len) ? 0 : -1;
}

void rapl_zone_close(rapl_zone_t *zone) {
    if (zone->fd_energy >= 0) close(zone->fd_energy);
    if (zone->fd_limit >= 0) close(zone->fd_limit);
}

int main(int argc, char **argv) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    rapl_zone_t zone;
    if (rapl_zone_init(&zone, RAPL_BASE_PATH) < 0) {
        fprintf(stderr, "Ініціалізація RAPL не вдалася. Перевірте наявність модуля intel_rapl_msr.\n");
        return 1;
    }

    printf("Моніторинг RAPL запущено для %s (Апаратна ємність: %.2f Дж)\n",
           RAPL_BASE_PATH, (double)zone.max_range_uj / 1e6);

    // Встановлення тестового ліміту потужності 45.0 Вт
    if (rapl_set_power_limit_watts(&zone, 45.0) == 0) {
        printf("Успішно встановлено ліміт PL1 = 45.00 Вт\n");
    }

    while (g_running) {
        usleep(500000); // Період опитування 500 мс
        double power = rapl_read_power_watts(&zone);
        if (power >= 0.0) {
            printf("Поточне споживання сокета: %6.2f Вт\n", power);
        }
    }

    printf("\nЗавершення роботи. Закриття дескрипторів...\n");
    rapl_zone_close(&zone);
    return 0;
}
