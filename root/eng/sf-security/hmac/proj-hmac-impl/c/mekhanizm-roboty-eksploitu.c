#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* Функція створення підробленого гешу продовженням стану */
void length_extension_attack_sha256(
    const uint8_t original_hash[32],
    size_t original_total_len,  /* Довжина Key || Message */
    const uint8_t *extension_data,
    size_t extension_len,
    uint8_t forged_hash[32],
    uint8_t *forged_msg,
    size_t *forged_msg_len)
{
    /* 1. Обчислення оригінального padding для Key || Message */
    uint8_t pad[128] = {0};
    pad[0] = 0x80;
    size_t rem = original_total_len % 64;
    size_t pad_len = (rem < 56) ? (56 - rem) : (120 - rem);
    uint64_t bitlen = original_total_len * 8;
    for (int i = 0; i < 8; i++) {
        pad[pad_len + 7 - i] = (uint8_t)(bitlen >> (i * 8));
    }
    size_t total_pad_bytes = pad_len + 8;

    /* 2. Відновлення 8 регістрів стану з перехопленого 32-байтного гешу */
    sha256_ctx_t forged_ctx;
    for (int i = 0; i < 8; i++) {
        forged_ctx.state[i] = ((uint32_t)original_hash[i * 4] << 24) |
                              ((uint32_t)original_hash[i * 4 + 1] << 16) |
                              ((uint32_t)original_hash[i * 4 + 2] << 8) |
                              ((uint32_t)original_hash[i * 4 + 3]);
    }
    /* Лічильник встановлюється так, ніби початкові блоки вже оброблено */
    forged_ctx.count = original_total_len + total_pad_bytes;

    /* 3. Продовження гешування шкідливим хвостом */
    sha256_update(&forged_ctx, extension_data, extension_len);
    sha256_final(&forged_ctx, forged_hash);

    /* 4. Формування тіла сфальсифікованого повідомлення (без ключа) */
    memcpy(forged_msg, pad, total_pad_bytes);
    memcpy(forged_msg + total_pad_bytes, extension_data, extension_len);
    *forged_msg_len = total_pad_bytes + extension_len;
}
