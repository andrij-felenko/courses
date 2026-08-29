// HardFaultTrap.cpp — перехоплювач фатальних винятків ARM Cortex-M.
// Ланцюжок один: витягти стековий кадр -> записати кадри аварії ->
// вивантажити том у FRAM -> скинути ядро.
#include "FlightRecorderCore.hpp"
#include "McuPort.hpp"
#include "SpiEmergencyDump.hpp"

namespace {

// Адреса слота дампа в енергонезалежному носії.
constexpr std::uint32_t kNvSlotAddr = 0x000000U;

} // namespace

// Обробник передає сюди два аргументи: r0 — покажчик на апаратний стековий
// кадр, r1 — EXC_RETURN, за яким видно, чий це був стек.
extern "C" void blackbox_fault_entry(const std::uint32_t* stack_frame,
                                     std::uint32_t exc_return) noexcept {
    using namespace embedded;

    diagnostics::FaultInfo fault{};
    // Апаратний кадр: R0, R1, R2, R3, R12, LR, PC, xPSR
    fault.lr         = stack_frame[5];
    fault.pc         = stack_frame[6];
    fault.psr        = stack_frame[7];
    fault.exc_return = exc_return;
    fault.cfsr       = mcu::reg(mcu::kScbCfsr);
    fault.hfsr       = mcu::reg(mcu::kScbHfsr);

    // MMFAR і BFAR тримають сміття, доки не стоїть їхній біт дійсності:
    // записати їх наосліп означає надіслати слідчого хибним слідом.
    if ((fault.cfsr & mcu::kCfsrMmarValid) != 0U) {
        fault.fault_addr = mcu::reg(mcu::kScbMmfar);
        fault.addr_valid = 0x01U;
    } else if ((fault.cfsr & mcu::kCfsrBfarValid) != 0U) {
        fault.fault_addr = mcu::reg(mcu::kScbBfar);
        fault.addr_valid = 0x02U;
    }

    diagnostics::recorder().panic(fault);

    // Знімок у .noinit переживе скидання, але не переживе знеструмлення, тому
    // той самий том одразу лягає в носій. Помилку тут нікому доповідати —
    // копія в SRAM лишилась, і скидання відкладати не можна.
    (void)drivers::dump_recorder_to_fram(kNvSlotAddr);

    mcu::system_reset();
}

// Голий (naked) перехідник: компілятор не має права поставити пролог, який
// зачепить зіпсований стек. Другий біт EXC_RETURN каже, куди ядро склало
// кадр — у MSP чи в PSP потоку, і саме тут пролягає межа між живим дампом
// і вторинним збоєм стекування.
#if defined(__ARM_ARCH_6M__)
// Cortex-M0/M0+: без IT-блоків і без умовних mrs — розгалуження явне.
extern "C" [[gnu::naked]] void HardFault_Handler() {
    asm volatile("movs r0, #4       \n"
                 "mov  r1, lr       \n"
                 "tst  r0, r1       \n"
                 "beq  1f           \n"
                 "mrs  r0, psp      \n"
                 "b    2f           \n"
                 "1:                \n"
                 "mrs  r0, msp      \n"
                 "2:                \n"
                 "b    blackbox_fault_entry \n");
}
#else
extern "C" [[gnu::naked]] void HardFault_Handler() {
    asm volatile("tst   lr, #4      \n"
                 "ite   eq          \n"
                 "mrseq r0, msp     \n"
                 "mrsne r0, psp     \n"
                 "mov   r1, lr      \n"
                 "b     blackbox_fault_entry \n");
}

// Налаштовані винятки, доки їх не ескалювали в HardFault, приходять своїми
// векторами — і мають лягти в чорну скриньку так само.
extern "C" [[gnu::alias("HardFault_Handler")]] void MemManage_Handler();
extern "C" [[gnu::alias("HardFault_Handler")]] void BusFault_Handler();
extern "C" [[gnu::alias("HardFault_Handler")]] void UsageFault_Handler();
#endif
