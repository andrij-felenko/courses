#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sched.h>
#include <sys/mman.h>
#include <x86intrin.h>

#define PAGE_SIZE 4096
#define PROBE_ENTRIES 256
#define CALIBRATION_ROUNDS 2000

/* Виділення пам'яті для масиву-зонда */
static uint8_t probe_array[PROBE_ENTRIES * PAGE_SIZE];

/* Точне вимірювання затримки читання пам'яті в тактах CPU */
static inline uint64_t measure_access_time(volatile void *addr) {
    uint32_t aux;
    uint64_t start_tsc, end_tsc;

    /* Серіалізація конвеєра перед початком вимірювання */
    _mm_lfence();
    start_tsc = __rdtscp(&aux);
    _mm_lfence();

    /* Зчитування цільової адреси пам'яті */
    (void)*(volatile uint8_t *)addr;

    /* Серіалізація конвеєра після завершення завантаження даних */
    _mm_lfence();
    end_tsc = __rdtscp(&aux);
    _mm_lfence();

    return end_tsc - start_tsc;
}

/* Примусове витіснення лінії пам'яті з усіх рівнів кешу */
static inline void flush_memory_line(volatile void *addr) {
    _mm_clflush((const void *)addr);
}

/* Автоматичне калібрування оптимального порогу відсікання Hit/Miss */
static uint64_t calibrate_timing_threshold(void) {
    uint64_t hit_total = 0;
    uint64_t miss_total = 0;
    volatile uint8_t *test_addr = &probe_array[0];

    /* Попередній прогрів сторінки для уникнення затримок Page Fault */
    *test_addr = 0xAA;

    for (int i = 0; i < CALIBRATION_ROUNDS; ++i) {
        /* Замір часу доступу до кешованої лінії (Hit) */
        (void)*test_addr;
        _mm_lfence();
        hit_total += measure_access_time(test_addr);

        /* Замір часу доступу після витіснення (Miss) */
        flush_memory_line(test_addr);
        _mm_mfence();
        miss_total += measure_access_time(test_addr);
    }

    uint64_t hit_avg = hit_total / CALIBRATION_ROUNDS;
    uint64_t miss_avg = miss_total / CALIBRATION_ROUNDS;

    printf("[Калібрування] Середній Hit: %lu тактів, Середній Miss: %lu тактів\n",
           hit_avg, miss_avg);

    /* Поріг як зважене середнє між піками */
    return (hit_avg + miss_avg) / 2;
}

int main(void) {
    /* Прив'язка процесу до нульового ядра для усунення дрижання планувальника */
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset);
    sched_setaffinity(0, sizeof(cpu_set_t), &cpuset);

    /* Ініціалізація та розгортання сторінок у фізичну пам'ять */
    memset(probe_array, 0x55, sizeof(probe_array));

    uint64_t threshold = calibrate_timing_threshold();
    printf("[Ініціалізація] Встановлено поріг виявлення: %lu тактів\n\n", threshold);

    /* 1. Фаза FLUSH: очищення всіх 256 контрольних сторінок */
    for (int i = 0; i < PROBE_ENTRIES; ++i) {
        flush_memory_line(&probe_array[i * PAGE_SIZE]);
    }
    _mm_mfence();

    /* 2. Імітація дії жертви: доступ до комірки з секретним індексом */
    uint8_t secret_value = 187; /* Секретне значення, що вивчається */
    volatile uint8_t *victim_target = &probe_array[secret_value * PAGE_SIZE];
    (void)*victim_target; /* Жертва звертається до пам'яті */

    _mm_mfence();

    /* 3. Фаза RELOAD: вимірювання часу доступу до всіх 256 сторінок */
    int detected_value = -1;
    uint64_t min_latency = UINT64_MAX;

    for (int i = 0; i < PROBE_ENTRIES; ++i) {
        volatile void *target = &probe_array[i * PAGE_SIZE];
        uint64_t latency = measure_access_time(target);

        if (latency < threshold && latency < min_latency) {
            min_latency = latency;
            detected_value = i;
        }
    }

    if (detected_value != -1) {
        printf("[Успіх] Відновлено значення секрету: %d (затримка: %lu тактів)\n",
               detected_value, min_latency);
    } else {
        printf("[Помилка] Секрет не виявлено (усі лінії дали Miss)\n");
    }

    return 0;
}
