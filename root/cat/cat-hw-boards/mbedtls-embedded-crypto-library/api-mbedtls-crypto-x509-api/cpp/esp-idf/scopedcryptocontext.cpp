#include "mbedtls/x509_crt.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/entropy.h"

class ScopedCryptoContext {
private:
    mbedtls_x509_crt crt_;
    mbedtls_ctr_drbg_context drbg_;
    mbedtls_entropy_context entropy_;

public:
    ScopedCryptoContext() {
        mbedtls_x509_crt_init(&crt_);
        mbedtls_ctr_drbg_init(&drbg_);
        mbedtls_entropy_init(&entropy_);
    }

    ~ScopedCryptoContext() {
        // Зворотний порядок очищення під час руйнування об'єкта
        mbedtls_x509_crt_free(&crt_);
        mbedtls_ctr_drbg_free(&drbg_);
        mbedtls_entropy_free(&entropy_);
    }

    mbedtls_x509_crt* crt() { return &crt_; }
    mbedtls_ctr_drbg_context* drbg() { return &drbg_; }
    mbedtls_entropy_context* entropy() { return &entropy_; }
};
