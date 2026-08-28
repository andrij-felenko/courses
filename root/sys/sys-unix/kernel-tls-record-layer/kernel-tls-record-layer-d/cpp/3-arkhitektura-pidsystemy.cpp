#include <sys/socket.h>
#include <netinet/tcp.h>
#include <linux/tls.h>
#include <string_view>
#include <system_error>
#include <cstring>

namespace ktls_utils {

[[nodiscard]] std::error_code enable_ktls(int sockfd, const struct tls12_crypto_info_aes_gcm_128& crypto_tx) noexcept {
    constexpr std::string_view ulp_name = "tls";
    
    // 1. Активація ULP модуля у ядрі
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_ULP, ulp_name.data(), ulp_name.size()) < 0) {
        return std::error_code(errno, std::generic_category());
    }

    // 2. Встановлення ключів TX
    if (::setsockopt(sockfd, SOL_TLS, TLS_TX, &crypto_tx, sizeof(crypto_tx)) < 0) {
        return std::error_code(errno, std::generic_category());
    }

    return {};
}

} // namespace ktls_utils
