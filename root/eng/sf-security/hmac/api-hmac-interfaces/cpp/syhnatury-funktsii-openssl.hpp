#include <openssl/evp.h>
#include <openssl/params.h>

// Сигнатури функцій OpenSSL C API залишаються ідентичними в C++
// Проте ідіоматичний C++ огортає їх у RAII-покажчики std::unique_ptr:
extern "C" {
    EVP_MAC *EVP_MAC_fetch(OSSL_LIB_CTX *libctx, const char *algorithm, const char *properties);
    EVP_MAC_CTX *EVP_MAC_CTX_new(EVP_MAC *mac);
    EVP_MAC_CTX *EVP_MAC_CTX_dup(const EVP_MAC_CTX *src);
    int EVP_MAC_init(EVP_MAC_CTX *ctx, const unsigned char *key, size_t keylen, const OSSL_PARAM params[]);
    int EVP_MAC_update(EVP_MAC_CTX *ctx, const unsigned char *data, size_t datalen);
    int EVP_MAC_final(EVP_MAC_CTX *ctx, unsigned char *out, size_t *outl, size_t outsize);
    void EVP_MAC_CTX_free(EVP_MAC_CTX *ctx);
    void EVP_MAC_free(EVP_MAC *mac);
}
