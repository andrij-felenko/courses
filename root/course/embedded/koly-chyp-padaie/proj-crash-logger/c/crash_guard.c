#include "crash_guard.h"

#include "crash_dump.h"
#include "stm32f4xx.h"
#include "uart_sync.h"

#define CRASH_LOOP_THRESHOLD 3u
#define HEALTHY_UPTIME_MS 60000u

// Плата курсу: дозвіл силових ключів — PB0, живлення радіомодуля — PB1.
#define ACTUATOR_EN_PIN 0u
#define RADIO_EN_PIN 1u

// Системний завантажувач STM32F4 (AN2606). В інших родин адреса своя.
#define SYSTEM_BOOTLOADER_ADDR 0x1FFF0000u

static int g_counter_cleared;

boot_mode_t crash_guard_decide(void)
{
    const uint32_t crashes = crash_dump_consecutive();

    if (crashes == 0u) {
        return BOOT_NORMAL;
    }

    (void)uart_sync_write("[guard] падінь поспіль: ");
    (void)uart_sync_dec(crashes);
    (void)uart_sync_write(" з ");
    (void)uart_sync_dec(CRASH_LOOP_THRESHOLD);
    (void)uart_sync_newline();

    return (crashes >= CRASH_LOOP_THRESHOLD) ? BOOT_SAFE : BOOT_NORMAL;
}

void crash_guard_mark_healthy(uint32_t uptime_ms)
{
    if (g_counter_cleared || uptime_ms < HEALTHY_UPTIME_MS) {
        return;
    }
    g_counter_cleared = 1;
    if (crash_dump_consecutive() > 0u) {
        crash_dump_clear_counter();
        (void)uart_sync_write("[guard] хвилина без падінь — лічильник скинуто\r\n");
    }
}

// Приводи й радіо гасимо ПЕРШИМИ: у безпечний режим ми потрапили, бо прошивка
// падає, і мотор, який лишився під живленням, встигне наробити біди.
static void shutdown_outputs(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;

    GPIOB->MODER &= ~((3u << (ACTUATOR_EN_PIN * 2)) | (3u << (RADIO_EN_PIN * 2)));
    GPIOB->MODER |= (1u << (ACTUATOR_EN_PIN * 2)) | (1u << (RADIO_EN_PIN * 2));
    GPIOB->BSRR = (1u << (ACTUATOR_EN_PIN + 16)) | (1u << (RADIO_EN_PIN + 16));
}

__attribute__((noreturn)) static void jump_to_system_bootloader(void)
{
    typedef void (*entry_fn_t)(void);

    __disable_irq();

    // Гасимо все, що може вистрілити перериванням уже всередині завантажувача.
    SysTick->CTRL = 0u;
    SysTick->LOAD = 0u;
    SysTick->VAL = 0u;
    for (int i = 0; i < 8; ++i) {
        NVIC->ICER[i] = 0xFFFFFFFFu;
        NVIC->ICPR[i] = 0xFFFFFFFFu;
    }

    const uint32_t stack_top = *(volatile uint32_t *)SYSTEM_BOOTLOADER_ADDR;
    const entry_fn_t entry = (entry_fn_t) * (volatile uint32_t *)(SYSTEM_BOOTLOADER_ADDR + 4u);

    SCB->VTOR = SYSTEM_BOOTLOADER_ADDR;
    __DSB();
    __ISB();
    __set_MSP(stack_top);
    __enable_irq();
    entry();

    for (;;) {
    } // сюди не повертаються
}

__attribute__((noreturn)) void crash_guard_safe_mode(void)
{
    shutdown_outputs();

    (void)uart_sync_write("\r\n[safe] аварійний режим: приводи знеструмлено, задачі не стартують\r\n");
    (void)uart_sync_write("[safe] r - перезапуск, c - скинути лічильник і перезапустити, b - завантажувач\r\n");

    for (;;) {
        char cmd = 0;
        if (!uart_sync_read(&cmd)) {
            continue;
        }
        switch (cmd) {
        case 'r':
            NVIC_SystemReset();
            break;
        case 'c':
            crash_dump_clear_counter();
            (void)uart_sync_write("[safe] лічильник скинуто\r\n");
            NVIC_SystemReset();
            break;
        case 'b':
            (void)uart_sync_write("[safe] стрибок у системний завантажувач\r\n");
            jump_to_system_bootloader();
            break;
        default:
            (void)uart_sync_write("[safe] невідома команда\r\n");
            break;
        }
    }
}
