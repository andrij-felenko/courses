#pragma once

#include <cstdint>

namespace auth {

class FlightArbiterFilter {
public:
    [[nodiscard]] constexpr bool is_manual_control_allowed(
        uint8_t src_gcs_id, 
        uint32_t nonce, 
        uint32_t now_ms
    ) const noexcept {
        if (commander_locked_) {
            return false;
        }
        if (now_ms > lease_deadline_ms_) {
            return false;
        }
        if (src_gcs_id != active_pilot_gcs_id_) {
            return false;
        }
        if (nonce != token_nonce_) {
            return false;
        }
        return true;
    }

private:
    uint8_t  active_pilot_gcs_id_{0};
    uint32_t token_nonce_{0};
    uint32_t lease_deadline_ms_{0};
    bool     commander_locked_{false};
};

} // namespace auth
