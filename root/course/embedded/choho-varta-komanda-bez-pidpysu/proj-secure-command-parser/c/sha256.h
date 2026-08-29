#ifndef SHA256_H
#define SHA256_H

#include <stddef.h>
#include <stdint.h>

#define SHA256_DIGEST_SIZE 32U
#define SHA256_BLOCK_SIZE  64U

/*
 * Потокове SHA-256. Стан цілком лежить у структурі, яку заводить викликач:
 * ні malloc, ні статичних глобальних буферів — два завдання RTOS можуть
 * рахувати хеш одночасно, кожне зі своїм контекстом на власному стеку.
 */
typedef struct {
    uint32_t h[8];              /* поточний стан стиску                    */
    uint64_t total_len;         /* скільки байтів прийнято всього          */
    uint8_t  buf[SHA256_BLOCK_SIZE];
    size_t   buf_len;           /* недобраний хвіст до повного блоку 64 Б  */
} Sha256Ctx;

void sha256_init(Sha256Ctx *ctx);
void sha256_update(Sha256Ctx *ctx, const uint8_t *data, size_t len);
/* Завершує обчислення й затирає контекст: у ньому лишався б слід ключа. */
void sha256_final(Sha256Ctx *ctx, uint8_t out[SHA256_DIGEST_SIZE]);

void sha256(const uint8_t *data, size_t len, uint8_t out[SHA256_DIGEST_SIZE]);

/*
 * Затирання секретів через volatile-вказівник: звичайний memset компілятор
 * має право викинути як "запис у мертву змінну", і ключ лишиться на стеку.
 */
void crypto_wipe(void *p, size_t len);

#endif /* SHA256_H */
