// Захист від циклічного перезавантаження: після кількох падінь поспіль пристрій
// має лишитися доступним для відладчика й оновлення, а не перезапускатися вічно.
#pragma once

#include <chrono>

namespace crash {

enum class BootDecision {
    Normal,  // звичайний старт: піднімаємо периферію й задачі
    SafeMode // приводи знеструмлені, задачі не стартують, чекаємо оновлення
};

[[nodiscard]] BootDecision decide();

// Лічильник гаситься лише після ТРИВАЛОЇ нормальної роботи: пристрій, який
// падає раз на десять хвилин, інакше ніколи не перетнув би поріг.
void note_uptime(std::chrono::milliseconds uptime);

[[noreturn]] void safe_mode();

} // namespace crash
