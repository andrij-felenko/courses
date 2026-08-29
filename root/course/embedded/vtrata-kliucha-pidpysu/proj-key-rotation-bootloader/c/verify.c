#include <string.h>

#include "mbedtls/bignum.h"
#include "mbedtls/ecdsa.h"
#include "mbedtls/ecp.h"
#include "mbedtls/memory_buffer_alloc.h"
#include "mbedtls/sha256.h"

#include "verify.h"

/*
 * Купи в завантажувачі немає, а mbedtls_ecdsa_verify() всередині заводить
 * великі числа через calloc(). Вихід — статичний пул: mbedTLS збирають із
 * MBEDTLS_MEMORY_BUFFER_ALLOC_C, і всі його виділення йдуть у цей масив.
 * 6 КБ вистачає для P-256 із запасом; переповнення пулу повертає помилку,
 * а не псує сусідні дані.
 */
static uint8_t g_crypto_arena[6144] __attribute__((aligned(8)));

void verify_init(void)
{
    mbedtls_memory_buffer_alloc_init(g_crypto_arena, sizeof(g_crypto_arena));
}

bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t size)
{
    uint8_t result = 0;

    for (size_t i = 0; i < size; ++i) {
        result |= (uint8_t)(a[i] ^ b[i]);
    }

    return result == 0;
}

/* SHA-256 над заголовком (без поля підпису) і тілом прошивки. */
static boot_status_t digest_image(const firmware_manifest_t *manifest,
                                  const uint8_t *payload,
                                  uint8_t out[SHA256_SIZE])
{
    mbedtls_sha256_context ctx;
    mbedtls_sha256_init(&ctx);

    boot_status_t status = BOOT_ERR_CRYPTO_ENGINE;

    if (mbedtls_sha256_starts(&ctx, 0) != 0) {
        goto cleanup;
    }
    /*
     * Заголовок мусить бути під підписом разом із тілом. Інакше зловмисник
     * бере старий вразливий образ із його ЧИННИМ підписом, підмінює в заголовку
     * security_version на більше число — і анти-відкат пропускає підробку.
     */
    if (mbedtls_sha256_update(&ctx, (const uint8_t *)manifest, MANIFEST_SIGNED_SIZE) != 0) {
        goto cleanup;
    }
    if (mbedtls_sha256_update(&ctx, payload, manifest->payload_length) != 0) {
        goto cleanup;
    }
    if (mbedtls_sha256_finish(&ctx, out) != 0) {
        goto cleanup;
    }

    status = BOOT_OK;

cleanup:
    mbedtls_sha256_free(&ctx);
    return status;
}

/* Перевірка ECDSA P-256 над готовим хешем. Ключ у маніфесті лежить як X||Y. */
static boot_status_t verify_signature(const uint8_t public_key[PUBKEY_SIZE],
                                      const uint8_t hash[SHA256_SIZE],
                                      const uint8_t signature[SIGNATURE_SIZE])
{
    mbedtls_ecp_group group;
    mbedtls_ecp_point point;
    mbedtls_mpi r;
    mbedtls_mpi s;
    uint8_t encoded_point[1 + PUBKEY_SIZE];  /* оголошуємо до першого goto */

    mbedtls_ecp_group_init(&group);
    mbedtls_ecp_point_init(&point);
    mbedtls_mpi_init(&r);
    mbedtls_mpi_init(&s);

    boot_status_t status = BOOT_ERR_CRYPTO_ENGINE;

    if (mbedtls_ecp_group_load(&group, MBEDTLS_ECP_DP_SECP256R1) != 0) {
        goto cleanup;
    }

    /* Нестиснена форма точки: 0x04 || X || Y. */
    encoded_point[0] = 0x04;
    memcpy(&encoded_point[1], public_key, PUBKEY_SIZE);

    if (mbedtls_ecp_point_read_binary(&group, &point,
                                      encoded_point, sizeof(encoded_point)) != 0) {
        status = BOOT_ERR_SIGNATURE_INVALID;
        goto cleanup;
    }
    /*
     * Точка мусить справді лежати на кривій і в потрібній підгрупі. Без цієї
     * перевірки підсунутий «ключ» поза кривою відкриває атаку невірної кривої.
     */
    if (mbedtls_ecp_check_pubkey(&group, &point) != 0) {
        status = BOOT_ERR_SIGNATURE_INVALID;
        goto cleanup;
    }

    if (mbedtls_mpi_read_binary(&r, signature, 32) != 0 ||
        mbedtls_mpi_read_binary(&s, signature + 32, 32) != 0) {
        goto cleanup;
    }

    if (mbedtls_ecdsa_verify(&group, hash, SHA256_SIZE, &point, &r, &s) != 0) {
        status = BOOT_ERR_SIGNATURE_INVALID;
        goto cleanup;
    }

    status = BOOT_OK;

cleanup:
    mbedtls_mpi_free(&s);
    mbedtls_mpi_free(&r);
    mbedtls_ecp_point_free(&point);
    mbedtls_ecp_group_free(&group);
    return status;
}

boot_status_t boot_verify_image(const firmware_manifest_t *manifest,
                                const uint8_t *payload,
                                const efuse_mirror_t *efuse)
{
    if (manifest == NULL || payload == NULL || efuse == NULL) {
        return BOOT_ERR_FLASH_READ;
    }

    const uint8_t slot = manifest->key_slot_index;
    if (slot >= BOOT_KEY_SLOTS) {
        return BOOT_ERR_INVALID_SLOT;
    }

    /* Крок 2. Відкликання: слот міг бути спалений після витоку ключа. */
    if ((efuse->revocation_bits & (1U << slot)) != 0U) {
        return BOOT_ERR_KEY_REVOKED;
    }

    /*
     * Крок 3. Корінь довіри: у перемички зашито не сам ключ, а його хеш —
     * 32 байти на слот замість 64, і ключ можна оновити, не міняючи залізо.
     */
    uint8_t key_digest[SHA256_SIZE];
    if (mbedtls_sha256(manifest->public_key, PUBKEY_SIZE, key_digest, 0) != 0) {
        return BOOT_ERR_CRYPTO_ENGINE;
    }
    if (!constant_time_memcmp(key_digest, efuse->root_key_digest[slot], SHA256_SIZE)) {
        return BOOT_ERR_ROOT_MISMATCH;
    }

    /* Крок 4. Анти-відкат: версія нижча за апаратний лічильник — образ мертвий. */
    if (manifest->security_version < efuse->monotonic_counter) {
        return BOOT_ERR_ROLLBACK_DETECTED;
    }

    /* Крок 5. Найдорожча перевірка — останньою, коли дешеві вже пройшли. */
    uint8_t image_digest[SHA256_SIZE];
    boot_status_t status = digest_image(manifest, payload, image_digest);
    if (status != BOOT_OK) {
        return status;
    }

    return verify_signature(manifest->public_key, image_digest, manifest->signature);
}
