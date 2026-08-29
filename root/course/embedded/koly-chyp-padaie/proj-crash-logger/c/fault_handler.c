#include "fault_handler.h"

#include <stddef.h>
#include <stdint.h>

#include "crash_dump.h"
#include "stm32f4xx.h"
#include "uart_sync.h"

// Межі RAM STM32F407: основна SRAM плюс щільно зв'язана CCM. Покажчик стека в
// аварії може бути будь-яким сміттям, і читати за ним наосліп — це другий
// виняток поспіль і Lockup замість звіту.
#define SRAM_BEGIN 0x20000000u
#define SRAM_END 0x20020000u
#define CCM_BEGIN 0x10000000u
#define CCM_END 0x10010000u

static int addr_is_ram(uint32_t addr, uint32_t size)
{
    if ((addr & 3u) != 0u) {
        return 0; // кадр завжди вирівняний по слову
    }
    if (addr >= SRAM_BEGIN && (addr + size) <= SRAM_END) {
        return 1;
    }
    return (addr >= CCM_BEGIN && (addr + size) <= CCM_END) ? 1 : 0;
}

// Аналітична частина. Викликається містком; frame вказує на кадр, збережений
// апаратурою, exc_return — значення LR на вході в обробник.
void fault_handler_capture(const cortex_frame_t *frame, uint32_t exc_return)
{
    const cortex_frame_t *safe_frame = NULL;
    const uint32_t *fpu_block = NULL;
    fpu_frame_state_t fpu_state = FPU_FRAME_NONE;

    if (addr_is_ram((uint32_t)frame, sizeof(cortex_frame_t))) {
        safe_frame = frame;
    }

    // Біт 4 EXC_RETURN: нуль — апаратура виділила розширений кадр із місцем під
    // S0-S15 і FPSCR одразу за базовими вісьмома словами.
    if ((exc_return & (1u << 4)) == 0u) {
        fpu_state = FPU_FRAME_SAVED;
#if defined(__FPU_PRESENT) && (__FPU_PRESENT == 1U)
        // Лінивe збереження: місце виділено, а самі регістри ядро ще не
        // виштовхнуло. Читати їх звідти можна, але це не стан аварії.
        if ((FPU->FPCCR & FPU_FPCCR_LSPACT_Msk) != 0u) {
            fpu_state = FPU_FRAME_LAZY;
        }
#endif
        if (safe_frame != NULL &&
            addr_is_ram((uint32_t)frame + sizeof(cortex_frame_t), 18u * 4u)) {
            fpu_block = (const uint32_t *)((const uint8_t *)frame + sizeof(cortex_frame_t));
        } else {
            fpu_state = FPU_FRAME_LAZY;
        }
    }

    crash_dump_store(safe_frame, exc_return, fpu_state, fpu_block);

    // Один рядок у порт негайно: якщо плата на столі й термінал відкритий,
    // розробник бачить падіння тієї ж миті, не чекаючи перезапуску.
    (void)uart_sync_write("\r\n[FAULT] dump stored, resetting\r\n");

    // Відладчик підключений — зупиняємося тут, а не тікаємо в перезапуск:
    // жива зупинка на місці аварії коштує дорожче за будь-який дамп.
    if ((CoreDebug->DHCSR & CoreDebug_DHCSR_C_DEBUGEN_Msk) != 0u) {
        __BKPT(0);
    }

    NVIC_SystemReset();

    for (;;) {
    } // NVIC_SystemReset не повертається, але компілятор про це не знає
}

// Місток. Тіло — чотири інструкції: визначити активний стек, віддати його
// адресу першим аргументом і передати керування в C. __attribute__((naked))
// гарантує, що компілятор не вставить сюди пролог і не зрушить SP.
__attribute__((naked)) void HardFault_Handler(void)
{
    __asm volatile(
        "tst   lr, #4                  \n" // біт 2 EXC_RETURN: який стек був активний
        "ite   eq                      \n"
        "mrseq r0, msp                 \n" // 0 — переривання прийшло з MSP
        "mrsne r0, psp                 \n" // 1 — код задачі працював на PSP
        "mov   r1, lr                  \n" // другий аргумент — саме EXC_RETURN
        "b     fault_handler_capture   \n" // хвостовий перехід: LR лишається цілим
    );
}

// Ті самі чотири інструкції потрібні всім фатальним винятковим векторам —
// заводимо на них псевдоніми, а не чотири копії коду.
void MemManage_Handler(void) __attribute__((alias("HardFault_Handler")));
void BusFault_Handler(void) __attribute__((alias("HardFault_Handler")));
void UsageFault_Handler(void) __attribute__((alias("HardFault_Handler")));

void fault_handler_init(void)
{
    SCB->SHCSR |= SCB_SHCSR_USGFAULTENA_Msk | SCB_SHCSR_BUSFAULTENA_Msk |
                  SCB_SHCSR_MEMFAULTENA_Msk;
    SCB->CCR |= SCB_CCR_DIV_0_TRP_Msk | SCB_CCR_UNALIGN_TRP_Msk;
    __DSB();
    __ISB();
}
