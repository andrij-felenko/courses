#include <string_view>
#include <cstdint>

namespace totp {

struct ResyncResult {
    bool success;
    int drift_offset;
};

ResyncResult resynchronize_clock(
    std::string_view secret_base32,
    std::string_view code1,
    std::string_view code2,
    std::int64_t current_timestamp,
    int max_drift_steps = 50,
    std::int64_t time_step = 30
) {
    auto secret_bytes = decode_base32(secret_base32);
    std::int64_t current_step = current_timestamp / time_step;

    for (int drift = -max_drift_steps; drift <= max_drift_steps; ++drift) {
        std::string exp1 = generate_totp_code(secret_bytes, (current_step + drift) * time_step, time_step, 6);
        std::string exp2 = generate_totp_code(secret_bytes, (current_step + drift + 1) * time_step, time_step, 6);

        if (constant_time_equals(code1, exp1) && constant_time_equals(code2, exp2)) {
            return {true, drift};
        }
    }

    return {false, 0};
}

} // namespace totp
