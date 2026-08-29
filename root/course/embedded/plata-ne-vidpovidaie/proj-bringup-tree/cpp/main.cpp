// Bring-up Test Runner: чотири фази підряд, без RTOS і без стеків протоколів.
// Кожна фаза відпрацьовує незалежно від попередньої — мертвий кварц не має
// ховати від нас справний GPIO чи справну шину.
#include "bringup.hpp"

// Звіт лежить у ОЗП під зовнішнім символом: у GDB це `p g_report`.
// Прошивка нічого не друкує — на першому ввімкненні друкувати ще нікуди.
bringup::Report g_report{};

namespace {

// ~2 с меандру 100 кГц: вистачає, щоб спокійно обійти щупом усі майданчики.
constexpr std::uint32_t testpoint_cycles = 100'000U;
constexpr std::uint32_t heartbeat_cycles = 1'000U;
constexpr std::uint32_t heartbeat_pause_us = 200'000U;

}  // namespace

int main()
{
    // Фаза 1: тактові домени.
    if (auto clocks = bringup::verify_clocks(); clocks) {
        g_report.clocks = *clocks;
    } else {
        g_report.clock_error = clocks.error();
    }

    // Фаза 2: контрольні майданчики. Виконуємо навіть після провалу HSE —
    // на HSI ядро живе, а цілісність доріжок від кварцу не залежить.
    bringup::exercise_testpoints(bringup::default_testpoints(), testpoint_cycles);

    // Фаза 3: шина. Об'єкт живе рівно стільки, скільки триває сканування, —
    // на виході з if модуль сам вимикається й відпускає лінії.
    if (auto bus = bringup::I2cBus::open(); bus) {
        g_report.i2c_bus_was_stuck = bus->bus_was_stuck();
        if (auto found = bus->scan(g_report.i2c_addresses); found) {
            g_report.i2c_found = *found;
        } else {
            g_report.i2c_error = found.error();
        }
    } else {
        g_report.i2c_bus_was_stuck = true;
        g_report.i2c_error = bus.error();
    }

    // Фаза 4: опорне джерело й реальна напруга аналогового живлення.
    if (auto supply = bringup::measure_vdda(); supply) {
        g_report.supply = *supply;
    } else {
        g_report.supply_error = supply.error();
    }

    // Дійшли до кінця — показуємо це коротким пакетом імпульсів раз на
    // 200 мс: з осцилографа видно, що прошивка не зависла посеред фази.
    for (;;) {
        bringup::exercise_testpoints(bringup::default_testpoints(), heartbeat_cycles);
        bringup::mmio::delay_us(heartbeat_pause_us);
    }
}
