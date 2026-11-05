#include <cstdint>
#include <array>
#include <span>

template <std::size_t Depth>
class FlightRecorder {
public:
    struct Record {
        std::uint32_t timestamp_tick{0};
        std::uint32_t raw_vector{0};
        std::uint32_t suppress_vector{0};
        std::uint32_t final_vector{0};
        std::uint8_t  fsm_mode{0};
    };

    void log(std::uint32_t raw, std::uint32_t suppress, std::uint32_t final_vec, std::uint8_t mode, std::uint32_t tick) noexcept {
        if (frozen_) return;
        records_[head_] = Record{
            .timestamp_tick = tick,
            .raw_vector = raw,
            .suppress_vector = suppress,
            .final_vector = final_vec,
            .fsm_mode = mode
        };
        head_ = (head_ + 1U) % Depth;
    }

    void freeze() noexcept { frozen_ = true; }
    [[nodiscard]] bool isFrozen() const noexcept { return frozen_; }
    [[nodiscard]] std::span<const Record> getRecords() const noexcept { return records_; }

private:
    std::array<Record, Depth> records_{};
    std::size_t head_{0};
    bool frozen_{false};
};

class ShelveEscalationMonitor {
public:
    static constexpr std::uint32_t WARNING_LEVEL_BIT = (1U << 2);
    static constexpr std::uint32_t CRITICAL_LEVEL_BIT = (1U << 3);

    // Примусове скасування відкладення при переході з Warning у Critical
    [[nodiscard]] static std::uint32_t evaluateEscalation(std::uint32_t raw_vector, std::uint32_t shelved_vector) noexcept {
        std::uint32_t updated_shelved = shelved_vector;
        // Якщо тривога відкладена на рівні Warning, але виникла критична тривога того ж каналу
        if ((raw_vector & CRITICAL_LEVEL_BIT) != 0U) {
            updated_shelved &= ~WARNING_LEVEL_BIT; // Скасовуємо шелвінг Warning
            updated_shelved &= ~CRITICAL_LEVEL_BIT; // Критична тривога не може бути відкладена
        }
        return updated_shelved;
    }
};
