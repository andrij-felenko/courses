// faults.cpp — обробник збою з витягуванням кадру стека.
//
// Обробник складається з двох половин, і це не примха стилю.
//
// Перша половина мусить бути асемблерною. Входячи у виняток, ядро вже уклало
// кадр R0–R3, R12, LR, PC, xPSR на той стек, який був активний, — і лише
// значення LR каже, на який саме: біт 2 коду EXC_RETURN розрізняє головний
// стек MSP і стек задачі PSP. Мовою C++ цього не написати: компілятор має
// право вставити власний пролог і зрушити SP раніше, ніж ми встигнемо його
// прочитати. Атрибут naked забороняє пролог, а обгортка лише кладе адресу
// кадру в R0, EXC_RETURN у R1 і стрибає далі — за AAPCS це вже два перші
// аргументи звичайної функції.
//
// Друга половина — звичайний код: збирає FaultReport і спиняє ядро.

#include <cstdint>

#include "mcu/fault.hpp"
#include "mcu/scb.hpp"

extern "C" void fault_entry(const std::uint32_t* stack_frame,
                            std::uint32_t exc_return);

// Один і той самий текст потрібен чотирьом векторам, тому він оформлений
// макросом: шаблон тут не допоміг би — тіло naked-функції не має права
// містити нічого, крім асемблерного блоку, а ім'я символу мусить точно
// збігатися з іменем у векторній таблиці.
#define FAULT_TRAMPOLINE(name)                                    \
    extern "C" __attribute__((naked, used)) void name()           \
    {                                                             \
        __asm volatile(                                           \
            ".syntax unified    \n"                               \
            "tst    lr, #4      \n" /* біт 2 EXC_RETURN */        \
            "ite    eq          \n"                               \
            "mrseq  r0, msp     \n" /* 0 → кадр на MSP */         \
            "mrsne  r0, psp     \n" /* 1 → кадр на PSP */         \
            "mov    r1, lr      \n" /* сам EXC_RETURN */          \
            "b      fault_entry \n"                               \
        );                                                        \
    }

// Сильні визначення перекривають слабкі псевдоніми зі стартового модуля.
FAULT_TRAMPOLINE(HardFault_Handler)
FAULT_TRAMPOLINE(MemManage_Handler)
FAULT_TRAMPOLINE(BusFault_Handler)
FAULT_TRAMPOLINE(UsageFault_Handler)

extern "C" __attribute__((used))
void fault_entry(const std::uint32_t* stack_frame, std::uint32_t exc_return)
{
    const std::uint32_t cfsr_value = mcu::cfsr::load();
    const std::uint32_t hfsr_value = mcu::hfsr::load();
    const std::uint32_t mmfar_value = mcu::mmfar::load();
    const std::uint32_t bfar_value = mcu::bfar::load();

    // Кадр лежить у пам'яті рівно так, як описує ExceptionFrame: порядок полів
    // заданий архітектурою, тож копіюємо структуру цілком.
    const auto* frame = reinterpret_cast<const mcu::ExceptionFrame*>(stack_frame);

    mcu::last_fault = mcu::FaultReport{
        .frame = *frame,
        .exception = mcu::active_exception(),
        .cfsr = cfsr_value,
        .hfsr = hfsr_value,
        .address = mcu::access_address(cfsr_value, mmfar_value, bfar_value),
        .cause = mcu::decode_cause(cfsr_value, hfsr_value),
        .used_psp = (exc_return & mcu::bits::exc_return_psp) != 0,
        .escalated = (hfsr_value & mcu::hfsr_bits::forced) != 0,
    };

    // Ознаки збою липкі: доки їх не скинути записом одиниць, наступний аналіз
    // побачить причину минулого разу. Скидаємо ПІСЛЯ того, як звіт зібрано.
    mcu::cfsr::clear_sticky(cfsr_value);
    mcu::hfsr::clear_sticky(hfsr_value);

    // Зупинка саме тут: увесь контекст іще на місці, а mcu::last_fault.frame.pc
    // віддається команді arm-none-eabi-addr2line -e firmware.elf <pc>.
    mcu::halt();
}
