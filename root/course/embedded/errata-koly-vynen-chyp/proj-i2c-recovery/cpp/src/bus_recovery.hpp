#pragma once

#include <cstdint>
#include <expected>

namespace hw {

enum class BusFault : std::uint8_t {
    SclStuckLow,   /* такт не піднімається: вічне розтягування або КЗ на землю */
    SdaStuckLow,   /* дев'ять тактів не звільнили дані: мертвий чип або КЗ */
};

struct RecoveryReport {
    std::uint8_t pulses;   /* скільки тактів довелося видати; 0 — шина була вільна */
};

/* П'ять кроків процедури: скидання модуля через RCC, перехоплення виводів у
   GPIO Open-Drain, до дев'яти ручних тактів SCL, ручний STOP, перевірка ліній.
   Успіх означає, що виводи вже повернуто в Alternate Function, а модуль виведено
   зі скидання й він чекає на конструктор I2c1. Помилка лишає модуль У СКИДАННІ:
   на фізично зіпсованій шині вмикати передавач нічого. */
[[nodiscard]] std::expected<RecoveryReport, BusFault> recover_i2c1_bus() noexcept;

} // namespace hw
