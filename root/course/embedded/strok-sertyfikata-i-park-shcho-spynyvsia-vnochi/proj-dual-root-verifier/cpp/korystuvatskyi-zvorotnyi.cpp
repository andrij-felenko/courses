#include <cstdint>
#include "mbedtls/x509_crt.h"

struct VerifyContext {
    bool emergencyBootstrapMode{false};
    bool allowClockSkewRecovery{false};
};

extern "C" int customCppVerifyCallback(void* parameter, mbedtls_x509_crt* /*crt*/, int /*depth*/, uint32_t* flags) noexcept {
    if (!flags) return -1;
    auto* context = static_cast<VerifyContext*>(parameter);

    const uint32_t currentFlags = *flags;

    // Перевірка на суто часові помилки (розсинхронізація RTC)
    constexpr uint32_t TimeFlagsMask = MBEDTLS_X509_BADCERT_EXPIRED | MBEDTLS_X509_BADCERT_FUTURE;
    if ((currentFlags & ~TimeFlagsMask) == 0 && (currentFlags & TimeFlagsMask) != 0) {
        if (context && (context->emergencyBootstrapMode || context->allowClockSkewRecovery)) {
            // Очищаємо прапорці часу лише для аварійного каналу відновлення
            *flags &= ~TimeFlagsMask;
            return 0;
        }
    }

    // Будь-яке порушення криптографічної цілісності або підпису призводить до негайної відмови
    constexpr uint32_t CriticalFlags = MBEDTLS_X509_BADCERT_NOT_TRUSTED | MBEDTLS_X509_BADCERT_BAD_KEY | MBEDTLS_X509_BADCERT_BAD_MD;
    if ((currentFlags & CriticalFlags) != 0) {
        return -1;
    }

    return 0;
}
