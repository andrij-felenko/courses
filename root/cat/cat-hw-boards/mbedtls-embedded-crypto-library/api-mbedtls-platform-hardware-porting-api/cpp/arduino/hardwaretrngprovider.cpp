#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

class HardwareTrngProvider {
public:
    static int poll(void *data, unsigned char *output, size_t len, size_t *olen) {
        size_t bytes_written = 0;
        while (bytes_written < len) {
            uint32_t val = *reinterpret_cast<volatile uint32_t*>(0x60000CC0);
            size_t chunk = (len - bytes_written > 4) ? 4 : (len - bytes_written);
            memcpy(output + bytes_written, &val, chunk);
            bytes_written += chunk;
        }
        *olen = bytes_written;
        return 0;
    }
};

class CryptoRngSystem {
private:
    mbedtls_entropy_context entropy_;
    mbedtls_ctr_drbg_context drbg_;

public:
    bool begin() {
        mbedtls_entropy_init(&entropy_);
        mbedtls_ctr_drbg_init(&drbg_);

        int status = mbedtls_entropy_add_source(&entropy_, HardwareTrngProvider::poll,
                                                nullptr, 32, MBEDTLS_ENTROPY_SOURCE_STRONG);
        if (status != 0) return false;

        const char *custom_tag = "arduino_tls";
        return mbedtls_ctr_drbg_seed(&drbg_, mbedtls_entropy_func, &entropy_,
                                    reinterpret_cast<const uint8_t*>(custom_tag),
                                    strlen(custom_tag)) == 0;
    }
};
