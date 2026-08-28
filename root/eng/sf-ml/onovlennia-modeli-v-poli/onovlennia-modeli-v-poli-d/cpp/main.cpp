#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <cmath>
#include <expected>

namespace emb::ml {

inline constexpr uintptr_t kModelAAddr   = 0x080D8000U;
inline constexpr uintptr_t kModelBAddr   = 0x08158000U;
inline constexpr size_t    kMaxArenaSize = 48U * 1024U;

struct ShadowResult {
    float primary_prediction{0.0f};
    float shadow_prediction{0.0f};
    float absolute_divergence{0.0f};
    bool  shadow_valid{false};
};

class ModelRuntimeManager {
public:
    enum class ExecutionError : uint8_t {
        InvalidData,
        InferenceFault,
        CorruptedModel
    };

    explicit ModelRuntimeManager(uint8_t active_slot, bool enable_shadow = false)
        : shadow_active_(enable_shadow) {
        if (active_slot == 0) {
            active_addr_ = kModelAAddr;
            shadow_addr_ = kModelBAddr;
        } else {
            active_addr_ = kModelBAddr;
            shadow_addr_ = kModelAAddr;
        }
    }

    std::expected<ShadowResult, ExecutionError> execute_cycle(std::span<const int8_t> sensor_data) noexcept {
        if (sensor_data.empty()) {
            return std::unexpected(ExecutionError::InvalidData);
        }

        auto primary_res = invoke_inference(active_addr_, sensor_data);
        if (!primary_res) {
            return std::unexpected(ExecutionError::InferenceFault);
        }

        ShadowResult result{};
        result.primary_prediction = *primary_res;

        if (shadow_active_) {
            auto shadow_res = invoke_inference(shadow_addr_, sensor_data);
            if (shadow_res) {
                result.shadow_valid = true;
                result.shadow_prediction = *shadow_res;
                result.absolute_divergence = std::abs(result.primary_prediction - result.shadow_prediction);

                if (result.absolute_divergence < 0.25f) {
                    consecutive_valid_cycles_++;
                } else {
                    consecutive_valid_cycles_ = 0;
                }
            }
        }

        return result;
    }

    [[nodiscard]] uint32_t valid_cycles() const noexcept { return consecutive_valid_cycles_; }
    [[nodiscard]] bool is_ready_for_promotion() const noexcept { return consecutive_valid_cycles_ >= 1000U; }

private:
    static std::expected<float, ExecutionError> invoke_inference(uintptr_t base_addr,
                                                                 std::span<const int8_t> input) noexcept {
        constexpr size_t kHeaderSize = 128U;
        const auto* flatbuffer_data = reinterpret_cast<const uint8_t*>(base_addr + kHeaderSize);

        // Перевірка магічних байтів FlatBuffer ('TFL3')
        if (flatbuffer_data[4] != 'T' || flatbuffer_data[5] != 'F' ||
            flatbuffer_data[6] != 'L' || flatbuffer_data[7] != '3') {
            return std::unexpected(ExecutionError::CorruptedModel);
        }

        float acc = 0.0f;
        for (size_t i = 0; i < std::min(input.size(), size_t{32}); ++i) {
            acc += static_cast<float>(input[i]) * 0.03125f;
        }

        float score = 1.0f / (1.0f + std::exp(-acc));
        if (std::isnan(score)) {
            return std::unexpected(ExecutionError::InferenceFault);
        }
        return score;
    }

    uintptr_t active_addr_{0};
    uintptr_t shadow_addr_{0};
    bool shadow_active_{false};
    uint32_t consecutive_valid_cycles_{0};
};

} // namespace emb::ml
