/* dnssec_validator.h */
#ifndef DNSSEC_VALIDATOR_H
#define DNSSEC_VALIDATOR_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DNSSEC_OK = 0,
    DNSSEC_ERR_EXPIRED,
    DNSSEC_ERR_NOT_YET_VALID,
    DNSSEC_ERR_KEYTAG_MISMATCH,
    DNSSEC_ERR_MALFORMED_KEY,
    DNSSEC_ERR_MALFORMED_SIG,
    DNSSEC_ERR_CRYPTO_FAIL,
    DNSSEC_ERR_MEMORY
} dnssec_status_t;

typedef struct {
    uint16_t type_covered;
    uint8_t  algorithm;
    uint8_t  labels;
    uint32_t original_ttl;
    uint32_t expiration;
    uint32_t inception;
    uint16_t key_tag;
    const char *signer_name;
    const uint8_t *sig_bytes;
    size_t sig_len;
} rrsig_record_t;

typedef struct {
    uint16_t flags;
    uint8_t  protocol;
    uint8_t  algorithm;
    const uint8_t *pubkey_bytes;
    size_t pubkey_len;
} dnskey_record_t;

uint16_t dnssec_calc_keytag(const uint8_t *rdata, size_t rdata_len);

dnssec_status_t dnssec_verify_signature(
    const rrsig_record_t *rrsig,
    const dnskey_record_t *dnskey,
    const uint8_t *preimage,
    size_t preimage_len,
    int64_t current_time
);

#ifdef __cplusplus
}
#endif

#endif /* DNSSEC_VALIDATOR_H */

/* dnssec_validator.c */
#include "dnssec_validator.h"
#include <openssl/evp.h>
#include <openssl/ec.h>
#include <openssl/rsa.h>
#include <openssl/param_build.h>
#include <openssl/core_names.h>
#include <openssl/ecdsa.h>
#include <openssl/bn.h>
#include <string.h>
#include <stdio.h>

#define CLOCK_SKEW_TOLERANCE 300 /* 5 хвилин */

uint16_t dnssec_calc_keytag(const uint8_t *rdata, size_t rdata_len) {
    if (!rdata || rdata_len < 4) return 0;
    uint32_t ac = 0;
    for (size_t i = 0; i < rdata_len; ++i) {
        ac += (i & 1) ? rdata[i] : ((uint32_t)rdata[i] << 8);
    }
    ac += (ac >> 16) & 0xFFFF;
    return (uint16_t)(ac & 0xFFFF);
}

static uint8_t *raw_ecdsa_to_der(const uint8_t *sig_raw, size_t sig_len, size_t *out_der_len) {
    if (sig_len != 64) return NULL;

    BIGNUM *r = BN_bin2bn(sig_raw, 32, NULL);
    BIGNUM *s = BN_bin2bn(sig_raw + 32, 32, NULL);
    if (!r || !s) {
        BN_free(r);
        BN_free(s);
        return NULL;
    }

    ECDSA_SIG *sig = ECDSA_SIG_new();
    if (!sig) {
        BN_free(r);
        BN_free(s);
        return NULL;
    }

    ECDSA_SIG_set0(sig, r, s);

    int der_len = i2d_ECDSA_SIG(sig, NULL);
    if (der_len <= 0) {
        ECDSA_SIG_free(sig);
        return NULL;
    }

    uint8_t *der_buf = OPENSSL_malloc((size_t)der_len);
    if (!der_buf) {
        ECDSA_SIG_free(sig);
        return NULL;
    }

    uint8_t *p = der_buf;
    i2d_ECDSA_SIG(sig, &p);
    ECDSA_SIG_free(sig);

    *out_der_len = (size_t)der_len;
    return der_buf;
}

static EVP_PKEY *build_ecdsa_pkey(const uint8_t *pubkey, size_t pubkey_len) {
    if (pubkey_len != 64) return NULL;

    uint8_t uncompressed_pt[65];
    uncompressed_pt[0] = 0x04;
    memcpy(uncompressed_pt + 1, pubkey, 64);

    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_from_name(NULL, "EC", NULL);
    if (!pctx) return NULL;

    if (EVP_PKEY_fromdata_init(pctx) <= 0) {
        EVP_PKEY_CTX_free(pctx);
        return NULL;
    }

    OSSL_PARAM_BLD *bld = OSSL_PARAM_BLD_new();
    OSSL_PARAM_BLD_push_utf8_string(bld, OSSL_PKEY_PARAM_GROUP_NAME, "prime256v1", 0);
    OSSL_PARAM_BLD_push_octet_string(bld, OSSL_PKEY_PARAM_PUB_KEY, uncompressed_pt, 65);

    OSSL_PARAM *params = OSSL_PARAM_BLD_to_param(bld);
    EVP_PKEY *pkey = NULL;
    if (EVP_PKEY_fromdata(pctx, &pkey, EVP_PKEY_PUBLIC_KEY, params) <= 0) {
        pkey = NULL;
    }

    OSSL_PARAM_free(params);
    OSSL_PARAM_BLD_free(bld);
    EVP_PKEY_CTX_free(pctx);
    return pkey;
}

static EVP_PKEY *build_rsa_pkey(const uint8_t *pubkey, size_t pubkey_len) {
    if (pubkey_len < 3) return NULL;
    size_t elen = pubkey[0];
    size_t offset = 1;
    if (elen == 0) {
        if (pubkey_len < 5) return NULL;
        elen = ((size_t)pubkey[1] << 8) | pubkey[2];
        offset = 3;
    }
    if (pubkey_len < offset + elen) return NULL;

    BIGNUM *e = BN_bin2bn(pubkey + offset, (int)elen, NULL);
    BIGNUM *n = BN_bin2bn(pubkey + offset + elen, (int)(pubkey_len - offset - elen), NULL);
    if (!e || !n) {
        BN_free(e);
        BN_free(n);
        return NULL;
    }

    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_from_name(NULL, "RSA", NULL);
    if (!pctx || EVP_PKEY_fromdata_init(pctx) <= 0) {
        BN_free(e); BN_free(n);
        EVP_PKEY_CTX_free(pctx);
        return NULL;
    }

    OSSL_PARAM_BLD *bld = OSSL_PARAM_BLD_new();
    OSSL_PARAM_BLD_push_BN(bld, OSSL_PKEY_PARAM_RSA_N, n);
    OSSL_PARAM_BLD_push_BN(bld, OSSL_PKEY_PARAM_RSA_E, e);

    OSSL_PARAM *params = OSSL_PARAM_BLD_to_param(bld);
    EVP_PKEY *pkey = NULL;
    EVP_PKEY_fromdata(pctx, &pkey, EVP_PKEY_PUBLIC_KEY, params);

    OSSL_PARAM_free(params);
    OSSL_PARAM_BLD_free(bld);
    EVP_PKEY_CTX_free(pctx);
    BN_free(e);
    BN_free(n);
    return pkey;
}

dnssec_status_t dnssec_verify_signature(
    const rrsig_record_t *rrsig,
    const dnskey_record_t *dnskey,
    const uint8_t *preimage,
    size_t preimage_len,
    int64_t current_time
) {
    if (!rrsig || !dnskey || !preimage) return DNSSEC_ERR_CRYPTO_FAIL;

    if (current_time + CLOCK_SKEW_TOLERANCE < (int64_t)rrsig->inception) {
        return DNSSEC_ERR_NOT_YET_VALID;
    }
    if (current_time - CLOCK_SKEW_TOLERANCE > (int64_t)rrsig->expiration) {
        return DNSSEC_ERR_EXPIRED;
    }

    if (dnskey->algorithm != rrsig->algorithm) {
        return DNSSEC_ERR_CRYPTO_FAIL;
    }

    EVP_PKEY *pkey = NULL;
    uint8_t *der_sig = NULL;
    size_t der_sig_len = 0;
    const uint8_t *sig_to_verify = rrsig->sig_bytes;
    size_t sig_len_to_verify = rrsig->sig_len;

    if (rrsig->algorithm == 13) { /* ECDSA P-256 */
        pkey = build_ecdsa_pkey(dnskey->pubkey_bytes, dnskey->pubkey_len);
        if (!pkey) return DNSSEC_ERR_MALFORMED_KEY;

        der_sig = raw_ecdsa_to_der(rrsig->sig_bytes, rrsig->sig_len, &der_sig_len);
        if (!der_sig) {
            EVP_PKEY_free(pkey);
            return DNSSEC_ERR_MALFORMED_SIG;
        }
        sig_to_verify = der_sig;
        sig_len_to_verify = der_sig_len;
    } else if (rrsig->algorithm == 8) { /* RSA-SHA256 */
        pkey = build_rsa_pkey(dnskey->pubkey_bytes, dnskey->pubkey_len);
        if (!pkey) return DNSSEC_ERR_MALFORMED_KEY;
    } else {
        return DNSSEC_ERR_CRYPTO_FAIL;
    }

    EVP_MD_CTX *mctx = EVP_MD_CTX_new();
    if (!mctx) {
        if (der_sig) OPENSSL_free(der_sig);
        EVP_PKEY_free(pkey);
        return DNSSEC_ERR_MEMORY;
    }

    dnssec_status_t status = DNSSEC_ERR_CRYPTO_FAIL;
    if (EVP_DigestVerifyInit(mctx, NULL, EVP_sha256(), NULL, pkey) > 0) {
        if (EVP_DigestVerifyUpdate(mctx, preimage, preimage_len) > 0) {
            if (EVP_DigestVerifyFinal(mctx, sig_to_verify, sig_len_to_verify) == 1) {
                status = DNSSEC_OK;
            }
        }
    }

    EVP_MD_CTX_free(mctx);
    if (der_sig) OPENSSL_free(der_sig);
    EVP_PKEY_free(pkey);

    return status;
}
