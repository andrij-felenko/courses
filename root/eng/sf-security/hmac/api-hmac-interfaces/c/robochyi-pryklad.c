#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/params.h>
#include <openssl/core_names.h>

int compute_openssl_hmac_sha256(
    const unsigned char *key, size_t key_len,
    const unsigned char *data, size_t data_len,
    unsigned char *out_mac, size_t *out_mac_len)
{
    EVP_MAC *mac = EVP_MAC_fetch(NULL, "HMAC", NULL);
    if (!mac) return 0;

    EVP_MAC_CTX *ctx = EVP_MAC_CTX_new(mac);
    if (!ctx) {
        EVP_MAC_free(mac);
        return 0;
    }

    char digest_name[] = "SHA256";
    OSSL_PARAM params[2];
    params[0] = OSSL_PARAM_construct_utf8_string(OSSL_MAC_PARAM_DIGEST, digest_name, 0);
    params[1] = OSSL_PARAM_construct_end();

    int ok = 1;
    ok &= EVP_MAC_init(ctx, key, key_len, params);
    ok &= EVP_MAC_update(ctx, data, data_len);
    ok &= EVP_MAC_final(ctx, out_mac, out_mac_len, 32);

    EVP_MAC_CTX_free(ctx);
    EVP_MAC_free(mac);
    return ok;
}
