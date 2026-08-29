#ifndef EOLBOOT_UNLOCK_H
#define EOLBOOT_UNLOCK_H

#include <stdint.h>

#include "hal.h"

#define CHALLENGE_NONCE_LEN 32u
#define SIGNATURE_LEN       64u
#define PUBLIC_KEY_LEN      32u

/* Підписується саме склейка Nonce || Chip_UUID */
#define CHALLENGE_MSG_LEN (CHALLENGE_NONCE_LEN + CHIP_UUID_LEN)

#define UNLOCK_SESSION_TIMEOUT_MS 120000u

typedef enum {
    UNLOCK_OK               = 0,
    UNLOCK_ERR_ALREADY      = 1, /* eFuse уже перепалено */
    UNLOCK_ERR_NO_SESSION   = 2, /* виклику не було */
    UNLOCK_ERR_TIMEOUT      = 3,
    UNLOCK_ERR_BAD_SIG      = 4,
    UNLOCK_ERR_FLASH        = 5, /* стирання NVS не завершилося */
    UNLOCK_ERR_EFUSE        = 6
} unlock_status_t;

/* Генерує Nonce у SRAM і повертає склейку Nonce || Chip_UUID для хоста */
void unlock_create_challenge(uint8_t out_msg[CHALLENGE_MSG_LEN]);

/* Верифікація підпису, стирання NVS і перепалювання eFuse — у цьому порядку */
unlock_status_t unlock_execute(const uint8_t signature[SIGNATURE_LEN]);

/* Гасить сесію, коли вийшов її час життя */
void unlock_tick(uint32_t now_ms);

const char *unlock_status_text(unlock_status_t status);

#endif /* EOLBOOT_UNLOCK_H */
