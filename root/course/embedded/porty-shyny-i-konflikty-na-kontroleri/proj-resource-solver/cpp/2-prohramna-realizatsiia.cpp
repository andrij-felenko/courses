#include <cstdint>
#include <string_view>
#include <span>
#include <array>
#include <expected>
#include <optional>

enum class ProtocolType : uint8_t {
    None = 0,
    DShot600,
    DShot300,
    PwmServo,
    Ws2812Led,
    SpiImu,
    UartTelemetry
};

enum class ValidationError {
    TimerProtocolConflict,
    DmaStreamCollision,
    ImuResourceMissing,
    InvalidTimerIndex,
    InvalidDmaIndex
};

struct PinResource {
    std::string_view pin_name;
    uint8_t timer_id{0};          // 1 = TIM1..8 = TIM8 (0 = none)
    uint8_t timer_channel{0};     // 1..4
    uint8_t dma_controller{0};    // 1..2
    uint8_t dma_stream{0};        // 0..7
    uint8_t alt_dma_stream{0xFF}; // 0..7 (0xFF = none)
    uint8_t dma_channel{0};       // 0..7
    ProtocolType protocol{ProtocolType::None};
};

struct TimerDomain {
    ProtocolType protocol{ProtocolType::None};
    uint8_t active_channels_mask{0};
    bool is_locked{false};
};

struct DmaStreamAllocation {
    bool is_allocated{false};
    std::string_view owner_pin{};
    ProtocolType protocol{ProtocolType::None};
};

class HardwareResourceManager {
public:
    static constexpr size_t MaxTimers = 8;
    static constexpr size_t DmaControllers = 2;
    static constexpr size_t DmaStreamsPerCtrl = 8;

    constexpr HardwareResourceManager() = default;

    [[nodiscard]] std::expected<size_t, ValidationError> validate_and_resolve(
        std::span<PinResource> pins) noexcept {
        
        bool has_imu = false;
        size_t resolved_collisions = 0;

        for (auto& pin : pins) {
            if (pin.protocol == ProtocolType::None) {
                continue;
            }

            if (pin.protocol == ProtocolType::SpiImu) {
                has_imu = true;
            }

            // 1. Валідація таймерних доменів
            if (pin.timer_id > 0) {
                if (pin.timer_id > MaxTimers) {
                    return std::unexpected(ValidationError::InvalidTimerIndex);
                }
                auto& domain = timers_[pin.timer_id - 1];
                if (!domain.is_locked) {
                    domain.protocol = pin.protocol;
                    domain.is_locked = true;
                    domain.active_channels_mask |= (1 << (pin.timer_channel - 1));
                } else if (domain.protocol != pin.protocol) {
                    return std::unexpected(ValidationError::TimerProtocolConflict);
                } else {
                    domain.active_channels_mask |= (1 << (pin.timer_channel - 1));
                }
            }

            // 2. Валідація та автоматичне розв'язання потоків DMA
            if (pin.dma_controller >= 1 && pin.dma_controller <= DmaControllers) {
                if (pin.dma_stream >= DmaStreamsPerCtrl) {
                    return std::unexpected(ValidationError::InvalidDmaIndex);
                }
                auto& dma = dma_matrix_[pin.dma_controller - 1][pin.dma_stream];
                if (dma.is_allocated) {
                    // Спроба розв'язання через альтернативний потік
                    if (pin.alt_dma_stream != 0xFF && pin.alt_dma_stream < DmaStreamsPerCtrl) {
                        auto& alt_dma = dma_matrix_[pin.dma_controller - 1][pin.alt_dma_stream];
                        if (!alt_dma.is_allocated) {
                            alt_dma.is_allocated = true;
                            alt_dma.owner_pin = pin.pin_name;
                            alt_dma.protocol = pin.protocol;
                            pin.dma_stream = pin.alt_dma_stream;
                            resolved_collisions++;
                            continue;
                        }
                    }
                    return std::unexpected(ValidationError::DmaStreamCollision);
                }
                dma.is_allocated = true;
                dma.owner_pin = pin.pin_name;
                dma.protocol = pin.protocol;
            }
        }

        if (!has_imu) {
            return std::unexpected(ValidationError::ImuResourceMissing);
        }

        return resolved_collisions;
    }

private:
    std::array<TimerDomain, MaxTimers> timers_{};
    std::array<std::array<DmaStreamAllocation, DmaStreamsPerCtrl>, DmaControllers> dma_matrix_{};
};
