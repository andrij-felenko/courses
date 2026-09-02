// main.cpp — той самий порядок запуску, що й у C-версії: безпечний рівень
// раніше за напрямок, перевірка проводки раніше за перший обмін. Різниця в
// тому, що тут порядок тримають типи, а не дисципліна автора.
//
// Плата: світлодіод PC13 (активний нуль), релейний модуль PB0 (активний нуль),
// шина I2C PB8/PB9 із зовнішніми підтяжками 4.7 кОм.
#include "hw/load_output.hpp"
#include "hw/open_drain.hpp"

#include <cstddef>
#include <string_view>

namespace {

using LedPin   = hw::Pin<hw::Port::C, 13>;
using RelayPin = hw::Pin<hw::Port::B, 0>;
using SclPin   = hw::Pin<hw::Port::B, 8>;
using SdaPin   = hw::Pin<hw::Port::B, 9>;

using Led   = hw::LoadOutput<LedPin, hw::Polarity::ActiveLow>;
using Relay = hw::LoadOutput<RelayPin, hw::Polarity::ActiveLow>;

// Друкувати нікуди, тож причину зупинки лишаємо в пам'яті — її видно в GDB.
volatile int g_faultCode = 0;
// Класи під volatile не кладуться, тому текст зберігаємо як пару
// «вказівник + довжина»: обидва поля читаються відлагоджувачем.
const char* volatile g_faultText = nullptr;
volatile std::size_t g_faultLen = 0;

[[noreturn]] void halt(int code, std::string_view text) noexcept
{
    // Об'єкти виходів до цієї точки вже зруйновані або зруйнуються разом зі
    // стеком — навантаження вимкнене без жодного рядка «не забудь вимкнути».
    g_faultCode = code;
    g_faultText = text.data();
    g_faultLen = text.size();
    for (;;) {
    }
}

// Лінія справді керована? Притиснути → нуль, відпустити → одиниця за
// відведений час. Так видно завелику підтяжку або зайву ємність шини.
[[nodiscard]] bool wiggle(hw::OpenDrainLine<SdaPin>& line) noexcept
{
    {
        const auto low = line.hold();
        line.settle();
        if (line.level()) {
            return false;
        }
    } // тут лінія відпускається сама

    line.settle();
    return line.level();
}

} // namespace

int main()
{
    auto led = Led::create(hw::Speed::Low);
    if (!led) {
        halt(1, hw::describe(led.error()));
    }

    auto relay = Relay::create(hw::Speed::Low);
    if (!relay) {
        halt(2, hw::describe(relay.error()));
    }

    auto scl = hw::OpenDrainLine<SclPin>::create(hw::Speed::Medium);
    if (!scl) {
        halt(3, hw::describe(scl.error()));
    }

    auto sda = hw::OpenDrainLine<SdaPin>::create(hw::Speed::Medium);
    if (!sda) {
        halt(4, hw::describe(sda.error()));
    }

    if (auto wiring = scl->checkWiring(); !wiring) {
        halt(5, hw::describe(wiring.error()));
    }
    if (auto wiring = sda->checkWiring(); !wiring) {
        halt(6, hw::describe(wiring.error()));
    }
    if (!wiggle(*sda)) {
        halt(7, "фронт SDA не встигає за відведений час");
    }

    // Робочий цикл: індикатор блимає, реле отримує короткий імпульс і довгу
    // паузу — механіка не любить швидкого клацання, а живлення не любить
    // пускового струму котушки.
    for (unsigned tick = 0;; ++tick) {
        led->toggle();

        if (tick % 40u == 0u) {
            const auto pulse = relay->pulse(); // вимкнеться на виході з блоку
            hw::spin(1'600'000u);
        } else {
            hw::spin(400'000u);
        }
    }
}
