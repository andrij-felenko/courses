#ifndef FIAT_SHAMIR_TRANSCRIPT_H
#define FIAT_SHAMIR_TRANSCRIPT_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define FS_STATE_BYTES 32
#define FS_LABEL_MAX_LEN 64

typedef enum {
    FS_SUCCESS = 0,
    FS_ERR_INVALID_PARAM = 1,
    FS_ERR_STATE_CORRUPTED = 2,
    FS_ERR_OUT_OF_ORDER = 3,
    FS_ERR_BUFFER_OVERFLOW = 4
} fiat_shamir_status_t;

typedef struct {
    uint8_t state[FS_STATE_BYTES]; /* Поточний хеш-стан (SHA-256 / BLAKE3 / Sponge) */
    uint64_t counter;              /* Лічильник згенерованих викликів */
    bool is_initialized;           /* Прапорець ініціалізації контексту */
} fiat_shamir_transcript_t;

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Ініціалізація транскрипту з розділювачем домену (Domain Separator).
 * @param ctx Вказівник на контекст транскрипту.
 * @param protocol_label Рядок ідентифікації протоколу (наприклад, "Schnorr-Ed25519-v1").
 * @return FS_SUCCESS у разі успіху.
 */
fiat_shamir_status_t fiat_shamir_init(
    fiat_shamir_transcript_t *ctx,
    const char *protocol_label
);

/**
 * @brief Поглинання повідомлення або комітменту в стан транскрипту (Absorb).
 * @param ctx Вказівник на контекст.
 * @param label Текстова мітка елемента (наприклад, "commitment_alpha").
 * @param data Послідовність байтів елемента.
 * @param len Довжина даних у байтах.
 * @return FS_SUCCESS у разі успіху.
 */
fiat_shamir_status_t fiat_shamir_absorb(
    fiat_shamir_transcript_t *ctx,
    const char *label,
    const uint8_t *data,
    size_t len
);

/**
 * @brief Генерація детермінованого виклику (Squeeze Challenge).
 * @param ctx Вказівник на контекст.
 * @param label Текстова мітка виклику (наприклад, "challenge_beta").
 * @param out_challenge Буфер для запису згенерованого виклику.
 * @param challenge_len Необхідний розмір виклику у байтах.
 * @return FS_SUCCESS у разі успіху.
 */
fiat_shamir_status_t fiat_shamir_squeeze(
    fiat_shamir_transcript_t *ctx,
    const char *label,
    uint8_t *out_challenge,
    size_t challenge_len
);

/**
 * @brief Скинути стан транскрипту та очистити секрети з пам'яті.
 * @param ctx Вказівник на контекст.
 */
void fiat_shamir_clear(fiat_shamir_transcript_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* FIAT_SHAMIR_TRANSCRIPT_H */
