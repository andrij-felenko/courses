#include "quadrature_encoder.hpp"

namespace encoder {

// Реалізація PinDebouncer
PinDebouncer::PinDebouncer(uint32_t debounce_us) noexcept
    : debounce_us_(debounce_us) {}

bool PinDebouncer::update(bool raw_state, uint64_t current_time_us) noexcept {
    if (raw_state != raw_state_) {
        raw_state_ = raw_state;
        last_change_us_ = current_time_us;
    }

    if ((current_time_us - last_change_us_) >= debounce_us_) {
        if (stable_state_ != raw_state_) {
            stable_state_ = raw_state_;
            return true; // Стан стабілізувався і змінився
        }
    }
    return false;
}

bool PinDebouncer::get_state() const noexcept {
    return stable_state_;
}

void PinDebouncer::set_debounce_time(uint32_t debounce_us) noexcept {
    debounce_us_ = debounce_us;
}


// Реалізація QuadratureEncoder
QuadratureEncoder::QuadratureEncoder(uint32_t ppr, DecodingMode mode, uint32_t debounce_us) noexcept
    : ppr_(ppr), mode_(mode),
      pin_a_filter_(debounce_us),
      pin_b_filter_(debounce_us),
      pin_index_filter_(debounce_us) {}

void QuadratureEncoder::update(bool raw_pin_a, bool raw_pin_b, bool raw_pin_index, uint64_t current_time_us) {
    bool change_a = pin_a_filter_.update(raw_pin_a, current_time_us);
    bool change_b = pin_b_filter_.update(raw_pin_b, current_time_us);
    bool change_idx = pin_index_filter_.update(raw_pin_index, current_time_us);

    // Зчитування стабільних фазових станів
    bool state_a = pin_a_filter_.get_state();
    bool state_b = pin_b_filter_.get_state();
    uint8_t current_quad_state = (static_cast<uint8_t>(state_a) << 1) | static_cast<uint8_t>(state_b);

    // Якщо відбулася зміна на фазових лініях A або B
    if (change_a || change_b) {
        process_state_transition(last_quad_state_, current_quad_state);
        last_quad_state_ = current_quad_state;
    }

    // Обробка спрацьовування індексної мітки Z (Index)
    if (change_idx && pin_index_filter_.get_state()) {
        state_.index_active = true;
        reset_position();
        notify_event(EncoderEvent::IndexTriggered);
    } else {
        state_.index_active = false;
    }

    // Періодичний розрахунок швидкості обертання (кожні 10 мс = 10000 мкс)
    if (current_time_us - last_velocity_calc_us_ >= 10000) {
        calculate_velocity(current_time_us);
    }
}

void QuadratureEncoder::process_state_transition(uint8_t old_state, uint8_t new_state) {
    // Таблиця рішень квадратурного фазового зсуву (-1: CCW, +1: CW, 0: Недійсний крок)
    static constexpr int8_t quad_table[4][4] = {
        {  0,  1, -1,  0 }, // 00 -> 00(0), 01(+1), 10(-1), 11(0)
        { -1,  0,  0,  1 }, // 01 -> 00(-1), 01(0),  10(0),  11(+1)
        {  1,  0,  0, -1 }, // 10 -> 00(+1), 01(0),  10(0),  11(-1)
        {  0, -1,  1,  0 }  // 11 -> 00(0), 01(-1), 10(+1), 11(0)
    };

    int8_t step = quad_table[old_state & 0x03][new_state & 0x03];
    if (step == 0) return;

    // Ураховуємо режим квадратурного декодування
    bool apply_step = false;
    switch (mode_) {
        case DecodingMode::X4:
            apply_step = true; // Кожен фронт A та B
            break;
        case DecodingMode::X2:
            apply_step = (new_state == 0b00 || new_state == 0b11 || old_state == 0b00 || old_state == 0b11);
            break;
        case DecodingMode::X1:
            apply_step = (old_state == 0b00 && new_state == 0b10) || (old_state == 0b11 && new_state == 0b01);
            break;
    }

    if (apply_step) {
        state_.position += step;
        state_.direction = (step > 0) ? Direction::Clockwise : Direction::CounterClockwise;
        notify_event(EncoderEvent::PositionChanged);
    }
}

void QuadratureEncoder::calculate_velocity(uint64_t current_time_us) noexcept {
    uint64_t delta_t_us = current_time_us - last_velocity_calc_us_;
    if (delta_t_us == 0) return;

    int32_t delta_pos = state_.position - last_velocity_pos_;
    
    // Перетворення кроків у оберти за хвилину (RPM)
    float pulses_per_rev = static_cast<float>(ppr_ * (mode_ == DecodingMode::X4 ? 4 : (mode_ == DecodingMode::X2 ? 2 : 1)));
    float revs = static_cast<float>(delta_pos) / pulses_per_rev;
    float time_minutes = static_cast<float>(delta_t_us) / 60000000.0f;

    state_.velocity_rpm = revs / time_minutes;

    last_velocity_calc_us_ = current_time_us;
    last_velocity_pos_ = state_.position;

    notify_event(EncoderEvent::VelocityUpdated);
}

void QuadratureEncoder::set_event_callback(EventCallback callback) {
    event_callback_ = std::move(callback);
}

std::optional<EncoderState> QuadratureEncoder::get_state() const noexcept {
    return state_;
}

void QuadratureEncoder::reset_position() noexcept {
    state_.position = 0;
    last_velocity_pos_ = 0;
}

void QuadratureEncoder::set_decoding_mode(DecodingMode mode) noexcept {
    mode_ = mode;
}

void QuadratureEncoder::notify_event(EncoderEvent event) {
    if (event_callback_) {
        event_callback_(event, state_);
    }
}

} // namespace encoder
