// Фільтрація кадру в обробнику вхідних пакетів мовою C++20
#include <cstdint>
#include <concepts>

namespace safety {

constexpr uint8_t BroadcastId = 0xFF;
constexpr uint16_t CriticalCommandThreshold = 0x0100;

enum class State : uint8_t {
    Idle = 0,
    Armed = 1
};

struct RxFrame {
    uint8_t target_id{0};
    uint16_t cmd_code{0};
    uint32_t sbo_token{0};

    [[nodiscard]] constexpr bool is_broadcast() const noexcept {
        return target_id == BroadcastId;
    }

    [[nodiscard]] constexpr bool is_critical() const noexcept {
        return cmd_code >= CriticalCommandThreshold;
    }
};

struct GateState {
    State state{State::Idle};
    uint32_t active_token{0};
};

[[nodiscard]] constexpr bool validate_packet(const RxFrame& pkt, 
                                            uint8_t my_id, 
                                            const GateState& gate) noexcept {
    // Ступінь 1: Перевірка адреси
    if (pkt.is_broadcast()) {
        if (pkt.is_critical()) {
            return false; // Заборона критичної дії на широкомовну адресу
        }
    } else if (pkt.target_id != my_id) {
        return false; // Чужий пакет, ігноруємо
    }

    // Ступінь 2: Перевірка транзакційного стану SBO
    if (pkt.is_critical()) {
        if (gate.state != State::Armed) {
            return false; // Спроба прямої дії без вибору цілі
        }
        if (pkt.sbo_token != gate.active_token) {
            return false; // Недійсний токен
        }
    }

    return true;
}

} // namespace safety
