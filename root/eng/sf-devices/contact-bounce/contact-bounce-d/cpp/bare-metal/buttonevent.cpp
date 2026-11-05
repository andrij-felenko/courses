#include <cstdint>
#include <array>

// Опис події кнопки у стилі C++17
struct ButtonEvent {
    uint8_t pin_id;
    bool is_pressed;
    uint32_t timestamp;
};

// Шаблонний клас дебаунсера з фіксованою глибиною фільтрації без використання vtable
template <size_t PinCount, uint8_t HistoryDepth = 8>
class HardwareDebouncer {
public:
    static_assert(HistoryDepth <= 16, "Глибина фільтрації не може перевищувати 16 біт");

    explicit HardwareDebouncer(uint16_t active_mask = 0xFFFF)
        : active_mask_(active_mask), stable_state_(active_mask) {
        history_.fill(0xFFFF);
    }

    // Метод обробки вхідного порту, викликаний із таймерного переривання
    inline uint16_t update(uint16_t raw_port_value) {
        uint16_t state_changed_mask = 0;
        constexpr uint16_t mask_match = (1U << HistoryDepth) - 1U;

        for (size_t i = 0; i < PinCount; ++i) {
            if ((active_mask_ & (1U << i)) == 0) continue;

            // Зсув історії та вставка нового зчитаного біта
            bool current_bit = (raw_port_value & (1U << i)) != 0;
            history_[i] = static_cast<uint16_t>((history_[i] << 1) | (current_bit ? 1U : 0U));

            uint16_t current_history = history_[i] & mask_match;

            // Перевірка стабільності: всі 1 або всі 0 в історії
            if (current_history == mask_match && !(stable_state_ & (1U << i))) {
                stable_state_ |= (1U << i);
                state_changed_mask |= (1U << i);
            } else if (current_history == 0 && (stable_state_ & (1U << i))) {
                stable_state_ &= ~(1U << i);
                state_changed_mask |= (1U << i);
            }
        }
        return state_changed_mask; // Повертає маску виводів, які змінили підтверджений стан
    }

    [[nodiscard]] constexpr uint16_t get_stable_state() const noexcept {
        return stable_state_;
    }

private:
    uint16_t active_mask_;
    uint16_t stable_state_;
    std::array<uint16_t, PinCount> history_;
};
