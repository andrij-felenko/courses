// main.cpp — порядок дій на старті: спершу дізнатися, ЧОМУ ми тут,
// потім налаштувати діагностику, і лише потім робити щось корисне.
#include "fault_report.hpp"
#include "reset_cause.hpp"
#include "trace.hpp"

#include "stm32f4xx.h"

namespace {

enum class DemoFault {
    divide_by_zero,
    unaligned,
    bad_address,
    undefined_instruction,
};

constexpr DemoFault k_demo = DemoFault::bad_address;

void provoke(DemoFault kind)
{
    switch (kind) {
    case DemoFault::divide_by_zero: {
        // volatile, щоб компілятор не порахував це сам і не викинув ділення.
        volatile int divisor = 0;
        volatile int result = 42 / divisor;
        static_cast<void>(result);
        break;                                  // → UsageFault: DIVBYZERO
    }
    case DemoFault::unaligned: {
        // Адреса в RAM, зсунута на байт: при UNALIGN_TRP=1 звичайний STR
        // теж стає збоєм.
        auto* misaligned = reinterpret_cast<volatile std::uint32_t*>(SRAM_BASE + 1u);
        *misaligned = 0xDEADBEEFu;
        break;                                  // → UsageFault: UNALIGNED
    }
    case DemoFault::bad_address: {
        // Дірка в карті адрес: читання не знаходить ані пам'яті, ані
        // периферії, і шина відповідає помилкою.
        const volatile std::uint32_t value = *reinterpret_cast<volatile std::uint32_t*>(0xCC000000u);
        static_cast<void>(value);
        break;                                  // → BusFault: PRECISERR + BFARVALID
    }
    case DemoFault::undefined_instruction:
        asm volatile(".short 0xDE00");          // UDF #0 — навмисно недійсний опкод
        break;                                  // → UsageFault: UNDEFINSTR
    }
}

}  // namespace

int main()
{
    // Крок 1. Причину скидання читаємо ПЕРШОЮ дією: прапорці липкі, і поки
    // ми їх не стерли, вони описують попередній прогін, а не цей.
    const reset::Status status = reset::Status::capture();

    trace::out() << "\n--- старт прошивки ---\n";
    status.report();

    // Крок 2. Діагностичне середовище — до першого власного коду, інакше
    // ранній збій прийде як безіменний HardFault.
    fault::init_diagnostics();

    // Крок 3. Демонстрація: валимо ядро наперед відомим способом і дивимось,
    // що саме покаже розбір регістрів.
    trace::out() << "Провокуємо збій...\n";
    provoke(k_demo);

    // Сюди керування не повертається: provoke() гарантовано впаде,
    // а fault::report() зупиняє або перезавантажує ядро.
    trace::out() << "ПОМИЛКА: збою не сталося — перевір, чи ввімкнено пастки в CCR\n";
    for (;;) {
    }
}
