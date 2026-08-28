#include <string>
#include <string_view>
#include <cstdint>
#include <span>

namespace totp {

bool constant_time_equals(std::string_view a, std::string_view b) {
    if (a.size() != b.size()) return false;
    unsigned char result = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        result |= static_cast<unsigned char>(a[i]) ^ static_cast<unsigned char>(b[i]);
    }
    return result == 0;
}

struct VerificationResult {
    bool valid;
    std::int64_t verified_step;
};

VerificationResult verify_totp_code(
    std::string_view secret_base32,
    std::string_view user_input_code,
    std::int64_t current_timestamp,
    std::int64_t last_verified_step = 0,
    int window = 1,
    std::int64_t time_step = 30
) {
    if (user_input_code.size() != 6) {
        return {false, 0};
    }

    auto secret_bytes = decode_base32(secret_base32);
    std::int64_t current_step = current_timestamp / time_step;

    for (int offset = -window; offset <= window; ++offset) {
        std::int64_t step = current_step + offset;
        if (step <= last_verified_step) {
            continue;
        }

        std::string expected = generate_totp_code(secret_bytes, step * time_step, time_step, 6);
        if (constant_time_equals(user_input_code, expected)) {
            return {true, step};
        }
    }

    return {false, 0};
}

} // namespace totp
