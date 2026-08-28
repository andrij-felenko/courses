#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>

#define MAX_SPIFFE_LEN 256

/* Витягування SPIFFE ID з розширення Subject Alternative Name (SAN URI) */
int extract_spiffe_id(X509 *cert, char *out_spiffe_id, size_t max_len) {
    if (!cert || !out_spiffe_id || max_len == 0) return 0;

    int san_loc = X509_get_ext_by_NID(cert, NID_subject_alt_name, -1);
    if (san_loc < 0) return 0;

    X509_EXTENSION *ext = X509_get_ext(cert, san_loc);
    if (!ext) return 0;

    GENERAL_NAMES *names = (GENERAL_NAMES *)X509V3_EXT_d2i(ext);
    if (!names) return 0;

    int found = 0;
    int num_names = sk_GENERAL_NAME_num(names);
    for (int i = 0; i < num_names; ++i) {
        GENERAL_NAME *val = sk_GENERAL_NAME_value(names, i);
        if (val->type == GEN_URI) {
            const char *uri_str = (const char *)ASN1_STRING_get0_data(val->d.uniformResourceIdentifier);
            size_t uri_len = (size_t)ASN1_STRING_length(val->d.uniformResourceIdentifier);

            if (uri_len < max_len && strncmp(uri_str, "spiffe://", 9) == 0) {
                memcpy(out_spiffe_id, uri_str, uri_len);
                out_spiffe_id[uri_len] = '\0';
                found = 1;
                break;
            }
        }
    }

    GENERAL_NAMES_free(names);
    return found;
}

/* Перевірка правила авторизації: чи має SPIFFE ID право на ресурс */
int authorize_request(const char *spiffe_id, const char *http_method, const char *path) {
    if (!spiffe_id || !http_method || !path) return 0;

    /* Правило: сервіс платежів має доступ до фінансового API */
    if (strcmp(spiffe_id, "spiffe://prod.corp/ns/billing/sa/checkout") == 0) {
        if (strcmp(http_method, "POST") == 0 && strcmp(path, "/v1/charge") == 0) {
            return 1;
        }
    }

    /* Правило: аудит-сервіс має доступ лише до читання */
    if (strcmp(spiffe_id, "spiffe://prod.corp/ns/security/sa/auditor") == 0) {
        if (strcmp(http_method, "GET") == 0) {
            return 1;
        }
    }

    return 0; /* Deny by default */
}

/* Ініціалізація захищеного SSL_CTX з пам'яті */
SSL_CTX *create_spiffe_ssl_ctx(const char *cert_pem, const char *key_pem, const char *ca_bundle_pem) {
    SSL_CTX *ctx = SSL_CTX_new(TLS_server_method());
    if (!ctx) return NULL;

    /* Суворий TLS 1.3 та обов'язковий взаємний mTLS */
    SSL_CTX_set_min_proto_version(ctx, TLS1_3_VERSION);
    SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT, NULL);

    /* Завантаження CA Bundle з пам'яті */
    BIO *ca_bio = BIO_new_mem_buf(ca_bundle_pem, -1);
    X509_STORE *store = SSL_CTX_get_cert_store(ctx);
    X509_INFO *it = NULL;
    STACK_OF(X509_INFO) *inf = PEM_X509_INFO_read_bio(ca_bio, NULL, NULL, NULL);
    BIO_free(ca_bio);

    if (inf) {
        for (int i = 0; i < sk_X509_INFO_num(inf); i++) {
            it = sk_X509_INFO_value(inf, i);
            if (it->x509) X509_STORE_add_cert(store, it->x509);
        }
        sk_X509_INFO_pop_free(inf, X509_INFO_free);
    }

    /* Завантаження сертифіката сервера */
    BIO *cert_bio = BIO_new_mem_buf(cert_pem, -1);
    X509 *cert = PEM_read_bio_X509(cert_bio, NULL, NULL, NULL);
    BIO_free(cert_bio);
    if (!cert || SSL_CTX_use_certificate(ctx, cert) <= 0) {
        X509_free(cert);
        SSL_CTX_free(ctx);
        return NULL;
    }
    X509_free(cert);

    /* Завантаження закритого ключа */
    BIO *key_bio = BIO_new_mem_buf(key_pem, -1);
    EVP_PKEY *pkey = PEM_read_bio_PrivateKey(key_bio, NULL, NULL, NULL);
    BIO_free(key_bio);
    if (!pkey || SSL_CTX_use_PrivateKey(ctx, pkey) <= 0) {
        EVP_PKEY_free(pkey);
        SSL_CTX_free(ctx);
        return NULL;
    }
    EVP_PKEY_free(pkey);

    return ctx;
}
