/* dnssec_validator.c — Реалізація валідатора DNSSEC мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <openssl/ec.h>
#include <openssl/ecdsa.h>

#define DNSSEC_ALG_ECDSAP256SHA256 13
#define DNSSEC_DIGEST_SHA256        2

typedef struct {
    uint16_t type_covered;
    uint8_t  algorithm;
    uint8_t  labels;
    uint32_t original_ttl;
    uint32_t sig_expiration;
    uint32_t sig_inception;
    uint16_t key_tag;
    const uint8_t *signer_name;
    size_t signer_name_len;
    const uint8_t *sig_data;
    size_t sig_len;
} dnssec_rrsig_t;

typedef struct {
    uint16_t flags;
    uint8_t  protocol;
    uint8_t  algorithm;
    const uint8_t *pubkey;
    size_t pubkey_len;
    const uint8_t *rdata_raw;
    size_t rdata_len;
} dnssec_dnskey_t;

typedef struct {
    const uint8_t *rdata;
    uint16_t rdlength;
} dnssec_rr_entry_t;

/* 1. Обчислення Key Tag за RFC 4034 Appendix B */
uint16_t dnssec_calc_key_tag(const uint8_t *rdata, size_t rdata_len) {
    uint32_t ac = 0;
    for (size_t i = 0; i < rdata_len; i++) {
        ac += (i & 1) ? (uint32_t)rdata[i] : ((uint32_t)rdata[i] << 8);
    }
    ac += (ac >> 16) & 0xFFFF;
    return (uint16_t)(ac & 0xFFFF);
}

/* 2. Порівняння записів для канонічного сортування RRset (RFC 4034 §6.3) */
static int compare_rr_entries(const void *a, const void *b) {
    const dnssec_rr_entry_t *r1 = (const dnssec_rr_entry_t *)a;
    const dnssec_rr_entry_t *r2 = (const dnssec_rr_entry_t *)b;
    size_t min_len = (r1->rdlength < r2->rdlength) ? r1->rdlength : r2->rdlength;
    int cmp = memcmp(r1->rdata, r2->rdata, min_len);
    if (cmp != 0) return cmp;
    if (r1->rdlength < r2->rdlength) return -1;
    if (r1->rdlength > r2->rdlength) return 1;
    return 0;
}

/* 3. Звірка відповідності відкритого ключа KSK запису DS */
bool dnssec_verify_ds(const uint8_t *owner_wire, size_t owner_wire_len,
                      const dnssec_dnskey_t *key,
                      const uint8_t *expected_digest, size_t expected_digest_len) {
    if (expected_digest_len != SHA256_DIGEST_LENGTH) return false;

    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) return false;

    uint8_t calc_digest[SHA256_DIGEST_LENGTH];
    bool ok = false;

    if (EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) &&
        EVP_DigestUpdate(ctx, owner_wire, owner_wire_len) &&
        EVP_DigestUpdate(ctx, key->rdata_raw, key->rdata_len) &&
        EVP_DigestFinal_ex(ctx, calc_digest, NULL)) {
        ok = (CRYPTO_memcmp(calc_digest, expected_digest, SHA256_DIGEST_LENGTH) == 0);
    }

    EVP_MD_CTX_free(ctx);
    return ok;
}

/* 4. Валідація підпису RRSIG над набором RRset для ECDSA P-256 */
bool dnssec_verify_rrsig(const dnssec_rrsig_t *sig,
                         const uint8_t *owner_wire, size_t owner_wire_len,
                         uint16_t rr_class,
                         dnssec_rr_entry_t *entries, size_t num_entries,
                         const dnssec_dnskey_t *key,
                         uint32_t current_time) {
    /* Перевірка часового вікна валідності */
    if (current_time < sig->sig_inception || current_time > sig->sig_expiration) {
        fprintf(stderr, "Помилка DNSSEC: підпис прострочено або ще не набрав чинності!\n");
        return false;
    }

    /* Перевірка збігу алгоритму та Key Tag */
    if (sig->algorithm != key->algorithm || sig->algorithm != DNSSEC_ALG_ECDSAP256SHA256) {
        fprintf(stderr, "Помилка DNSSEC: непідтримуваний або незбіжний алгоритм ключа!\n");
        return false;
    }

    uint16_t calculated_tag = dnssec_calc_key_tag(key->rdata_raw, key->rdata_len);
    if (sig->key_tag != calculated_tag) {
        fprintf(stderr, "Помилка DNSSEC: Key Tag підпису (%u) не збігається з ключем (%u)!\n",
                sig->key_tag, calculated_tag);
        return false;
    }

    /* Канонічне сортування записів RRset */
    qsort(entries, num_entries, sizeof(dnssec_rr_entry_t), compare_rr_entries);

    /* Формування підписного масиву байтів */
    EVP_MD_CTX *md_ctx = EVP_MD_CTX_new();
    if (!md_ctx) return false;

    if (!EVP_DigestInit_ex(md_ctx, EVP_sha256(), NULL)) {
        EVP_MD_CTX_free(md_ctx);
        return false;
    }

    /* А. Заголовок RDATA RRSIG (18 байтів без самого підпису) */
    uint8_t hdr[18];
    hdr[0] = (uint8_t)(sig->type_covered >> 8);
    hdr[1] = (uint8_t)(sig->type_covered & 0xFF);
    hdr[2] = sig->algorithm;
    hdr[3] = sig->labels;
    hdr[4] = (uint8_t)((sig->original_ttl >> 24) & 0xFF);
    hdr[5] = (uint8_t)((sig->original_ttl >> 16) & 0xFF);
    hdr[6] = (uint8_t)((sig->original_ttl >> 8) & 0xFF);
    hdr[7] = (uint8_t)(sig->original_ttl & 0xFF);
    hdr[8] = (uint8_t)((sig->sig_expiration >> 24) & 0xFF);
    hdr[9] = (uint8_t)((sig->sig_expiration >> 16) & 0xFF);
    hdr[10] = (uint8_t)((sig->sig_expiration >> 8) & 0xFF);
    hdr[11] = (uint8_t)(sig->sig_expiration & 0xFF);
    hdr[12] = (uint8_t)((sig->sig_inception >> 24) & 0xFF);
    hdr[13] = (uint8_t)((sig->sig_inception >> 16) & 0xFF);
    hdr[14] = (uint8_t)((sig->sig_inception >> 8) & 0xFF);
    hdr[15] = (uint8_t)(sig->sig_inception & 0xFF);
    hdr[16] = (uint8_t)(sig->key_tag >> 8);
    hdr[17] = (uint8_t)(sig->key_tag & 0xFF);

    EVP_DigestUpdate(md_ctx, hdr, 18);
    EVP_DigestUpdate(md_ctx, sig->signer_name, sig->signer_name_len);

    /* Б. Канонічні записи RRset */
    uint8_t prefix[10];
    prefix[0] = (uint8_t)(sig->type_covered >> 8);
    prefix[1] = (uint8_t)(sig->type_covered & 0xFF);
    prefix[2] = (uint8_t)(rr_class >> 8);
    prefix[3] = (uint8_t)(rr_class & 0xFF);
    prefix[4] = hdr[4]; prefix[5] = hdr[5]; prefix[6] = hdr[6]; prefix[7] = hdr[7]; /* Original TTL */

    for (size_t i = 0; i < num_entries; i++) {
        EVP_DigestUpdate(md_ctx, owner_wire, owner_wire_len);
        prefix[8] = (uint8_t)(entries[i].rdlength >> 8);
        prefix[9] = (uint8_t)(entries[i].rdlength & 0xFF);
        EVP_DigestUpdate(md_ctx, prefix, 10);
        EVP_DigestUpdate(md_ctx, entries[i].rdata, entries[i].rdlength);
    }

    uint8_t digest[SHA256_DIGEST_LENGTH];
    unsigned int digest_len = 0;
    EVP_DigestFinal_ex(md_ctx, digest, &digest_len);
    EVP_MD_CTX_free(md_ctx);

    /* Перевірка підпису ECDSA P-256 через OpenSSL */
    if (key->pubkey_len != 64 || sig->sig_len != 64) {
        fprintf(stderr, "Помилка DNSSEC: некоректна довжина відкритого ключа чи підпису ECDSA!\n");
        return false;
    }

    /* Відновлення точки відкритого ключа (0x04 + X + Y) */
    uint8_t uncompressed_pt[65];
    uncompressed_pt[0] = 0x04;
    memcpy(&uncompressed_pt[1], key->pubkey, 64);

    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_id(EVP_PKEY_EC, NULL);
    if (!pctx) return false;
    if (EVP_PKEY_paramgen_init(pctx) <= 0 ||
        EVP_PKEY_CTX_set_ec_paramgen_curve_nid(pctx, NID_X9_62_prime256v1) <= 0) {
        EVP_PKEY_CTX_free(pctx);
        return false;
    }

    EVP_PKEY *params = NULL;
    EVP_PKEY_paramgen(pctx, &params);
    EVP_PKEY_CTX_free(pctx);

    EVP_PKEY *pubkey = NULL;
    EVP_PKEY_CTX *kctx = EVP_PKEY_CTX_new(params, NULL);
    EVP_PKEY_free(params);

    if (EVP_PKEY_keygen_init(kctx) <= 0) {
        EVP_PKEY_CTX_free(kctx);
        return false;
    }

    EC_KEY *eckey = EC_KEY_new_by_curve_name(NID_X9_62_prime256v1);
    EC_KEY_oct2key(eckey, uncompressed_pt, 65, NULL);
    pubkey = EVP_PKEY_new();
    EVP_PKEY_set1_EC_KEY(pubkey, eckey);
    EC_KEY_free(eckey);
    EVP_PKEY_CTX_free(kctx);

    /* Формування структури ECDSA_SIG з сирих компонентів R і S */
    ECDSA_SIG *ec_sig = ECDSA_SIG_new();
    BIGNUM *r = BN_bin2bn(&sig->sig_data[0], 32, NULL);
    BIGNUM *s = BN_bin2bn(&sig->sig_data[32], 32, NULL);
    ECDSA_SIG_set0(ec_sig, r, s);

    int verify_status = ECDSA_do_verify(digest, SHA256_DIGEST_LENGTH, ec_sig, EVP_PKEY_get0_EC_KEY(pubkey));
    ECDSA_SIG_free(ec_sig);
    EVP_PKEY_free(pubkey);

    return (verify_status == 1);
}
