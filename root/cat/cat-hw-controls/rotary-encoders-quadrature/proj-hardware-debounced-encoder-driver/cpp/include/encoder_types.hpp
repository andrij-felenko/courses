#ifndef ENCODER_TYPES_HPP
#define ENCODER_TYPES_HPP

#include <cstdint>
#include <string_view>

namespace encoder {

// Режими квадратурного декодування
enum class DecodingMode {
    X1, // Зчитування за фронтом фази A (найменша роздільна здатність)
    X2, // Зчитування за обома фронтами фази A (середня роздільна здатність)
    X4  // Зчитування за всіма фронтами фаз A та B (квадро-роздільна здатність)
};

// Напрямок обертання вала енкодера
enum class Direction {
    None,            // Обертання відсутнє
    Clockwise,       // За годинниковою стрілкою (CW)
    CounterClockwise // Проти годинникової стрілки (CCW)
};

// Типи подій енкодера для зворотних викликів (Callbacks)
enum class EncoderEvent {
    PositionChanged, // Зміна позиції (крок CW або CCW)
    IndexTriggered,  // Фіксація нульової мітки Index (Z)
    VelocityUpdated  // Оновлення швидкості обертання
};

// Структура поточного стану енкодера
struct EncoderState {
    int32_t position{0};         // Поточна лічильна позиція у кроках
    Direction direction{Direction::None}; // Поточний напрямок
    float velocity_rpm{0.0f};    // Кутова швидкість в обертах на хвилину (RPM)
    bool index_active{false};    // Стан індексної мітки
};

// Перетворення напрямку у текстове позначення
constexpr std::string_view direction_to_string(Direction dir) noexcept {
    switch (dir) {
        case Direction::Clockwise:        return "CW (За стрілкою)";
        case Direction::CounterClockwise: return "CCW (Проти стрілки)";
        default:                          return "Стоїть";
    }
}

} // namespace encoder

#endif // ENCODER_TYPES_HPP
