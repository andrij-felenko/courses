#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <cmath>
#include <iomanip>
#include <sstream>
#include <span>

namespace totp {

std::string generate_totp_code(
    std::span<const std::uint8_t> secret,
    std::int64_t timestamp_seconds,
    std::int64_t time_step = 30,
    int digits = 6
) {
    std::uint64_t counter = static_cast<std::uint64_t>(timestamp_seconds / time_step);
    std::uint8_t counter_bytes[8];
    for (int i = 7; i >= 0; --i) {
        counter_bytes[i] = static_cast<std::uint8_t>(counter & 0xFF);
        counter >>= 8;
    }

    unsigned int len = 20;
    std::uint8_t digest[EVP_MAX_MD_SIZE];
    HMAC(EVP_sha1(), secret.data(), static_cast<int>(secret.size()),
         counter_bytes, sizeof(counter_bytes), digest, &len);

    std::uint8_t offset = digest[len - 1] & 0x0F;
    std::uint32_t binary_code =
        ((static_cast<std::uint32_t>(digest[offset]) & 0x7F) << 24) |
        ((static_cast<std::uint32_t>(digest[offset + 1]) & 0xFF) << 16) |
        ((static_cast<std::uint32_t>(digest[offset + 2]) & 0xFF) << 8) |
        (static_cast<std::uint32_t>(digest[offset + 3]) & 0xFF);

    std::uint32_t mod = static_cast<std::uint32_t>(std::pow(10, digits));
    std::uint32_t otp = binary_code % mod;

    std::ostringstream ss;
    ss << std::setw(digits) << std::setfill('0') << otp;
    return ss.str();
}

} // namespace totp
