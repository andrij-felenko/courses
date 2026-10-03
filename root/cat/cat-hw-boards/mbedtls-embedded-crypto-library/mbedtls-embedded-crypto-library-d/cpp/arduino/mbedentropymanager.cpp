#include <Arduino.h>
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

class MbedEntropyManager {
private:
    mbedtls_entropy_context entropyCtx;
    mbedtls_ctr_drbg_context drbgCtx;
    bool isReady;

public:
    MbedEntropyManager() : isReady(false) {
        mbedtls_entropy_init(&entropyCtx);
        mbedtls_ctr_drbg_init(&drbgCtx);
    }

    ~MbedEntropyManager() {
        mbedtls_ctr_drbg_free(&drbgCtx);
        mbedtls_entropy_free(&entropyCtx);
    }

    bool init(const char *personalization = "arduino_mbedtls") {
        int res = mbedtls_ctr_drbg_seed(&drbgCtx, mbedtls_entropy_func, &entropyCtx,
                                         (const unsigned char *)personalization,
                                         strlen(personalization));
        isReady = (res == 0);
        return isReady;
    }

    bool generateBytes(uint8_t *buffer, size_t size) {
        if (!isReady) return false;
        return (mbedtls_ctr_drbg_random(&drbgCtx, buffer, size) == 0);
    }
};
