/*
 * Криптографічні ворота завантажувача: хеш тіла й підпис кореня довіри.
 * Пам'яті не виділяє; сторожовий таймер гладить сам.
 */
#ifndef RELEASE_IMAGE_VERIFY_H
#define RELEASE_IMAGE_VERIFY_H

#include "image_header.h"

typedef struct {
    /* Відкритий ключ релізу: сира непакована точка P-256, 65 байтів
       (0x04 || X || Y). Живе в захищеному секторі, а не в бандлі. */
    const uint8_t *root_pubkey;
    size_t         root_pubkey_len;

    /* Гладити IWDG між блоками хешування; NULL — якщо таймера немає. */
    void (*watchdog_kick)(void *user);
    void  *watchdog_user;
} release_verify_ctx_t;

/*
 * Повний прохід: структура → хеш тіла → підпис. Повертає RELEASE_OK лише
 * тоді, коли пройшли всі троє; out_header можна не запитувати (NULL).
 */
release_status_t release_verify_image(const release_verify_ctx_t *ctx,
                                      const uint8_t *image,
                                      size_t image_len,
                                      uint32_t active_counter,
                                      uint32_t max_payload,
                                      const release_header_t **out_header);

#endif /* RELEASE_IMAGE_VERIFY_H */
