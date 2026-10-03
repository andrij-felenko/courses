#include "mbedtls/aes.h"

#if defined(MBEDTLS_AES_ALT)

class HardwareAesPort {
public:
    static constexpr uintptr_t AesBase = 0x6000B000;
    static constexpr uintptr_t RegCtrl = AesBase + 0x00;
    static constexpr uintptr_t RegStart = AesBase + 0x04;
    static constexpr uintptr_t RegStatus = AesBase + 0x08;
    static constexpr uintptr_t TextIn = AesBase + 0x10;
    static constexpr uintptr_t TextOut = AesBase + 0x30;

    static int processBlock(int mode, const uint8_t in[16], uint8_t out[16]) {
        memcpy(reinterpret_cast<void*>(TextIn), in, 16);
        *reinterpret_cast<volatile uint32_t*>(RegCtrl) = (mode == MBEDTLS_AES_ENCRYPT) ? 1 : 0;
        *reinterpret_cast<volatile uint32_t*>(RegStart) = 1;

        while ((*reinterpret_cast<volatile uint32_t*>(RegStatus) & 0x01) == 0) {
            // Чекаємо завершення виконання блоком апаратного AES
        }

        memcpy(out, reinterpret_cast<const void*>(TextOut), 16);
        return 0;
    }
};

extern "C" {
    void mbedtls_aes_init(mbedtls_aes_context *ctx) {
        memset(ctx, 0, sizeof(mbedtls_aes_context));
    }
    void mbedtls_aes_free(mbedtls_aes_context *ctx) {
        if (ctx) memset(ctx, 0, sizeof(mbedtls_aes_context));
    }
    int mbedtls_aes_crypt_ecb(mbedtls_aes_context *ctx, int mode,
                              const unsigned char input[16], unsigned char output[16]) {
        return HardwareAesPort::processBlock(mode, input, output);
    }
}
#endif
