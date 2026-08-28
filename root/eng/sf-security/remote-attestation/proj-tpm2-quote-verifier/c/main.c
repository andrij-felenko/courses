#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/sha.h>

#define TPM_GENERATED_VALUE 0xff544347
#define TPM_ST_ATTEST_QUOTE 0x8018
#define SHA256_DIGEST_LENGTH 32

/* Спрощена структура події логу завантаження */
typedef struct {
    uint32_t pcr_index;
    uint8_t digest[SHA256_DIGEST_LENGTH];
    char event_name[64];
} BootEvent;

/* Результат покрокової верифікації */
typedef struct {
    bool magic_valid;
    bool type_valid;
    bool nonce_valid;
    bool signature_valid;
    bool pcr_match;
} VerificationResult;

/* Функція симуляції розширення регістра PCR: PCR = SHA256(PCR || Digest) */
static void pcr_extend_sha256(uint8_t pcr[SHA256_DIGEST_LENGTH], const uint8_t event_digest[SHA256_DIGEST_LENGTH]) {
    uint8_t buffer[SHA256_DIGEST_LENGTH * 2];
    memcpy(buffer, pcr, SHA256_DIGEST_LENGTH);
    memcpy(buffer + SHA256_DIGEST_LENGTH, event_digest, SHA256_DIGEST_LENGTH);

    SHA256(buffer, sizeof(buffer), pcr);
}

/* Перевірка криптографічного підпису за допомогою OpenSSL EVP */
static bool verify_signature(EVP_PKEY *ak_pubkey, const uint8_t *data, size_t data_len,
                            const uint8_t *sig, size_t sig_len) {
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) return false;

    bool valid = false;
    if (EVP_DigestVerifyInit(ctx, NULL, EVP_sha256(), NULL, ak_pubkey) == 1) {
        if (EVP_DigestVerifyUpdate(ctx, data, data_len) == 1) {
            if (EVP_DigestVerifyFinal(ctx, sig, sig_len) == 1) {
                valid = true;
            }
        }
    }

    EVP_MD_CTX_free(ctx);
    return valid;
}

/* Головна функція аналізу цитати та журналу подій */
VerificationResult verify_tpm2_quote(
    const uint8_t *attest_buf, size_t attest_len,
    uint32_t magic, uint16_t type,
    const uint8_t *extra_data, size_t extra_data_len,
    const uint8_t *quoted_pcr_digest,
    const uint8_t *signature, size_t sig_len,
    EVP_PKEY *ak_pubkey,
    const uint8_t *expected_nonce, size_t nonce_len,
    const BootEvent *events, size_t event_count)
{
    VerificationResult res = {0};

    /* 1. Перевірка магічних констант заголовка */
    res.magic_valid = (magic == TPM_GENERATED_VALUE);
    res.type_valid = (type == TPM_ST_ATTEST_QUOTE);

    /* 2. Перевірка свіжості виклику (Nonce) */
    if (extra_data_len == nonce_len && memcmp(extra_data, expected_nonce, nonce_len) == 0) {
        res.nonce_valid = true;
    }

    /* 3. Перевірка цифрового підпису AK над бінарним буфером цитати */
    if (ak_pubkey && signature && sig_len > 0) {
        res.signature_valid = verify_signature(ak_pubkey, attest_buf, attest_len, signature, sig_len);
    }

    /* 4. Відтворення журналу подій для регістра PCR[0] */
    uint8_t simulated_pcr0[SHA256_DIGEST_LENGTH] = {0};
    for (size_t i = 0; i < event_count; i++) {
        if (events[i].pcr_index == 0) {
            pcr_extend_sha256(simulated_pcr0, events[i].digest);
        }
    }

    /* Порівняння відтвореного PCR[0] із підписаним значенням у цитаті */
    if (memcmp(simulated_pcr0, quoted_pcr_digest, SHA256_DIGEST_LENGTH) == 0) {
        res.pcr_match = true;
    }

    return res;
}
