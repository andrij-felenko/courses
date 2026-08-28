#include <stdint.h>
#include <string.h>

#define KEY_LEN   12          // ключ фіксованої довжини (доповнюємо нулями)
#define MAGIC     0xA5        // байт-початок: «тут починається запис»

// Один запис журналу. Порядок полів = порядок запису в пам'ять.
typedef struct {
    uint8_t  magic;           // 0xA5 — маркер початку запису
    uint8_t  key_len;         // реальна довжина ключа (≤ KEY_LEN)
    uint16_t val_len;         // довжина значення в байтах
    char     key[KEY_LEN];    // сам ключ, «хвіст» доповнено нулями
    // далі йдуть val_len байтів значення, а за ними — 4 байти CRC-32
} rec_hdr_t;

// Повний розмір запису на диску: заголовок + значення + печатка (CRC).
static uint32_t rec_size(uint16_t val_len) {
    return sizeof(rec_hdr_t) + val_len + sizeof(uint32_t);
}
