#pragma once

#include <array>
#include <string_view>
#include <functional>
#include <cstdint>
#include <span>
#include <optional>

namespace Health {

inline constexpr uint16_t ScorePerfect = 1000;
inline constexpr uint16_t CriticalThreshold = 400;
inline constexpr uint16_t DegradedThreshold = 700;
inline constexpr uint16_t NominalThreshold = 900;
inline constexpr uint32_t WarmupTicks = 20;
inline constexpr uint32_t BlackboxMagic = 0xDEADBEEF;

enum class State : uint8_t {
    Nominal = 0,
    Degraded,
    Critical,
    Emergency
};

enum class BusStatus : uint8_t {
    Ok = 0,
    SdaStuckLow,
    SclStuckLow,
    Timeout,
    CrcError,
    BusOff
};

struct alignas(4) BlackboxEntry {
    uint32_t magic{BlackboxMagic};
    uint32_t seq_num{0};
    uint64_t timestamp_ms{0};
    uint16_t system_score{ScorePerfect};
    State    system_state{State::Nominal};
    uint8_t  fault_component_id{0xFF};
    uint32_t cfsr_reg{0};
    uint32_t hfsr_reg{0};
    uint32_t vdd_mv{3300};
    int16_t  core_temp_c{25};
    uint16_t min_stack_free_bytes{1024};
    uint32_t crc32{0};
};

struct ComponentDescriptor {
    std::string_view                             name{};
    std::function<uint16_t()>                    collector{};
    uint16_t                                     weight{10};
    bool                                         is_critical{false};
    uint16_t                                     smoothed_score{ScorePerfect};
    uint32_t                                     consecutive_failures{0};
};

template <size_t MaxComponents = 8, size_t BlackboxSlots = 16>
class Supervisor {
public:
    constexpr Supervisor() noexcept = default;

    bool register_component(std::string_view name,
                            std::function<uint16_t()> collector,
                            uint16_t weight,
                            bool is_critical) noexcept {
        if (component_count_ >= MaxComponents) {
            return false;
        }
        components_[component_count_++] = ComponentDescriptor{
            .name = name,
            .collector = std::move(collector),
            .weight = weight,
            .is_critical = is_critical,
            .smoothed_score = ScorePerfect,
            .consecutive_failures = 0
        };
        return true;
    }

    void tick(uint64_t timestamp_ms) noexcept;
    void log_emergency(uint8_t faulty_id, uint32_t cfsr, uint32_t hfsr, uint64_t timestamp_ms) noexcept;

    [[nodiscard]] uint16_t system_score() const noexcept { return system_score_; }
    [[nodiscard]] State state() const noexcept { return current_state_; }
    [[nodiscard]] std::span<const ComponentDescriptor> components() const noexcept {
        return std::span<const ComponentDescriptor>(components_.data(), component_count_);
    }
    [[nodiscard]] std::span<const BlackboxEntry> blackbox() const noexcept {
        return std::span<const BlackboxEntry>(blackbox_ring_.data(), BlackboxSlots);
    }

private:
    uint32_t calculate_crc32(const uint8_t *data, size_t length) const noexcept;

    std::array<ComponentDescriptor, MaxComponents> components_{};
    size_t                                         component_count_{0};
    uint16_t                                       system_score_{ScorePerfect};
    State                                          current_state_{State::Nominal};
    uint32_t                                       iteration_counter_{0};
    uint32_t                                       warmup_ticks_left_{WarmupTicks};

    std::array<BlackboxEntry, BlackboxSlots>       blackbox_ring_{};
    uint32_t                                       blackbox_head_{0};
    uint32_t                                       blackbox_seq_{0};
};

} // namespace Health
