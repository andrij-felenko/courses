#ifndef PIN_DEBOUNCER_HPP
#define PIN_DEBOUNCER_HPP

#include <cstdint>

namespace encoder {

// Клас цифрового фільтра брязкоту контактів (Debouncer)
class PinDebouncer {
public:
    explicit PinDebouncer(uint32_t debounce_us = 50) noexcept;

    // Неблокуюче оновлення стану дискретного входу (вертає true якщо стан змінився)
    bool update(bool raw_state, uint64_t current_time_us) noexcept;

    // Отримання відфільтрованого стабільного стану входу
    [[nodiscard]] bool get_state() const noexcept;

    // Зміна часового вікна фільтрації
    void set_debounce_time(uint32_t debounce_us) noexcept;

private:
    uint32_t debounce_us_{50};
    uint64_t last_change_us_{0};
    bool raw_state_{false};
    bool stable_state_{false};
};

} // namespace encoder

#endif // PIN_DEBOUNCER_HPP
