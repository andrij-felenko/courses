/* decom_cert.c - Повна реалізація генератора та верифікатора сертифікатів на C99 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <errno.h>

#define CERT_MAGIC "SCERT100"
#define CERT_MAGIC_LEN 8
#define CERT_VERSION 0x0001
#define MAX_IDENT_LEN 32
#define HASH_LEN 32
#define SIGNATURE_LEN 32

/* Перелік методів санітизації згідно з NIST SP 800-88 */
typedef enum {
    SAN_METHOD_NONE                = 0x00,
    SAN_METHOD_OVERWRITE_SINGLE    = 0x01,
    SAN_METHOD_OVERWRITE_MULTI     = 0x02,
    SAN_METHOD_NVME_BLOCK_ERASE    = 0x03,
    SAN_METHOD_CRYPTO_ERASE        = 0x04,
    SAN_METHOD_PHYSICAL_SHRED      = 0x05
} sanitization_method_t;

/* Рівень санітизації */
typedef enum {
    NIST_LEVEL_UNKNOWN = 0x00,
    NIST_LEVEL_CLEAR   = 0x01,
    NIST_LEVEL_PURGE   = 0x02,
    NIST_LEVEL_DESTROY = 0x03
} nist_compliance_level_t;

/* Тип хімічного джерела струму */
typedef enum {
    BATTERY_CHEM_NONE      = 0x00,
    BATTERY_CHEM_LI_ION    = 0x01,
    BATTERY_CHEM_LIFEPO4   = 0x02,
    BATTERY_CHEM_LTO       = 0x03
} battery_chemistry_t;

/* Бінарна структура сертифіката санітизації (фіксований розмір) */
#pragma pack(push, 1)
typedef struct {
    uint8_t  magic[CERT_MAGIC_LEN];          /* 0x00: 'SCERT100' */
    uint16_t schema_version;                /* 0x08: 0x0001 */
    uint16_t reserved_flags;                /* 0x0A: Резерв */
    uint64_t timestamp_utc;                 /* 0x0C: Час створення (UNIX) */
    char     device_uid[MAX_IDENT_LEN];     /* 0x14: UID пристрою / плати */
    char     storage_serial[MAX_IDENT_LEN]; /* 0x34: Серійний номер Flash/SSD */
    uint8_t  sanitization_method;           /* 0x54: sanitization_method_t */
    uint8_t  nist_level;                    /* 0x55: nist_compliance_level_t */
    uint8_t  is_battery_removed;            /* 0x56: 1 якщо АКБ демонтовано */
    uint8_t  battery_chemistry;             /* 0x57: battery_chemistry_t */
    uint64_t erased_sectors_count;          /* 0x58: Кількість стертих секторів */
    uint8_t  pre_sanitize_hash[HASH_LEN];   /* 0x60: SHA-256 до очищення */
    uint8_t  post_check_passed;             /* 0x80: 1 якщо нулі підтверджено */
    uint8_t  pad[7];                        /* 0x81: Вирівнювання */
    char     technician_id[16];             /* 0x88: ID техніка або стенда */
    uint8_t  signature[SIGNATURE_LEN];      /* 0x98: HMAC-SHA256 підпис [0x00..0x97] */
} sanitization_certificate_t;
#pragma pack(pop)

/* Реалізація спрощеного вбудованого SHA-256 для демонстрації повної автономності */
typedef struct {
    uint32_t state[8];
    uint64_t count;
    uint8_t  buffer[64];
} sha256_ctx_t;

#define ROTR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTR(x, 2) ^ ROTR(x, 13) ^ ROTR(x, 22))
#define EP1(x) (ROTR(x, 6) ^ ROTR(x, 11) ^ ROTR(x, 25))
#define SIG0(x) (ROTR(x, 7) ^ ROTR(x, 18) ^ ((x) >> 3))
#define SIG1(x) (ROTR(x, 17) ^ ROTR(x, 19) ^ ((x) >> 10))

static const uint32_t K[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0bef9a3f,0xc67178f2
};

void sha256_init(sha256_ctx_t *ctx) {
    ctx->state[0] = 0x6a09e667; ctx->state[1] = 0xbb67ae85;
    ctx->state[2] = 0x3c6ef372; ctx->state[3] = 0xa54ff53a;
    ctx->state[4] = 0x510e527f; ctx->state[5] = 0x9b05688c;
    ctx->state[6] = 0x1f83d9ab; ctx->state[7] = 0x5be0cd19;
    ctx->count = 0;
}

static void sha256_transform(sha256_ctx_t *ctx, const uint8_t data[64]) {
    uint32_t a, b, c, d, e, f, g, h, i, t1, t2, m[64];
    for (i = 0; i < 16; ++i) {
        m[i] = ((uint32_t)data[i * 4] << 24) |
               ((uint32_t)data[i * 4 + 1] << 16) |
               ((uint32_t)data[i * 4 + 2] << 8) |
               ((uint32_t)data[i * 4 + 3]);
    }
    for (; i < 64; ++i) {
        m[i] = SIG1(m[i - 2]) + m[i - 7] + SIG0(m[i - 15]) + m[i - 16];
    }
    a = ctx->state[0]; b = ctx->state[1]; c = ctx->state[2]; d = ctx->state[3];
    e = ctx->state[4]; f = ctx->state[5]; g = ctx->state[6]; h = ctx->state[7];
    for (i = 0; i < 64; ++i) {
        t1 = h + EP1(e) + CH(e, f, g) + K[i] + m[i];
        t2 = EP0(a) + MAJ(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }
    ctx->state[0] += a; ctx->state[1] += b; ctx->state[2] += c; ctx->state[3] += d;
    ctx->state[4] += e; ctx->state[5] += f; ctx->state[6] += g; ctx->state[7] += h;
}

void sha256_update(sha256_ctx_t *ctx, const uint8_t *data, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        ctx->buffer[ctx->count % 64] = data[i];
        ctx->count++;
        if (ctx->count % 64 == 0) {
            sha256_transform(ctx, ctx->buffer);
        }
    }
}

void sha256_final(sha256_ctx_t *ctx, uint8_t hash[32]) {
    uint64_t total_bits = ctx->count * 8;
    ctx->buffer[ctx->count % 64] = 0x80;
    ctx->count++;
    if (ctx->count % 64 > 56) {
        while (ctx->count % 64 != 0) {
            ctx->buffer[ctx->count % 64] = 0x00;
            ctx->count++;
        }
        sha256_transform(ctx, ctx->buffer);
    }
    while (ctx->count % 64 < 56) {
        ctx->buffer[ctx->count % 64] = 0x00;
        ctx->count++;
    }
    for (int i = 7; i >= 0; --i) {
        ctx->buffer[56 + (7 - i)] = (uint8_t)((total_bits >> (i * 8)) & 0xFF);
    }
    sha256_transform(ctx, ctx->buffer);
    for (int i = 0; i < 8; ++i) {
        hash[i * 4]     = (uint8_t)((ctx->state[i] >> 24) & 0xFF);
        hash[i * 4 + 1] = (uint8_t)((ctx->state[i] >> 16) & 0xFF);
        hash[i * 4 + 2] = (uint8_t)((ctx->state[i] >> 8) & 0xFF);
        hash[i * 4 + 3] = (uint8_t)(ctx->state[i] & 0xFF);
    }
}

/* Обчислення HMAC-SHA256 над блоком даних */
void hmac_sha256(const uint8_t *key, size_t key_len,
                 const uint8_t *data, size_t data_len,
                 uint8_t out[32]) 
{
    uint8_t k_pad[64];
    uint8_t tk[32];
    memset(k_pad, 0, sizeof(k_pad));

    if (key_len > 64) {
        sha256_ctx_t tctx;
        sha256_init(&tctx);
        sha256_update(&tctx, key, key_len);
        sha256_final(&tctx, tk);
        memcpy(k_pad, tk, 32);
    } else {
        memcpy(k_pad, key, key_len);
    }

    uint8_t ipad[64], opad[64];
    for (int i = 0; i < 64; ++i) {
        ipad[i] = k_pad[i] ^ 0x36;
        opad[i] = k_pad[i] ^ 0x5C;
    }

    uint8_t inner_hash[32];
    sha256_ctx_t ictx;
    sha256_init(&ictx);
    sha256_update(&ictx, ipad, 64);
    sha256_update(&ictx, data, data_len);
    sha256_final(&ictx, inner_hash);

    sha256_ctx_t octx;
    sha256_init(&octx);
    sha256_update(&octx, opad, 64);
    sha256_update(&octx, inner_hash, 32);
    sha256_final(&octx, out);
}

/* Порівняння за сталий час для запобігання атакам за часом (Timing Attacks) */
static int constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t result = 0;
    for (size_t i = 0; i < len; ++i) {
        result |= (a[i] ^ b[i]);
    }
    return result;
}

/* Генерація та підпис сертифіката */
int generate_decommission_certificate(
    sanitization_certificate_t *cert,
    const char *device_uid,
    const char *storage_serial,
    sanitization_method_t method,
    nist_compliance_level_t nist_lvl,
    bool battery_removed,
    battery_chemistry_t chem,
    uint64_t erased_sectors,
    const char *tech_id,
    const uint8_t *secret_key,
    size_t key_len)
{
    if (!cert || !device_uid || !storage_serial || !tech_id || !secret_key) {
        return -EINVAL;
    }

    memset(cert, 0, sizeof(*cert));
    memcpy(cert->magic, CERT_MAGIC, CERT_MAGIC_LEN);
    cert->schema_version = CERT_VERSION;
    cert->timestamp_utc = (uint64_t)time(NULL);

    strncpy(cert->device_uid, device_uid, sizeof(cert->device_uid) - 1);
    strncpy(cert->storage_serial, storage_serial, sizeof(cert->storage_serial) - 1);
    strncpy(cert->technician_id, tech_id, sizeof(cert->technician_id) - 1);

    cert->sanitization_method = (uint8_t)method;
    cert->nist_level = (uint8_t)nist_lvl;
    cert->is_battery_removed = battery_removed ? 1 : 0;
    cert->battery_chemistry = (uint8_t)chem;
    cert->erased_sectors_count = erased_sectors;
    cert->post_check_passed = 1;

    /* Симуляція хешу випадкових секторів до очищення */
    for (int i = 0; i < HASH_LEN; ++i) {
        cert->pre_sanitize_hash[i] = (uint8_t)(i ^ 0xAA);
    }

    /* Розрахунок HMAC над тілом структури до поля signature */
    size_t payload_len = offsetof(sanitization_certificate_t, signature);
    hmac_sha256(secret_key, key_len, (const uint8_t *)cert, payload_len, cert->signature);

    return 0;
}

/* Верифікація сертифіката */
int verify_decommission_certificate(
    const sanitization_certificate_t *cert,
    const uint8_t *secret_key,
    size_t key_len)
{
    if (!cert || !secret_key) return -EINVAL;

    /* 1. Перевірка магічного заголовка */
    if (memcmp(cert->magic, CERT_MAGIC, CERT_MAGIC_LEN) != 0) {
        fprintf(stderr, "[ПОМИЛКА ВЕРИФІКАЦІЇ] Невірний заголовок Magic Signature.\n");
        return -EBADMSG;
    }

    /* 2. Перевірка версії схеми */
    if (cert->schema_version != CERT_VERSION) {
        fprintf(stderr, "[ПОМИЛКА ВЕРИФІКАЦІЇ] Непідтримувана версія схеми: 0x%04X\n", cert->schema_version);
        return -EPROTONOSUPPORT;
    }

    /* 3. Перевірка екологічного регламенту (EU) 2023/1542 */
    if (cert->battery_chemistry != BATTERY_CHEM_NONE && !cert->is_battery_removed) {
        fprintf(stderr, "[ПОМИЛКА ВЕРИФІКАЦІЇ] Порушення WEEE/EU-2023/1542: АКБ не демонтовано перед списанням!\n");
        return -EPERM;
    }

    /* 4. Перевірка статусу санітизації */
    if (!cert->post_check_passed || cert->erased_sectors_count == 0) {
        fprintf(stderr, "[ПОМИЛКА ВЕРИФІКАЦІЇ] Відсутнє підтвердження успішного занулення носія.\n");
        return -EINVAL;
    }

    /* 5. Перевірка криптографічного цифрового підпису */
    uint8_t expected_sig[SIGNATURE_LEN];
    size_t payload_len = offsetof(sanitization_certificate_t, signature);
    hmac_sha256(secret_key, key_len, (const uint8_t *)cert, payload_len, expected_sig);

    if (constant_time_memcmp(cert->signature, expected_sig, SIGNATURE_LEN) != 0) {
        fprintf(stderr, "[ПОМИЛКА ВЕРИФІКАЦІЇ] Цифровий підпис недійсний! Дані сертифіката сфальсифіковано.\n");
        return -EACCES;
    }

    return 0;
}

int main(void) {
    printf("=== ТЕСТУВАННЯ ГЕНЕРАТОРА ТА ВЕРИФІКАТОРА СЕРТИФІКАТІВ (C99) ===\n");
    const uint8_t hmac_secret[] = "MasterAuditSecretKey2026_NIST800-88";
    sanitization_certificate_t cert;

    /* Генерація валідного сертифіката */
    int res = generate_decommission_certificate(
        &cert,
        "IOT-GATEWAY-MAC-001A2B3C4D5E",
        "SAMSUNG-NVME-MZVLB512HAJQ-000",
        SAN_METHOD_CRYPTO_ERASE,
        NIST_LEVEL_PURGE,
        true,
        BATTERY_CHEM_LI_ION,
        1000215216ULL,
        "TECH-OPERATOR-77",
        hmac_secret,
        sizeof(hmac_secret) - 1
    );

    if (res == 0) {
        printf("[1] Сертифікат успішно згенеровано та підписано HMAC-SHA256.\n");
        printf("    • Пристрій: %s\n", cert.device_uid);
        printf("    • Носій:    %s\n", cert.storage_serial);
        printf("    • Метод:    Crypto-Erase (NIST Purge)\n");
        printf("    • АКБ:      Демонтовано (EU 2023/1542 Compliant)\n");
    }

    /* Верифікація оригінального сертифіката */
    res = verify_decommission_certificate(&cert, hmac_secret, sizeof(hmac_secret) - 1);
    if (res == 0) {
        printf("[2] Верифікація успішна: Сертифікат автентичний, цілісність підтверджено.\n");
    }

    /* Тест на виявлення підробки */
    printf("[3] Тест на модифікацію даних (спроба фальсифікації UID)...\n");
    cert.device_uid[0] = 'X'; // Несанкціонована зміна одного символу
    res = verify_decommission_certificate(&cert, hmac_secret, sizeof(hmac_secret) - 1);
    if (res != 0) {
        printf("    -> Атаку успішно заблоковано: підробку виявлено криптографічним верифікатором.\n");
    }

    return 0;
}
