#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include <cstring>

class CryptoRng {
private:
    mbedtls_entropy_context entropy_;
    mbedtls_ctr_drbg_context ctr_drbg_;
    bool initialized_;

    static int getHwEntropy(void *data, unsigned char *output, size_t len, size_t *olen) {
        uint32_t val;
        for (size_t i = 0; i < len; i += 4) {
            val = *((volatile uint32_t *)0x3FF20E44);
            size_t chunk = (len - i < 4) ? (len - i) : 4;
            std::memcpy(output + i, &val, chunk);
        }
        *olen = len;
        return 0;
    }

public:
    CryptoRng() : initialized_(false) {
        mbedtls_entropy_init(&entropy_);
        mbedtls_ctr_drbg_init(&ctr_drbg_);
    }

    ~CryptoRng() {
        mbedtls_ctr_drbg_free(&ctr_drbg_);
        mbedtls_entropy_free(&entropy_);
    }

    bool init(const char *customPers) {
        int ret = mbedtls_entropy_add_source(&entropy_, getHwEntropy, nullptr, 32, MBEDTLS_ENTROPY_SOURCE_STRONG);
        if (ret != 0) return false;

        ret = mbedtls_ctr_drbg_seed(&ctr_drbg_, mbedtls_entropy_func, &entropy_,
                                    reinterpret_cast<const unsigned char*>(customPers),
                                    std::strlen(customPers));
        if (ret == 0) {
            initialized_ = true;
        }
        return initialized_;
    }

    mbedtls_ctr_drbg_context* getContext() { return &ctr_drbg_; }
};
