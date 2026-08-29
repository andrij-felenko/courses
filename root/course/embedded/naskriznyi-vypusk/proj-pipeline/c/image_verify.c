#include "image_verify.h"

#include <string.h>

#include <mbedtls/bignum.h>
#include <mbedtls/ecdsa.h>
#include <mbedtls/ecp.h>
#include <mbedtls/sha256.h>

/* Хешуємо блоками: 256 КіБ одним викликом — це десятки мілісекунд,
   за які сторожовий таймер устигає перезавантажити пристрій. */
#define HASH_CHUNK 4096u

static void kick(const release_verify_ctx_t *ctx)
{
    if (ctx->watchdog_kick != NULL) {
        ctx->watchdog_kick(ctx->watchdog_user);
    }
}

static int sha256_chunked(mbedtls_sha256_context *sha,
                          const uint8_t *data,
                          size_t len,
                          const release_verify_ctx_t *ctx)
{
    size_t offset = 0u;
    while (offset < len) {
        size_t take = len - offset;
        if (take > HASH_CHUNK) {
            take = HASH_CHUNK;
        }
        int rc = mbedtls_sha256_update(sha, data + offset, take);
        if (rc != 0) {
            return rc;
        }
        offset += take;
        kick(ctx);
    }
    return 0;
}

/* Порівняння за сталий час: звичайний memcmp вертається на першому
   розбіжному байті й тим підказує зловмиснику, скільки він угадав. */
static int equal_const_time(const uint8_t *a, const uint8_t *b, size_t len)
{
    uint8_t diff = 0u;
    for (size_t i = 0u; i < len; ++i) {
        diff |= (uint8_t)(a[i] ^ b[i]);
    }
    return diff == 0u;
}

static release_status_t digest_payload(const release_verify_ctx_t *ctx,
                                       const uint8_t *payload,
                                       size_t payload_len,
                                       uint8_t out[RELEASE_DIGEST_SIZE])
{
    mbedtls_sha256_context sha;
    mbedtls_sha256_init(&sha);
    release_status_t status = RELEASE_ERR_CRYPTO;

    if (mbedtls_sha256_starts(&sha, 0) == 0
        && sha256_chunked(&sha, payload, payload_len, ctx) == 0
        && mbedtls_sha256_finish(&sha, out) == 0) {
        status = RELEASE_OK;
    }

    mbedtls_sha256_free(&sha);
    return status;
}

static release_status_t digest_signed_area(const release_verify_ctx_t *ctx,
                                           const uint8_t *image,
                                           size_t payload_len,
                                           uint8_t out[RELEASE_DIGEST_SIZE])
{
    mbedtls_sha256_context sha;
    mbedtls_sha256_init(&sha);
    release_status_t status = RELEASE_ERR_CRYPTO;

    /* Підписано заголовок разом із тілом: інакше підписане тіло можна було б
       підставити під чужий заголовок і збити маску чи лічильник відкату. */
    if (mbedtls_sha256_starts(&sha, 0) == 0
        && mbedtls_sha256_update(&sha, image, RELEASE_SIGNED_PREFIX) == 0
        && sha256_chunked(&sha, image + RELEASE_HEADER_SIZE, payload_len, ctx) == 0
        && mbedtls_sha256_finish(&sha, out) == 0) {
        status = RELEASE_OK;
    }

    mbedtls_sha256_free(&sha);
    return status;
}

static release_status_t verify_signature(const release_verify_ctx_t *ctx,
                                         const uint8_t digest[RELEASE_DIGEST_SIZE],
                                         const uint8_t signature[RELEASE_SIGNATURE_SIZE])
{
    mbedtls_ecp_group grp;
    mbedtls_ecp_point pub;
    mbedtls_mpi r;
    mbedtls_mpi s;

    mbedtls_ecp_group_init(&grp);
    mbedtls_ecp_point_init(&pub);
    mbedtls_mpi_init(&r);
    mbedtls_mpi_init(&s);

    release_status_t status = RELEASE_ERR_CRYPTO;

    do {
        if (ctx->root_pubkey == NULL || ctx->root_pubkey_len != 65u) {
            break;
        }
        if (mbedtls_ecp_group_load(&grp, MBEDTLS_ECP_DP_SECP256R1) != 0) {
            break;
        }
        if (mbedtls_ecp_point_read_binary(&grp, &pub,
                                          ctx->root_pubkey,
                                          ctx->root_pubkey_len) != 0) {
            break;
        }
        /* Точка не з кривої — це вже не «поганий підпис», а зіпсований
           корінь довіри: без перевірки далі буде обчислення в нікуди. */
        if (mbedtls_ecp_check_pubkey(&grp, &pub) != 0) {
            break;
        }
        /* HSM віддає сирі r||s по 32 байти, без обгортки ASN.1. */
        if (mbedtls_mpi_read_binary(&r, signature, 32u) != 0
            || mbedtls_mpi_read_binary(&s, signature + 32u, 32u) != 0) {
            break;
        }

        kick(ctx); /* сама перевірка ECDSA теж триває мілісекунди */

        status = (mbedtls_ecdsa_verify(&grp, digest, RELEASE_DIGEST_SIZE,
                                       &pub, &r, &s) == 0)
                 ? RELEASE_OK
                 : RELEASE_ERR_SIGNATURE;
    } while (0);

    mbedtls_mpi_free(&s);
    mbedtls_mpi_free(&r);
    mbedtls_ecp_point_free(&pub);
    mbedtls_ecp_group_free(&grp);
    return status;
}

release_status_t release_verify_image(const release_verify_ctx_t *ctx,
                                      const uint8_t *image,
                                      size_t image_len,
                                      uint32_t active_counter,
                                      uint32_t max_payload,
                                      const release_header_t **out_header)
{
    if (ctx == NULL) {
        return RELEASE_ERR_CRYPTO;
    }
    if (out_header != NULL) {
        *out_header = NULL;
    }

    const release_header_t *hdr = NULL;
    release_status_t status = release_header_parse(image, image_len,
                                                   active_counter, max_payload,
                                                   &hdr);
    if (status != RELEASE_OK) {
        return status;
    }

    const uint8_t *payload = image + RELEASE_HEADER_SIZE;
    const size_t payload_len = (size_t)hdr->payload_size;

    kick(ctx); /* далі йде рахунок, під час якого таймер лишається без уваги */

    uint8_t digest[RELEASE_DIGEST_SIZE];
    status = digest_payload(ctx, payload, payload_len, digest);
    if (status != RELEASE_OK) {
        return status;
    }
    if (!equal_const_time(digest, hdr->payload_sha256, RELEASE_DIGEST_SIZE)) {
        return RELEASE_ERR_DIGEST;
    }

    status = digest_signed_area(ctx, image, payload_len, digest);
    if (status != RELEASE_OK) {
        return status;
    }

    status = verify_signature(ctx, digest, hdr->signature);
    if (status != RELEASE_OK) {
        return status;
    }

    if (out_header != NULL) {
        *out_header = hdr;
    }
    return RELEASE_OK;
}
