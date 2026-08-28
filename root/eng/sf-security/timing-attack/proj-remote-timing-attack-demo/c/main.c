#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <x86intrin.h>

#define TOKEN_LEN 16
#define SAMPLES_PER_BYTE 10000

/* Секретний токен сервера, прихований від клієнта */
static const uint8_t SECRET_TOKEN[TOKEN_LEN] = {
    0x53, 0x65, 0x63, 0x75, 0x72, 0x65, 0x50, 0x61,
    0x73, 0x73, 0x77, 0x6F, 0x72, 0x64, 0x34, 0x32
};

/* Штучне навантаження для імітації затримки порівняння */
static void work_delay(void) {
    volatile int dummy = 0;
    for (int i = 0; i < 50; ++i) {
        dummy += i;
    }
}

/* ВРАЗЛИВА функція перевірки: ранній вихід при першому неспівпадінні */
bool vulnerable_verify(const uint8_t *user_token, size_t len) {
    if (len != TOKEN_LEN) {
        return false;
    }
    for (size_t i = 0; i < TOKEN_LEN; ++i) {
        work_delay(); /* Імітація обробки байта */
        if (user_token[i] != SECRET_TOKEN[i]) {
            return false; /* Ранній вихід: витік часу! */
        }
    }
    return true;
}

/* ЗАХИЩЕНА функція перевірки: константний час виконання */
bool constant_time_verify(const uint8_t *user_token, size_t len) {
    if (len != TOKEN_LEN) {
        return false;
    }
    uint8_t diff = 0;
    for (size_t i = 0; i < TOKEN_LEN; ++i) {
        work_delay(); /* Однакове навантаження */
        diff |= (user_token[i] ^ SECRET_TOKEN[i]);
    }
    /* Компіляторний бар'єр проти оптимізації */
    __asm__ __volatile__("" : "+r"(diff) : : "memory");
    return (diff == 0);
}

/* Замір часу виконання в тактах процесора через rdtsc */
static inline uint64_t measure_cycles(const uint8_t *candidate, bool (*verify_fn)(const uint8_t*, size_t)) {
    unsigned int aux;
    _mm_lfence(); /* Бар'єр серіалізації інструкцій */
    uint64_t start = __rdtscp(&aux);
    _mm_lfence();

    volatile bool res = verify_fn(candidate, TOKEN_LEN);
    (void)res;

    _mm_lfence();
    uint64_t end = __rdtscp(&aux);
    _mm_lfence();

    return end - start;
}

/* Алгоритм атаки: побайтове відновлення секрету */
void run_timing_attack(bool (*verify_fn)(const uint8_t*, size_t), const char *target_name) {
    uint8_t recovered[TOKEN_LEN] = {0};
    printf("=== Запуск таймінг-атаки на: %s ===\n", target_name);

    for (size_t pos = 0; pos < TOKEN_LEN; ++pos) {
        uint64_t max_avg_cycles = 0;
        uint8_t best_byte = 0;

        for (int candidate = 0; candidate < 256; ++candidate) {
            recovered[pos] = (uint8_t)candidate;
            uint64_t total_cycles = 0;

            for (int s = 0; s < SAMPLES_PER_BYTE; ++s) {
                total_cycles += measure_cycles(recovered, verify_fn);
            }

            uint64_t avg = total_cycles / SAMPLES_PER_BYTE;
            if (avg > max_avg_cycles) {
                max_avg_cycles = avg;
                best_byte = (uint8_t)candidate;
            }
        }

        recovered[pos] = best_byte;
        printf("Позиція %02zu: знайдено байт 0x%02X ('%c') [сер. час: %lu тактів]\n",
               pos, best_byte, (best_byte >= 32 && best_byte <= 126) ? best_byte : '.', (unsigned long)max_avg_cycles);
    }

    printf("Відновлений рядок: \"");
    for (size_t i = 0; i < TOKEN_LEN; ++i) {
        printf("%c", recovered[i]);
    }
    printf("\"\n\n");
}

int main(void) {
    run_timing_attack(vulnerable_verify, "Вразливий алгоритм (Early-Exit)");
    return 0;
}
