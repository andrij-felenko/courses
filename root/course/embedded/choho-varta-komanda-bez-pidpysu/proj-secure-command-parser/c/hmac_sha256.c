#include "hmac_sha256.h"

#include <string.h>

#define IPAD 0x36U
#define OPAD 0x5cU

void hmac_sha256(const uint8_t *key, size_t key_len,
                 const uint8_t *msg, size_t msg_len,
                 uint8_t out[HMAC_SHA256_TAG_SIZE])
{
    uint8_t k0[SHA256_BLOCK_SIZE];
    uint8_t pad[SHA256_BLOCK_SIZE];
    uint8_t inner[SHA256_DIGEST_SIZE];
    Sha256Ctx ctx;

    /* K0: ключ, доведений рівно до розміру блоку. */
    memset(k0, 0, sizeof k0);
    if (key_len > SHA256_BLOCK_SIZE) {
        sha256(key, key_len, k0);      /* задовгий ключ згортаємо хешем */
    } else {
        memcpy(k0, key, key_len);
    }

    /* Внутрішній прохід: SHA256((K0 ^ ipad) || msg) */
    for (size_t i = 0; i < SHA256_BLOCK_SIZE; ++i) {
        pad[i] = (uint8_t)(k0[i] ^ IPAD);
    }
    sha256_init(&ctx);
    sha256_update(&ctx, pad, SHA256_BLOCK_SIZE);
    sha256_update(&ctx, msg, msg_len);
    sha256_final(&ctx, inner);

    /* Зовнішній прохід: SHA256((K0 ^ opad) || inner) */
    for (size_t i = 0; i < SHA256_BLOCK_SIZE; ++i) {
        pad[i] = (uint8_t)(k0[i] ^ OPAD);
    }
    sha256_init(&ctx);
    sha256_update(&ctx, pad, SHA256_BLOCK_SIZE);
    sha256_update(&ctx, inner, sizeof inner);
    sha256_final(&ctx, out);

    /* Усе, що торкалося ключа, лишається на стеку мережевого завдання —
     * і те саме місце стеку потім дістанеться іншому коду. Затираємо. */
    crypto_wipe(k0, sizeof k0);
    crypto_wipe(pad, sizeof pad);
    crypto_wipe(inner, sizeof inner);
}
