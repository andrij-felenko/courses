#include <string_view>
#include <cstdint>
#include <optional>
#include <chrono>

struct ParamWriteTransaction {
    char param_id[17]{};
    float expected_value{0.0f};
    uint8_t param_type{0};
    std::chrono::steady_clock::time_point send_time;
    uint8_t retry_count{0};
    bool is_pending{false};

    [[nodiscard]] bool verify_ack(std::string_view recv_id, float recv_val) noexcept {
        if (!is_pending) return false;
        
        std::string_view current_id(param_id);
        if (current_id == recv_id) {
            is_pending = false;
            return true;
        }
        return false;
    }
};
