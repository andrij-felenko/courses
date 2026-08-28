#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/x509.h>
#include <openssl/x509v3.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <openssl/evp.h>

/* Результат верифікації сертифіката */
typedef struct {
    int is_valid;
    int error_code;
    const char *error_string;
    unsigned char leaf_spki_sha256[32];
} CertVerifyResult;

/* Обчислення SHA-256 відбитка відкритого ключа (SubjectPublicKeyInfo) */
static int compute_spki_sha256(X509 *cert, unsigned char *out_hash) {
    X509_PUBKEY *pubkey = X509_get_X509_PUBKEY(cert);
    if (!pubkey) return 0;

    const unsigned char *spki_der = NULL;
    int spki_len = i2d_X509_PUBKEY(pubkey, (unsigned char **)&spki_der);
    if (spki_len <= 0 || !spki_der) return 0;

    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) {
        OPENSSL_free((void *)spki_der);
        return 0;
    }

    int ok = EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) &&
             EVP_DigestUpdate(ctx, spki_der, (size_t)spki_len) &&
             EVP_DigestFinal_ex(ctx, out_hash, NULL);

    EVP_MD_CTX_free(ctx);
    OPENSSL_free((void *)spki_der);
    return ok ? 1 : 0;
}

/* Головна функція верифікації ланцюга */
CertVerifyResult verify_certificate_chain(
    const char *leaf_pem,
    const char *intermediate_pem,
    const char *root_ca_pem,
    const char *expected_hostname
) {
    CertVerifyResult result;
    memset(&result, 0, sizeof(result));
    result.is_valid = 0;
    result.error_code = X509_V_ERR_UNSPECIFIED;

    BIO *bio_leaf = NULL;
    BIO *bio_interm = NULL;
    BIO *bio_root = NULL;
    X509 *leaf = NULL;
    X509 *interm = NULL;
    X509 *root = NULL;
    X509_STORE *store = NULL;
    X509_STORE_CTX *ctx = NULL;
    STACK_OF(X509) *untrusted_stack = NULL;

    /* 1. Читання кінцевого сертифіката */
    bio_leaf = BIO_new_mem_buf(leaf_pem, -1);
    if (!bio_leaf) goto cleanup;
    leaf = PEM_read_bio_X509(bio_leaf, NULL, NULL, NULL);
    if (!leaf) goto cleanup;

    /* 2. Читання проміжного сертифіката */
    if (intermediate_pem) {
        bio_interm = BIO_new_mem_buf(intermediate_pem, -1);
        if (!bio_interm) goto cleanup;
        interm = PEM_read_bio_X509(bio_interm, NULL, NULL, NULL);
        if (!interm) goto cleanup;
    }

    /* 3. Читання кореневого сертифіката довіри */
    bio_root = BIO_new_mem_buf(root_ca_pem, -1);
    if (!bio_root) goto cleanup;
    root = PEM_read_bio_X509(bio_root, NULL, NULL, NULL);
    if (!root) goto cleanup;

    /* 4. Створення та заповнення сховища довіри */
    store = X509_STORE_new();
    if (!store) goto cleanup;
    if (X509_STORE_add_cert(store, root) != 1) goto cleanup;

    /* 5. Формування стеку проміжних сертифікатів */
    untrusted_stack = sk_X509_new_null();
    if (!untrusted_stack) goto cleanup;
    if (interm) {
        sk_X509_push(untrusted_stack, interm);
    }

    /* 6. Ініціалізація контексту верифікації */
    ctx = X509_STORE_CTX_new();
    if (!ctx) goto cleanup;
    if (X509_STORE_CTX_init(ctx, store, leaf, untrusted_stack) != 1) goto cleanup;

    /* 7. Налаштування суворої перевірки імені хоста через SAN */
    if (expected_hostname && strlen(expected_hostname) > 0) {
        X509_VERIFY_PARAM *param = X509_STORE_CTX_get0_param(ctx);
        X509_VERIFY_PARAM_set_hostflags(param, X509_CHECK_FLAG_NO_PARTIAL_WILDCARDS);
        if (X509_VERIFY_PARAM_set1_host(param, expected_hostname, 0) != 1) {
            goto cleanup;
        }
    }

    /* 8. Виконання верифікації */
    int verify_status = X509_verify_cert(ctx);
    if (verify_status == 1) {
        result.is_valid = 1;
        result.error_code = X509_V_OK;
        result.error_string = "Certificate verification successful";
        compute_spki_sha256(leaf, result.leaf_spki_sha256);
    } else {
        result.is_valid = 0;
        result.error_code = X509_STORE_CTX_get_error(ctx);
        result.error_string = X509_verify_cert_error_string(result.error_code);
    }

cleanup:
    if (ctx) X509_STORE_CTX_free(ctx);
    if (untrusted_stack) sk_X509_free(untrusted_stack);
    if (store) X509_STORE_free(store);
    if (leaf) X509_free(leaf);
    if (interm) X509_free(interm);
    if (root) X509_free(root);
    if (bio_leaf) BIO_free(bio_leaf);
    if (bio_interm) BIO_free(bio_interm);
    if (bio_root) BIO_free(bio_root);

    return result;
}
