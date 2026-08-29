#include "pin_isolation.hpp"

namespace lowpower {
namespace {

// Порти, які ізолюються. Порядок збігається з порядком у saved_.
mcu::GpioBlock* ports[] = {&mcu::gpioa(), &mcu::gpiob(), &mcu::gpioc()};

// Розгортає маску виводів у маску двобітових полів MODER/PUPDR.
[[nodiscard]] mcu::u32 to_field_mask(mcu::u32 pin_mask) noexcept
{
    mcu::u32 fields = 0U;
    for (unsigned pin = 0; pin < 16; ++pin) {
        if ((pin_mask & (1U << pin)) != 0U) { fields |= 0b11U << (pin * 2U); }
    }
    return fields;
}

} // namespace

mcu::u32 PinIsolator::keep_mask(const mcu::GpioBlock& port) const noexcept
{
    mcu::u32 mask = 0U;
    for (const auto& pin : keep_) {
        if (&pin.port() == &port) { mask |= pin.mask(); }
    }
    return mask;
}

void PinIsolator::isolate() noexcept
{
    for (std::size_t n = 0; n < saved_.size(); ++n) {
        auto& port = *ports[n];
        saved_[n] = PortState{port.moder, port.pupdr, port.odr};

        const auto fields = to_field_mask(keep_mask(port));

        // Спершу MODER, потім PUPDR — і це не дрібниця. Аналоговий режим
        // від'єднує вхідний буфер; якщо зняти підтяжку раніше, вивід лишиться
        // цифровим входом із плаваючим рівнем і почне сіпатися біля порога, а
        // кожне сіпання це наскрізний струм у вхідному інверторі.
        port.moder = (saved_[n].moder & fields) | (~fields);
        port.pupdr = saved_[n].pupdr & fields;  // решта — без підтяжки
    }

    // Сигнальні лінії шин уже відпущено в Hi-Z у quiesce_all() — саме
    // відпущено, а не зведено в нуль. Нуль можна давати лише поки датчик
    // живиться; після розмикання ключа він стає стоком для заряду ємностей.

    // Поки в DBGMCU_CR стоять біти налагодження, ядро в Stop лишає ввімкненим
    // тактове дерево налагодження: плата спить, а споживає міліампери. На
    // столі це ховається за струмом самого налагоджувача.
    mcu::clear_bits(mcu::dbgmcu_cr(),
                    mcu::bits::kDbgSleep | mcu::bits::kDbgStop | mcu::bits::kDbgStandby);

    isolated_ = true;
}

void PinIsolator::restore() noexcept
{
    if (!isolated_) { return; }  // прокинулися не зі сну — відновлювати нічого

    for (std::size_t n = 0; n < saved_.size(); ++n) {
        auto& port = *ports[n];
        const auto keep = keep_mask(port);

        // Рівні виходів повертаємо ДО режимів: інакше вивід на мить стане
        // виходом зі старим вмістом засувки й смикне лінію. Виводи зі списку
        // винятків не спали, тому їхній поточний рівень свіжіший за збережений.
        port.odr = (saved_[n].odr & ~keep) | (port.odr & keep);
        port.pupdr = saved_[n].pupdr;
        port.moder = saved_[n].moder;
    }

    isolated_ = false;
}

} // namespace lowpower
