// faults.cpp — вектори винятків ядра.
//
// У виробі не буває «невідомого» винятку, який просто зациклює процесор
// у стандартній заглушці зі startup-файла: кожен виняток веде в ту саму
// точку — знеструмити, записати, перезапустити.
#include "crash_report.hpp"
#include "platform.hpp"
#include "safety.hpp"

extern "C" {

// Викликається з асемблерних обгорток нижче. Кадр винятку, який ядро
// саме поклало на стек: R0 R1 R2 R3 R12 LR PC xPSR.
[[noreturn]] void fault_report(const std::uint32_t* frame, std::uint32_t exc_return) noexcept
{
    static_cast<void>(exc_return);

    const diag::FaultContext context{
        .pc = frame[6],
        .lr = frame[5],
        // Кадр — вісім слів; дев'яте могло піти на вирівнювання, але для
        // пошуку місця падіння важлива саме межа кадру.
        .sp = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(frame + 8)),
        .cfsr = stm32::scb::cfsr::read(),
    };

    safety::panic(diag::PanicReason::hard_fault, context);
}

// Обгортка мусить бути naked: звичайний пролог функції зіпсував би стек,
// з якого ми зараз дістаємо контекст падіння. Біт 2 у EXC_RETURN каже,
// з якого стека ядро складало кадр — головного чи процесного.
#define FAULT_TRAMPOLINE(name)                     \
    [[gnu::naked]] void name()                     \
    {                                              \
        __asm volatile("tst   lr, #4          \n"  \
                       "ite   eq              \n"  \
                       "mrseq r0, msp         \n"  \
                       "mrsne r0, psp         \n"  \
                       "mov   r1, lr          \n"  \
                       "b     fault_report    \n"); \
    }

FAULT_TRAMPOLINE(HardFault_Handler)
FAULT_TRAMPOLINE(MemManage_Handler)
FAULT_TRAMPOLINE(BusFault_Handler)
FAULT_TRAMPOLINE(UsageFault_Handler)

#undef FAULT_TRAMPOLINE

} // extern "C"
