// app.cpp — прикладна програма, яка доводить, що середовище розгорнуте.
//
// Кожен об'єкт тут перевіряє свій крок стартового коду: g_boot_pattern лежить
// у .data, g_zero_probe — у .bss, а g_witness існує лише тому, що Reset_Handler
// обійшов .init_array і викликав конструктор.

#include <array>
#include <cstdint>
#include <memory>

#include "mcu/linker_symbols.hpp"
#include "mcu/scb.hpp"

namespace {

// .data: значення могло взятися лише з Flash.
volatile std::uint32_t g_boot_pattern = 0xA5A5A5A5u;

// .bss: місце, яке стартовий код мусив занулити. Тут саме сирий масив, а не
// std::array: у контейнера немає operator[] для volatile-об'єкта, і читання
// «як воно є просто зараз» довелося б підпирати приведеннями.
volatile std::uint8_t g_zero_probe[64]{};

// Об'єкт із НЕсталим конструктором: значення CPACR відоме лише в момент
// виконання, тож компілятор не має права порахувати його наперед і покласти
// готовим у .data. Через це в .init_array з'являється запис — рівно той, який
// обходить стартовий код.
class BootWitness {
public:
    BootWitness() noexcept
        : magic_{0x00C0FFEEu}, cpacr_at_construction_{mcu::cpacr::load()}
    {
    }

    bool constructed() const noexcept { return magic_ == 0x00C0FFEEu; }

    // Конструктори виконуються ПІСЛЯ enable_fpu(), тож співпроцесор тут уже
    // мав бути ввімкнений. Якщо ні — порядок кроків у Reset_Handler порушено.
    bool fpu_was_enabled() const noexcept
    {
        return (cpacr_at_construction_ & mcu::bits::cp10_cp11_full) ==
               mcu::bits::cp10_cp11_full;
    }

private:
    std::uint32_t magic_;
    std::uint32_t cpacr_at_construction_;
};

BootWitness g_witness;

}  // namespace

// Ознаки для налагоджувача: під GDB достатньо `set var g_trigger_fault = 1`,
// щоб побачити роботу діагностичного обробника на живому збої.
volatile int g_trigger_fault;
volatile std::uint32_t g_checks_failed;
volatile std::size_t g_heap_used;

namespace {

// Кожен біт результату — свій провалений крок стартового коду.
std::uint32_t verify_environment() noexcept
{
    std::uint32_t failed = 0;

    if (g_boot_pattern != 0xA5A5A5A5u) {
        failed |= 1u << 0;   // .data не скопійовано з Flash
    }

    for (std::size_t i = 0; i < sizeof(g_zero_probe); ++i) {
        if (g_zero_probe[i] != 0) {
            failed |= 1u << 1;   // .bss не занулено
            break;
        }
    }

    if (!g_witness.constructed()) {
        failed |= 1u << 2;   // .init_array не пройдено
    }

    if (!g_witness.fpu_was_enabled()) {
        failed |= 1u << 3;   // FPU увімкнули після конструкторів або не увімкнули
    }

    // Купа: unique_ptr бере пам'ять через operator new → malloc → _sbrk і
    // повертає її сам. Розмір помітний, але явно менший за _Min_Heap_Size.
    {
        auto block = std::make_unique<std::array<std::uint8_t, 256>>();
        block->fill(0x5A);
        g_heap_used = mcu::linker::heap_used();
        if (g_heap_used == 0 || (*block)[255] != 0x5A) {
            failed |= 1u << 4;
        }
    }

    return failed;
}

// Ділення на нуль. Дільник volatile, інакше компілятор порахував би все на
// етапі збирання й ніякого винятку в прошивці не сталося б.
void divide_by_zero() noexcept
{
    volatile int divisor = 0;
    volatile int result = 1 / divisor;
    static_cast<void>(result);
}

}  // namespace

int main()
{
    g_checks_failed = verify_environment();

    // Перша ж інструкція з рухомою комою перевіряє FPU не за регістром, а по
    // ділу: при вимкненому CP10 тут був би UsageFault з ознакою NOCP.
    volatile float x = 1.0f;
    x /= 3.0f;

    for (;;) {
        if (g_trigger_fault != 0) {
            g_trigger_fault = 0;
            divide_by_zero();
        }
        mcu::wait_for_interrupt();
    }
}
