#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>

#define PM_QOS_SYSFS_PATH "/dev/cpu_dma_latency"
#define CPUFREQ_GOV_PATH  "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
#define MSR_DEV_PATH      "/dev/cpu/0/msr"
#define IA32_PERF_STATUS  0x198

/* Запит на фіксацію максимальної затримки через PM QoS */
int set_pm_qos_latency(int32_t target_latency_us) {
    int fd = open(PM_QOS_SYSFS_PATH, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", PM_QOS_SYSFS_PATH, strerror(errno));
        return -1;
    }

    if (write(fd, &target_latency_us, sizeof(target_latency_us)) != sizeof(target_latency_us)) {
        fprintf(stderr, "Помилка запису в PM QoS: %s\n", strerror(errno));
        close(fd);
        return -1;
    }

    printf("[PM QoS] Успішно встановлено ліміт затримки: %d мкс (fd=%d)\n", target_latency_us, fd);
    return fd; /* Дескриптор має залишатися відкритим під час виконання роботи */
}

/* Зміна регулятора cpufreq через sysfs */
int set_cpufreq_governor(const char *governor_name) {
    int fd = open(CPUFREQ_GOV_PATH, O_WRONLY);
    if (fd < 0) {
        fprintf(stderr, "Помилка відкриття %s: %s\n", CPUFREQ_GOV_PATH, strerror(errno));
        return -1;
    }

    ssize_t len = strlen(governor_name);
    if (write(fd, governor_name, len) != len) {
        fprintf(stderr, "Помилка перемикання регулятора на %s: %s\n", governor_name, strerror(errno));
        close(fd);
        return -1;
    }

    close(fd);
    printf("[cpufreq] Встановлено регулятор: %s\n", governor_name);
    return 0;
}

/* Зчитати поточний множник частоти з MSR-регістра x86 */
int read_cpu_msr_ratio(void) {
    int fd = open(MSR_DEV_PATH, O_RDONLY);
    if (fd < 0) {
        /* Припускаємо, що модуль msr не завантажено або немає привілеїв root */
        return -1;
    }

    uint64_t msr_val = 0;
    if (pread(fd, &msr_val, sizeof(msr_val), IA32_PERF_STATUS) != sizeof(msr_val)) {
        close(fd);
        return -1;
    }

    close(fd);
    uint32_t ratio = (msr_val >> 8) & 0xFF;
    return (int)ratio;
}

int main(void) {
    printf("=== Налаштування параметрів живлення та затримок CPU (C API) ===\n");

    /* 1. Встановлюємо регулятор performance */
    if (set_cpufreq_governor("performance") != 0) {
        fprintf(stderr, "Увага: не вдалося змінити регулятор. Перевірте права root.\n");
    }

    /* 2. Блокуємо C-стани через PM QoS (затримка 0 мкс) */
    int qos_fd = set_pm_qos_latency(0);
    if (qos_fd < 0) {
        fprintf(stderr, "Не вдалося заблокувати затримку через PM QoS.\n");
        return EXIT_FAILURE;
    }

    /* 3. Зчитуємо поточний апаратний множник */
    int ratio = read_cpu_msr_ratio();
    if (ratio > 0) {
        printf("[MSR] Поточний множник частоти CPU: x%d\n", ratio);
    } else {
        printf("[MSR] Зчитування MSR недоступне (потрібно: modprobe msr).\n");
    }

    printf("Виконання критичної секції роботи з низькою затримкою...\n");
    sleep(2); /* Імітація роботи системи під навантаженням */

    /* Закриваємо дескриптор, звільняючи PM QoS */
    close(qos_fd);
    printf("[PM QoS] Ліміт затримки знято.\n");

    return EXIT_SUCCESS;
}
