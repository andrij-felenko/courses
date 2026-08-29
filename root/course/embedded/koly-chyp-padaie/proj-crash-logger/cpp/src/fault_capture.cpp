#include "fault_capture.hpp"

#include <cstdint>
#include <span>

#include "crash_record.hpp"
#include "stm32f4xx.h"
#include "sync_uart.hpp"

namespace {

// Межі RAM STM32F407: основна SRAM і щільно зв'язана CCM. Покажчик стека в
// аварії буває будь-яким сміттям, і читання за ним наосліп дає другий виняток
// поспіль, тобто Lockup замість звіту.
constexpr std::uintptr_t kSramBegin = 0x2000'0000;
constexpr std::uintptr_t kSramEnd = 0x2002'0000;
constexpr std::uintptr_t kCcmBegin = 0x1000'0000;
constexpr std::uintptr_t kCcmEnd = 0x1001'0000;

[[nodiscard]] bool is_ram(std::uintptr_t addr, std::size_t size) noexcept
{
    if ((addr & 3u) != 0) {
        return false; // кадр завжди вирівняний по слову
    }
    if (addr >= kSramBegin && addr + size <= kSramEnd) {
        return true;
    }
    return addr >= kCcmBegin && addr + size <= kCcmEnd;
}

// Розширена частина кадру: S0-S15, FPSCR і резервне слово вирівнювання.
constexpr std::size_t kFpuBlockWords = 18;

} // namespace

// Аналітична частина. Місток передає сюди адресу кадру й EXC_RETURN.
extern "C" void crash_capture(const crash::CortexFrame* frame,
                              std::uint32_t exc_return) noexcept
{
    const crash::CortexFrame* safe_frame = nullptr;
    if (is_ram(reinterpret_cast<std::uintptr_t>(frame), sizeof(crash::CortexFrame))) {
        safe_frame = frame;
    }

    auto fpu_state = crash::FpuFrame::None;
    std::span<const std::uint32_t> fpu_block{};

    // Біт 4 EXC_RETURN дорівнює нулю — апаратура виділила розширений кадр
    // одразу за базовими вісьмома словами.
    if ((exc_return & (1u << 4)) == 0) {
        fpu_state = crash::FpuFrame::Saved;

#if defined(__FPU_PRESENT) && (__FPU_PRESENT == 1U)
        // Ліниве збереження: місце під S0-S15 є, а самі регістри ядро ще не
        // виштовхнуло. Прочитати їх звідти можна, тільки це не стан аварії.
        if ((FPU->FPCCR & FPU_FPCCR_LSPACT_Msk) != 0) {
            fpu_state = crash::FpuFrame::LazyPending;
        }
#endif

        const auto block_addr =
            reinterpret_cast<std::uintptr_t>(frame) + sizeof(crash::CortexFrame);
        if (safe_frame != nullptr && is_ram(block_addr, kFpuBlockWords * sizeof(std::uint32_t))) {
            fpu_block = std::span<const std::uint32_t>{
                reinterpret_cast<const std::uint32_t*>(block_addr), kFpuBlockWords};
        } else {
            fpu_state = crash::FpuFrame::LazyPending;
        }
    }

    crash::store(safe_frame, exc_return, fpu_state, fpu_block);

    // Один рядок у порт негайно: якщо плата на столі, розробник бачить падіння
    // тієї ж миті, не чекаючи перезапуску. Помилку передавача ігноруємо
    // свідомо — рятувати тут уже нічого.
    static_cast<void>(io::console::write("\r\n[FAULT] dump stored, resetting\r\n"));

    // Відладчик підключений — зупиняємося на місці аварії: жива зупинка коштує
    // дорожче за будь-який дамп.
    if ((CoreDebug->DHCSR & CoreDebug_DHCSR_C_DEBUGEN_Msk) != 0) {
        __BKPT(0);
    }

    NVIC_SystemReset();
    while (true) {
    } // NVIC_SystemReset не повертається, але компілятор про це не знає
}

// Місток. Чотири інструкції: визначити активний стек, віддати його адресу
// першим аргументом і піти в C++. naked гарантує, що компілятор не вставить
// сюди пролог і не зрушить SP до того, як ми прочитаємо покажчик.
extern "C" [[gnu::naked]] void HardFault_Handler()
{
    __asm volatile(
        "tst   lr, #4          \n" // біт 2 EXC_RETURN: який стек був активний
        "ite   eq              \n"
        "mrseq r0, msp         \n" // 0 — виняток стався на MSP
        "mrsne r0, psp         \n" // 1 — код задачі працював на PSP
        "mov   r1, lr          \n" // другий аргумент — саме EXC_RETURN
        "b     crash_capture   \n" // хвостовий перехід: LR лишається цілим
    );
}

// Ті самі чотири інструкції потрібні всім фатальним векторам — заводимо
// псевдоніми, а не чотири копії коду.
extern "C" [[gnu::alias("HardFault_Handler")]] void MemManage_Handler();
extern "C" [[gnu::alias("HardFault_Handler")]] void BusFault_Handler();
extern "C" [[gnu::alias("HardFault_Handler")]] void UsageFault_Handler();

namespace crash {

void arm() noexcept
{
    SCB->SHCSR |= SCB_SHCSR_USGFAULTENA_Msk | SCB_SHCSR_BUSFAULTENA_Msk |
                  SCB_SHCSR_MEMFAULTENA_Msk;
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk | SCB_CCR_UNALIGN_TRP_Msk;
    __DSB();
    __ISB();
}

} // namespace crash
