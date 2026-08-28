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

#define RAPL_PKG_PATH "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"
#define RAPL_CORE_PATH "/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj"
#define RAPL_DRAM_PATH "/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:2/energy_uj"

typedef struct {
    int fd_pkg;
    int fd_core;
    int fd_dram;
    uint64_t start_energy_pkg;
    uint64_t start_energy_core;
    uint64_t start_energy_dram;
    struct timespec start_time;
} rapl_meter_t;

typedef struct {
    double duration_sec;
    double energy_pkg_joules;
    double energy_core_joules;
    double energy_dram_joules;
    double power_pkg_watts;
    double power_core_watts;
    double power_dram_watts;
} rapl_result_t;

static int open_sensor(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0 && errno == EACCES) {
        fprintf(stderr, "Помилка доступу до %s: потрібні права root (sudo) через захист PLATYPUS.\n", path);
    }
    return fd;
}

static uint64_t read_energy_uj(int fd) {
    if (fd < 0) return 0;
    char buf[32];
    ssize_t bytes = pread(fd, buf, sizeof(buf) - 1, 0);
    if (bytes <= 0) return 0;
    buf[bytes] = '\0';
    return (uint64_t)strtoull(buf, NULL, 10);
}

bool rapl_meter_init(rapl_meter_t *meter) {
    memset(meter, 0, sizeof(*meter));
    meter->fd_pkg = open_sensor(RAPL_PKG_PATH);
    if (meter->fd_pkg < 0) {
        return false;
    }
    meter->fd_core = open_sensor(RAPL_CORE_PATH);
    meter->fd_dram = open_sensor(RAPL_DRAM_PATH);
    return true;
}

void rapl_meter_start(rapl_meter_t *meter) {
    meter->start_energy_pkg = read_energy_uj(meter->fd_pkg);
    meter->start_energy_core = read_energy_uj(meter->fd_core);
    meter->start_energy_dram = read_energy_uj(meter->fd_dram);
    clock_gettime(CLOCK_MONOTONIC, &meter->start_time);
}

void rapl_meter_stop(const rapl_meter_t *meter, rapl_result_t *res) {
    struct timespec end_time;
    clock_gettime(CLOCK_MONOTONIC, &end_time);

    uint64_t end_pkg = read_energy_uj(meter->fd_pkg);
    uint64_t end_core = read_energy_uj(meter->fd_core);
    uint64_t end_dram = read_energy_uj(meter->fd_dram);

    double sec = (double)(end_time.tv_sec - meter->start_time.tv_sec) +
                 (double)(end_time.tv_nsec - meter->start_time.tv_nsec) / 1e9;
    res->duration_sec = sec;

    // Обробка приросту з захистом від переповнення (sysfs віддає 64-бітне нормалізоване значення)
    uint64_t d_pkg = (end_pkg >= meter->start_energy_pkg) ? 
                     (end_pkg - meter->start_energy_pkg) : 0;
    uint64_t d_core = (end_core >= meter->start_energy_core) ? 
                      (end_core - meter->start_energy_core) : 0;
    uint64_t d_dram = (end_dram >= meter->start_energy_dram) ? 
                      (end_dram - meter->start_energy_dram) : 0;

    res->energy_pkg_joules = (double)d_pkg / 1e6;
    res->energy_core_joules = (double)d_core / 1e6;
    res->energy_dram_joules = (double)d_dram / 1e6;

    res->power_pkg_watts = (sec > 0.0) ? (res->energy_pkg_joules / sec) : 0.0;
    res->power_core_watts = (sec > 0.0) ? (res->energy_core_joules / sec) : 0.0;
    res->power_dram_watts = (sec > 0.0) ? (res->energy_dram_joules / sec) : 0.0;
}

void rapl_meter_close(rapl_meter_t *meter) {
    if (meter->fd_pkg >= 0) close(meter->fd_pkg);
    if (meter->fd_core >= 0) close(meter->fd_core);
    if (meter->fd_dram >= 0) close(meter->fd_dram);
}

// Тестове обчислювальне навантаження (множення масиву чисел з плаваючою комою)
static void compute_heavy_workload(size_t n) {
    volatile double acc = 1.0;
    for (size_t i = 1; i <= n; ++i) {
        acc = acc * 1.0000001 + (double)(i & 0xFF) * 0.00001;
    }
}

int main(void) {
    rapl_meter_t meter;
    if (!rapl_meter_init(&meter)) {
        fprintf(stderr, "Не вдалося ініціалізувати сенсори RAPL.\n");
        return 1;
    }

    printf("Вимірювання енергоспоживання обчислювального блоку...\n");
    rapl_meter_start(&meter);

    compute_heavy_workload(150000000);

    rapl_result_t res;
    rapl_meter_stop(&meter, &res);
    rapl_meter_close(&meter);

    printf("=== Результати вимірювання (C API) ===\n");
    printf("Час виконання:      %.4f с\n", res.duration_sec);
    printf("Енергія Package:    %.4f Дж  (Потужність: %.2f Вт)\n", res.energy_pkg_joules, res.power_pkg_watts);
    printf("Енергія Cores:      %.4f Дж  (Потужність: %.2f Вт)\n", res.energy_core_joules, res.power_core_watts);
    if (res.energy_dram_joules > 0.0) {
        printf("Енергія DRAM:       %.4f Дж  (Потужність: %.2f Вт)\n", res.energy_dram_joules, res.power_dram_watts);
    }
    return 0;
}
