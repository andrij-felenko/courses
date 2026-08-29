#include <cstdint>

#include "fault_status.hpp"
#include "trace.hpp"
#include "stm32f4xx.h"

// Спільний вхід усіх чотирьох обробників. Трамплін уже поклав у R0 покажчик
// стека з кадром аварії, у R1 — EXC_RETURN, у R2 — номер вектора.
extern "C" void fault_entry_cpp(std::uint32_t stack_pointer,
                                std::uint32_t exc_return,
                                std::uint32_t vector) noexcept
{
    fault::report(stack_pointer,
                  fault::ExcReturn{exc_return},
                  static_cast<fault::Vector>(vector));

    trace::out.flush(); // дати останнім байтам вийти з UART до скидання

    // Не зависаємо у while(1): пристрій у полі має піднятися й працювати далі.
    // Наступний старт побачить у RCC->CSR прапорець SFTRSTF і знатиме, що це
    // був крах, а не подача живлення.
    NVIC_SystemReset();
}

// Трамплін мусить бути naked: будь-який пролог, згенерований компілятором,
// зсунув би покажчик стека, і R0 указував би вже не на кадр аварії.
// Біт 2 регістра LR (EXC_RETURN) каже, на якому стеку лежить кадр:
// 0 — MSP (bare-metal код або інше переривання), 1 — PSP (задача RTOS).
#define FAULT_TRAMPOLINE(handler, vector_id)                     \
    extern "C" [[gnu::naked]] void handler()                     \
    {                                                            \
        __asm volatile("tst   lr, #4              \n"             \
                       "ite   eq                  \n"             \
                       "mrseq r0, msp             \n"             \
                       "mrsne r0, psp             \n"             \
                       "mov   r1, lr              \n"             \
                       "mov   r2, %[id]           \n"             \
                       "b     fault_entry_cpp     \n"             \
                       :                                          \
                       : [id] "i"(static_cast<std::uint32_t>(vector_id)) \
                       : "r0", "r1", "r2", "memory");             \
    }

FAULT_TRAMPOLINE(HardFault_Handler, fault::Vector::Hard)
FAULT_TRAMPOLINE(MemManage_Handler, fault::Vector::MemManage)
FAULT_TRAMPOLINE(BusFault_Handler, fault::Vector::Bus)
FAULT_TRAMPOLINE(UsageFault_Handler, fault::Vector::Usage)
