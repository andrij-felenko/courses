#include "mbedtls/build_info.h"
#include "mbedtls/aes.h"
#include <string.h>

/* Увімкнено макрос MBEDTLS_AES_ALT у mbedtls_config.h */
#if defined(MBEDTLS_AES_ALT)

/* Базова адреса регістрів апаратного криптомодуля AES SoC */
#define HW_AES_BASE_ADDR      0x6000B000
#define HW_AES_REG_CTRL       (*(volatile uint32_t *)(HW_AES_BASE_ADDR + 0x00))
#define HW_AES_REG_START      (*(volatile uint32_t *)(HW_AES_BASE_ADDR + 0x04))
#define HW_AES_REG_STATUS     (*(volatile uint32_t *)(HW_AES_BASE_ADDR + 0x08))
#define HW_AES_TEXT_IN_ADDR   (HW_AES_BASE_ADDR + 0x10)
#define HW_AES_TEXT_OUT_ADDR  (HW_AES_BASE_ADDR + 0x30)

void mbedtls_aes_init(mbedtls_aes_context *ctx) {
    memset(ctx, 0, sizeof(mbedtls_aes_context));
}

void mbedtls_aes_free(mbedtls_aes_context *ctx) {
    if (ctx == NULL) return;
    memset(ctx, 0, sizeof(mbedtls_aes_context));
}

int mbedtls_aes_setkey_enc(mbedtls_aes_context *ctx, const unsigned char *key, unsigned int keybits) {
    if (keybits != 128 && keybits != 256) {
        return MBEDTLS_ERR_AES_INVALID_KEY_LENGTH;
    }
    ctx->rk = (uint32_t *)key;
    return 0;
}

int mbedtls_aes_crypt_ecb(mbedtls_aes_context *ctx, int mode,
                          const unsigned char input[16], unsigned char output[16]) {
    /* Копіювання вхідного блоку в регістри входу апаратного шифратора */
    memcpy((void *)HW_AES_TEXT_IN_ADDR, input, 16);

    /* Конфігурація режиму (0 - шифрування, 1 - розшифрування) та запуск */
    HW_AES_REG_CTRL = (mode == MBEDTLS_AES_ENCRYPT) ? 0x01 : 0x00;
    HW_AES_REG_START = 1;

    /* Очікування завершення обробки апаратним криптоблоком */
    while ((HW_AES_REG_STATUS & 0x01) == 0) {
        /* Очікування прапорця готовності апаратури */
    }

    /* Зчитування зашифрованого блоку з вихідних регістрів */
    memcpy(output, (void *)HW_AES_TEXT_OUT_ADDR, 16);
    return 0;
}
#endif /* MBEDTLS_AES_ALT */
