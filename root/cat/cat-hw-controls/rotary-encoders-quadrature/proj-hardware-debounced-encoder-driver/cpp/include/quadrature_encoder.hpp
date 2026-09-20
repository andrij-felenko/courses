#ifndef QUADRATURE_ENCODER_HPP
#define QUADRATURE_ENCODER_HPP

#include "encoder_types.hpp"
#include "pin_debouncer.hpp"
#include <functional>
#include <optional>
#include <cstdint>

namespace encoder {

// Головний C++17 клас інкрементального квадратурного енкодера
class QuadratureEncoder {
public:
    using EventCallback = std::function<void(EncoderEvent, const EncoderState&)>;

    explicit QuadratureEncoder(uint32_t ppr = 1000, 
                              DecodingMode mode = DecodingMode::X4,
                              uint32_t debounce_us = 20) noexcept;

    // Неблокуючий цикл оновлення (викликається у головному циклі або таймері)
    void update(bool raw_pin_a, bool raw_pin_b, bool raw_pin_index, uint64_t current_time_us);

    // Реєстрація користувацької функцій зворотного виклику (Callback)
    void set_event_callback(EventCallback callback);

    // Отримання поточного стану (вертає std::optional)
    [[nodiscard]] std::optional<EncoderState> get_state() const noexcept;

    // Скидання лічильника позиції в нуль
    void reset_position() noexcept;

    // Налаштування роздільної здатності декодування
    void set_decoding_mode(DecodingMode mode) noexcept;

private:
    uint32_t ppr_{1000};
    DecodingMode mode_{DecodingMode::X4};

    PinDebouncer pin_a_filter_;
    PinDebouncer pin_b_filter_;
    PinDebouncer pin_index_filter_;

    uint8_t last_quad_state_{0};
    EncoderState state_{};

    uint64_t last_velocity_calc_us_{0};
    int32_t last_velocity_pos_{0};

    EventCallback event_callback_{nullptr};

    void process_state_transition(uint8_t old_state, uint8_t new_state);
    void calculate_velocity(uint64_t current_time_us) noexcept;
    void notify_event(EncoderEvent event);
};

} // namespace encoder

#endif // QUADRATURE_ENCODER_HPP
