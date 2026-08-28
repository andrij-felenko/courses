#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>

#define SHA256_HEX_LEN 65
#define MAX_URL_LEN 2048

static void sha256_hex(const unsigned char *data, size_t len, char hex_out[SHA256_HEX_LEN]) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash);
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(&hex_out[i * 2], "%02x", hash[i]);
    }
    hex_out[64] = '\0';
}

static void hmac_sha256(const unsigned char *key, size_t key_len,
                        const unsigned char *data, size_t data_len,
                        unsigned char out[SHA256_DIGEST_LENGTH]) {
    unsigned int len = SHA256_DIGEST_LENGTH;
    HMAC(EVP_sha256(), key, (int)key_len, data, data_len, out, &len);
}

void derive_signing_key(const char *secret_key, const char *date,
                        const char *region, const char *service,
                        unsigned char k_signing[SHA256_DIGEST_LENGTH]) {
    char k_secret[128];
    snprintf(k_secret, sizeof(k_secret), "AWS4%s", secret_key);

    unsigned char k_date[SHA256_DIGEST_LENGTH];
    unsigned char k_region[SHA256_DIGEST_LENGTH];
    unsigned char k_service[SHA256_DIGEST_LENGTH];

    hmac_sha256((const unsigned char *)k_secret, strlen(k_secret),
                (const unsigned char *)date, strlen(date), k_date);
    hmac_sha256(k_date, SHA256_DIGEST_LENGTH,
                (const unsigned char *)region, strlen(region), k_region);
    hmac_sha256(k_region, SHA256_DIGEST_LENGTH,
                (const unsigned char *)service, strlen(service), k_service);
    hmac_sha256(k_service, SHA256_DIGEST_LENGTH,
                (const unsigned char *)"aws4_request", 12, k_signing);

    // Очищення проміжних секретів у пам'яті
    OPENSSL_cleanse(k_secret, sizeof(k_secret));
    OPENSSL_cleanse(k_date, sizeof(k_date));
    OPENSSL_cleanse(k_region, sizeof(k_region));
    OPENSSL_cleanse(k_service, sizeof(k_service));
}

int generate_presigned_url(const char *http_method, const char *host,
                           const char *uri, const char *access_key,
                           const char *secret_key, const char *region,
                           const char *service, int expires_sec,
                           time_t now_ts, char *url_out, size_t url_out_size) {
    char date_stamp[9];   // YYYYMMDD
    char amz_date[17];    // YYYYMMDDTHHMMSSZ
    struct tm gm_time;
    #ifdef _WIN32
    gmtime_s(&gm_time, &now_ts);
    #else
    gmtime_r(&now_ts, &gm_time);
    #endif

    strftime(date_stamp, sizeof(date_stamp), "%Y%m%d", &gm_time);
    strftime(amz_date, sizeof(amz_date), "%Y%m%dT%H%M%SZ", &gm_time);

    char credential_scope[128];
    snprintf(credential_scope, sizeof(credential_scope), "%s/%s/%s/aws4_request",
             date_stamp, region, service);

    char credential_encoded[256];
    snprintf(credential_encoded, sizeof(credential_encoded), "%s%%2F%s%%2F%s%%2F%s%%2Faws4_request",
             access_key, date_stamp, region, service);

    // Канонічний рядок параметрів, відсортований лексикографічно
    char canonical_qs[1024];
    snprintf(canonical_qs, sizeof(canonical_qs),
             "X-Amz-Algorithm=AWS4-HMAC-SHA256"
             "&X-Amz-Credential=%s"
             "&X-Amz-Date=%s"
             "&X-Amz-Expires=%d"
             "&X-Amz-SignedHeaders=host",
             credential_encoded, amz_date, expires_sec);

    char canonical_headers[256];
    snprintf(canonical_headers, sizeof(canonical_headers), "host:%s\n", host);

    char canonical_req[2048];
    snprintf(canonical_req, sizeof(canonical_req),
             "%s\n%s\n%s\n%s\nhost\nUNSIGNED-PAYLOAD",
             http_method, uri, canonical_qs, canonical_headers);

    char canonical_req_hash[SHA256_HEX_LEN];
    sha256_hex((const unsigned char *)canonical_req, strlen(canonical_req), canonical_req_hash);

    char string_to_sign[1024];
    snprintf(string_to_sign, sizeof(string_to_sign),
             "AWS4-HMAC-SHA256\n%s\n%s\n%s",
             amz_date, credential_scope, canonical_req_hash);

    unsigned char k_signing[SHA256_DIGEST_LENGTH];
    derive_signing_key(secret_key, date_stamp, region, service, k_signing);

    unsigned char raw_signature[SHA256_DIGEST_LENGTH];
    hmac_sha256(k_signing, SHA256_DIGEST_LENGTH,
                (const unsigned char *)string_to_sign, strlen(string_to_sign), raw_signature);
    OPENSSL_cleanse(k_signing, sizeof(k_signing));

    char signature_hex[SHA256_HEX_LEN];
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(&signature_hex[i * 2], "%02x", raw_signature[i]);
    }
    signature_hex[64] = '\0';

    return snprintf(url_out, url_out_size, "https://%s%s?%s&X-Amz-Signature=%s",
                    host, uri, canonical_qs, signature_hex);
}

int validate_presigned_url(const char *http_method, const char *host,
                           const char *uri, const char *canonical_qs_no_sig,
                           const char *provided_sig, const char *secret_key,
                           const char *date_stamp, const char *region,
                           const char *service, const char *amz_date,
                           time_t req_time, int expires_sec, time_t current_time) {
    // 1. Перевірка терміну дії (TTL)
    if (current_time < req_time || current_time > (req_time + expires_sec)) {
        return -1; // Посилання прострочене (Request has expired)
    }

    char credential_scope[128];
    snprintf(credential_scope, sizeof(credential_scope), "%s/%s/%s/aws4_request",
             date_stamp, region, service);

    char canonical_headers[256];
    snprintf(canonical_headers, sizeof(canonical_headers), "host:%s\n", host);

    char canonical_req[2048];
    snprintf(canonical_req, sizeof(canonical_req),
             "%s\n%s\n%s\n%s\nhost\nUNSIGNED-PAYLOAD",
             http_method, uri, canonical_qs_no_sig, canonical_headers);

    char canonical_req_hash[SHA256_HEX_LEN];
    sha256_hex((const unsigned char *)canonical_req, strlen(canonical_req), canonical_req_hash);

    char string_to_sign[1024];
    snprintf(string_to_sign, sizeof(string_to_sign),
             "AWS4-HMAC-SHA256\n%s\n%s\n%s",
             amz_date, credential_scope, canonical_req_hash);

    unsigned char k_signing[SHA256_DIGEST_LENGTH];
    derive_signing_key(secret_key, date_stamp, region, service, k_signing);

    unsigned char expected_raw_sig[SHA256_DIGEST_LENGTH];
    hmac_sha256(k_signing, SHA256_DIGEST_LENGTH,
                (const unsigned char *)string_to_sign, strlen(string_to_sign), expected_raw_sig);
    OPENSSL_cleanse(k_signing, sizeof(k_signing));

    char expected_sig_hex[SHA256_HEX_LEN];
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(&expected_sig_hex[i * 2], "%02x", expected_raw_sig[i]);
    }
    expected_sig_hex[64] = '\0';

    // 2. Порівняння підписів у константному часі для уникнення timing attacks
    if (CRYPTO_memcmp(provided_sig, expected_sig_hex, 64) == 0) {
        return 0; // Підпис автентичний
    }
    return -2; // Невірний підпис (SignatureMismatch)
}
