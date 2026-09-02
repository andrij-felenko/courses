#pragma once

#include <cstdint>
#include <string_view>

namespace input {

/* Семантика введення, а не стан пінів. enum class замість голого enum:
   подію кнопки не переплутаєш із кодом клавіші чи індексом меню. */
enum class EventType : std::uint8_t {
    None = 0,
    ButtonPress,           // контакт замкнувся й рівень стабільний
    ButtonRelease,         // контакт розімкнувся й рівень стабільний
    ButtonShortClick,      // натиснули й відпустили, другого не було
    ButtonDoubleClick,     // друге натискання вклалося у вікно
    ButtonLongPressStart,  // утримання перетнуло поріг
    ButtonLongPressHold,   // утримання триває
    ButtonRepeat,          // автоповтор із розгоном
    EncoderCW,             // один клац за годинниковою
    EncoderCCW             // один клац проти годинникової
};

/* Тривіально копійовна структура без покажчиків усередину: черга зберігає
   значення, а не посилання на чужу пам'ять. */
struct InputEvent {
    std::uint8_t  id{0};
    EventType     type{EventType::None};
    std::uint16_t durationMs{0};
};

constexpr std::string_view name(EventType type) noexcept {
    switch (type) {
    case EventType::ButtonPress:          return "PRESS";
    case EventType::ButtonRelease:        return "RELEASE";
    case EventType::ButtonShortClick:     return "SHORT_CLICK";
    case EventType::ButtonDoubleClick:    return "DOUBLE_CLICK";
    case EventType::ButtonLongPressStart: return "LONG_PRESS_START";
    case EventType::ButtonLongPressHold:  return "LONG_PRESS_HOLD";
    case EventType::ButtonRepeat:         return "REPEAT";
    case EventType::EncoderCW:            return "ENCODER_CW";
    case EventType::EncoderCCW:           return "ENCODER_CCW";
    case EventType::None:                 break;
    }
    return "NONE";
}

}  // namespace input
