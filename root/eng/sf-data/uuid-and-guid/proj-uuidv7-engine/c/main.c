#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <time.h>

#if defined(_WIN32)
#include <windows.h>
#include <bcrypt.h>
#pragma comment(lib, "bcrypt.lib")
#else
#include <sys/random.h>
#endif

typedef struct {
    uint8_t bytes[16];
} uuid_t;

/* Структура Windows GUID для демонстрації конвертації */
typedef struct {
    uint32_t Data1;
    uint16_t Data2;
    uint16_t Data3;
    uint8_t  Data4[8];
} win_guid_t;

/* Заповнення буфера криптографічно стійкими випадковими байтами */
static bool get_crypto_random(uint8_t *buf, size_t len) {
#if defined(_WIN32)
    return BCryptGenRandom(NULL, buf, (ULONG)len, BCRYPT_USE_SYSTEM_PREFERRED_RNG) == 0;
#else
    return getrandom(buf, len, 0) == (ssize_t)len;
#endif
}

/* Отримання поточного Unix-часу в мілісекундах */
static uint64_t get_unix_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return ((uint64_t)ts.tv_sec * 1000ULL) + ((uint64_t)ts.tv_nsec / 1000000ULL);
}

/* Генерація UUIDv7 зі збереженням монотонності */
bool uuid_generate_v7(uuid_t *out) {
    static uint64_t last_ms = 0;
    static uint16_t seq_counter = 0;

    if (!get_crypto_random(out->bytes, 16)) {
        return false;
    }

    uint64_t ms = get_unix_time_ms();

    /* Якщо час не змінився — інкрементуємо субмілісекундний лічильник */
    if (ms == last_ms) {
        seq_counter = (seq_counter + 1) & 0x0FFF; /* 12 бітів */
    } else {
        last_ms = ms;
        /* Ініціалізуємо лічильник випадковими 12 бітами для непередбачуваності */
        seq_counter = ((out->bytes[6] << 8) | out->bytes[7]) & 0x0FFF;
    }

    /* Байти 0..5: 48-бітний Unix timestamp (Big-Endian) */
    out->bytes[0] = (uint8_t)(ms >> 40);
    out->bytes[1] = (uint8_t)(ms >> 32);
    out->bytes[2] = (uint8_t)(ms >> 24);
    out->bytes[3] = (uint8_t)(ms >> 16);
    out->bytes[4] = (uint8_t)(ms >> 8);
    out->bytes[5] = (uint8_t)(ms);

    /* Байти 6..7: версія 0x7 + 12-бітний лічильник/ентропія */
    out->bytes[6] = 0x70 | (uint8_t)((seq_counter >> 8) & 0x0F);
    out->bytes[7] = (uint8_t)(seq_counter & 0xFF);

    /* Байт 8: варіант 0b10 (0x80) + випадкові біти */
    out->bytes[8] = (out->bytes[8] & 0x3F) | 0x80;

    return true;
}

/* Форматування у канонічний рядок 8-4-4-4-12 */
void uuid_to_string(const uuid_t *u, char out_str[37]) {
    snprintf(out_str, 37,
             "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
             u->bytes[0], u->bytes[1], u->bytes[2], u->bytes[3],
             u->bytes[4], u->bytes[5],
             u->bytes[6], u->bytes[7],
             u->bytes[8], u->bytes[9],
             u->bytes[10], u->bytes[11], u->bytes[12], u->bytes[13], u->bytes[14], u->bytes[15]);
}

/* Конвертація RFC 4122 / 9562 байтів у структуру Windows GUID */
void uuid_to_win_guid(const uuid_t *u, win_guid_t *g) {
    /* Little-Endian розпакування для перших трьох числових полів */
    g->Data1 = ((uint32_t)u->bytes[0] << 24) |
               ((uint32_t)u->bytes[1] << 16) |
               ((uint32_t)u->bytes[2] << 8)  |
               ((uint32_t)u->bytes[3]);
    g->Data2 = ((uint16_t)u->bytes[4] << 8)  | ((uint16_t)u->bytes[5]);
    g->Data3 = ((uint16_t)u->bytes[6] << 8)  | ((uint16_t)u->bytes[7]);
    memcpy(g->Data4, &u->bytes[8], 8);
}
