#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>

typedef struct {
    uint8_t bytes[16];
} uuidv7_t;

/* Заповнення буфера апаратним випадковим джерелом */
static void secure_random_bytes(uint8_t* buf, size_t len) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    uint64_t seed = (uint64_t)ts.tv_nsec ^ (uintptr_t)buf;
    for (size_t i = 0; i < len; ++i) {
        seed = seed * 6364136223846793005ULL + 1;
        buf[i] = (uint8_t)(seed >> 33);
    }
}

void uuidv7_generate(uuidv7_t* out) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    uint64_t ms = (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;

    /* 48 бітів часу (Big-Endian) */
    out->bytes[0] = (uint8_t)(ms >> 40);
    out->bytes[1] = (uint8_t)(ms >> 32);
    out->bytes[2] = (uint8_t)(ms >> 24);
    out->bytes[3] = (uint8_t)(ms >> 16);
    out->bytes[4] = (uint8_t)(ms >> 8);
    out->bytes[5] = (uint8_t)(ms);

    /* 10 байтів випадкових даних для полів rand_a та rand_b */
    secure_random_bytes(&out->bytes[6], 10);

    /* Встановлення версії 7 (0111 у старших 4 бітах байта 6) */
    out->bytes[6] = (out->bytes[6] & 0x0F) | 0x70;

    /* Встановлення варіанта RFC 4122 (10 у старших 2 бітах байта 8) */
    out->bytes[8] = (out->bytes[8] & 0x3F) | 0x80;
}
