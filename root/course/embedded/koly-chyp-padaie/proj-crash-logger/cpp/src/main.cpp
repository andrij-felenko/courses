// Аварійний реєстратор у зборі: після кожного скидання прошивка спершу каже,
// ЧОМУ вона перезапустилася, і лише потім береться до роботи.
#include <chrono>
#include <cstdint>

#include "crash_record.hpp"
#include "fault_capture.hpp"
#include "fault_decode.hpp"
#include "recovery.hpp"
#include "stm32f4xx.h"
#include "sync_uart.hpp"

namespace {

constexpr std::uint32_t kSysclkHz = 168'000'000;
constexpr std::uint32_t kPclk2Hz = 84'000'000;

constexpr std::uint32_t kResetIwdg = 1u << 29;
constexpr std::uint32_t kResetWwdg = 1u << 30;

volatile std::uint32_t g_uptime_ms = 0;

// Чотири способи зламати чип — кожен вмикає свій біт CFSR, і звіт після
// перезапуску показує, який саме.
void provoke_bus_fault()
{
    auto* bad = reinterpret_cast<volatile std::uint32_t*>(0xCCCC'CCCC);
    static_cast<void>(*bad);
}

void provoke_div_by_zero()
{
    volatile int zero = 0;
    volatile int result = 42 / zero;
    static_cast<void>(result);
}

void provoke_invalid_state()
{
    // Адреса без біта Thumb: ядро відмовиться туди переходити (INVSTATE).
    auto bad_call = reinterpret_cast<void (*)()>(0x2000'0000);
    bad_call();
}

void provoke_unaligned()
{
    auto* odd = reinterpret_cast<volatile std::uint32_t*>(0x2000'0002);
    *odd = 1;
}

void print_menu()
{
    static_cast<void>(io::console::write(
        "[menu] b - bus fault, d - ділення на нуль, i - INVSTATE, u - невирівняний доступ\r\n"));
}

} // namespace

extern "C" void SysTick_Handler()
{
    ++g_uptime_ms;
}

int main()
{
    io::console::init(kPclk2Hz, 115'200);

    // Вмикаємо окремі вектори якнайраніше: аварія під час ініціалізації
    // периферії — найчастіший випадок, і зловити її найважче.
    crash::arm();

    // Знімок причини скидання робимо ДО RMVF: прапорці накопичуються, і без
    // очищення наступний старт покаже суміш із двох перезапусків.
    const std::uint32_t reset_flags = RCC->CSR;
    RCC->CSR |= RCC_CSR_RMVF;

    static_cast<void>(io::console::write("\r\n===== старт прошивки =====\r\n"));
    crash::print_reset_cause(reset_flags);

    if (const auto dump = crash::take()) {
        crash::print(*dump);
    } else if ((reset_flags & (kResetIwdg | kResetWwdg)) != 0) {
        // Сторожовий таймер зупинив зависання: HardFault не спрацьовував, дампу
        // немає. Але перезапуск усе одно аварійний, і не порахувати його — це
        // пропустити зависання повз захист від циклу.
        static_cast<void>(crash::bump_counter());
        static_cast<void>(
            io::console::write("[crash] скидання сторожовим таймером, дампу немає\r\n"));
    } else {
        static_cast<void>(
            io::console::write("[crash] дампу немає — минулий сеанс завершився штатно\r\n"));
    }

    if (crash::decide() == crash::BootDecision::SafeMode) {
        crash::safe_mode(); // не повертається
    }

    SysTick_Config(kSysclkHz / 1000);
    print_menu();

    while (true) {
        crash::note_uptime(std::chrono::milliseconds{g_uptime_ms});

        const auto cmd = io::console::read();
        if (!cmd) {
            continue;
        }
        switch (*cmd) {
        case 'b':
            provoke_bus_fault();
            break;
        case 'd':
            provoke_div_by_zero();
            break;
        case 'i':
            provoke_invalid_state();
            break;
        case 'u':
            provoke_unaligned();
            break;
        default:
            print_menu();
            break;
        }
    }
}
