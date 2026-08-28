#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "stm32f4xx.h"

// Структура збереженого апаратурою базового кадру стека ARM Cortex-M
typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
} __attribute__((packed)) FaultStackFrame;

// Повний діагностичний дамп аварії для збереження в .noinit RAM
typedef struct {
    uint32_t magic;          // Маркер валідності дампу (0xDEADBEEF)
    uint32_t crash_count;    // Лічильник послідовних падінь (Crash Loop Guard)
    uint32_t reset_reason;   // Прапорці скидання RCC->CSR
    uint32_t hfsr;           // SCB->HFSR
    uint32_t cfsr;           // SCB->CFSR (UFSR + BFSR + MMFSR)
    uint32_t mmfar;          // SCB->MMFAR
    uint32_t bfar;           // SCB->BFAR
    uint32_t shcsr;          // SCB->SHCSR
    uint32_t exc_return;     // Значення LR на вході в обробник
    FaultStackFrame frame;   // Регістри R0-R3, R12, LR, PC, PSR
    uint32_t crc;            // Контрольна сума
} CrashDump;

#define CRASH_MAGIC 0xDEADBEEF
#define MAX_CRASH_LOOP_THRESHOLD 3

// Розміщення в секції .noinit, яка не очищається під час Reset
__attribute__((section(".noinit")))
static volatile CrashDump g_crash_dump;

// Проста реалізація контрольної суми для перевірки цілісності дампу
static uint32_t CalcCRC32(const uint8_t *data, uint32_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (uint32_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint32_t j = 0; j < 8; ++j) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320;
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

// Прямий синхронний вивід символу через UART (без переривань і DMA!)
static void UART_SendCharBlocking(char c) {
    // Очікуємо готовності передавача (TXE прапорець)
    while (!(USART1->SR & USART_SR_TXE)) {}
    USART1->DR = (uint8_t)c;
}

static void UART_SendStringBlocking(const char *str) {
    while (*str) {
        UART_SendCharBlocking(*str++);
    }
}

// C-частина обробника, яка отримує точний покажчик на стек
void HardFault_Handler_C(const FaultStackFrame *frame, uint32_t exc_return) {
    // Збільшуємо лічильник падінь або скидаємо, якщо магічне число пошкоджене
    uint32_t current_count = (g_crash_dump.magic == CRASH_MAGIC) ? g_crash_dump.crash_count + 1 : 1;

    // Заповнюємо дамп
    g_crash_dump.magic = CRASH_MAGIC;
    g_crash_dump.crash_count = current_count;
    g_crash_dump.reset_reason = RCC->CSR;
    g_crash_dump.hfsr = SCB->HFSR;
    g_crash_dump.cfsr = SCB->CFSR;
    g_crash_dump.mmfar = SCB->MMFAR;
    g_crash_dump.bfar = SCB->BFAR;
    g_crash_dump.shcsr = SCB->SHCSR;
    g_crash_dump.exc_return = exc_return;

    if (frame != NULL) {
        g_crash_dump.frame = *frame;
    }

    g_crash_dump.crc = CalcCRC32((const uint8_t *)&g_crash_dump, 
                                 sizeof(CrashDump) - sizeof(uint32_t));

    // Негайний синхронний вивід повідомлення для розробника
    UART_SendStringBlocking("\r\n[CRASH] Hardware fault captured, rebooting...\r\n");
    
    // Перезавантажуємо мікроконтролер для безпечного виходу з аварії
    NVIC_SystemReset();
}

// Асемблерний трамплін: визначає активний стек (MSP чи PSP)
__attribute__((naked)) void HardFault_Handler(void) {
    __asm volatile(
        "tst lr, #4                \n" // Перевіряємо біт 2 регістра LR (EXC_RETURN)
        "ite eq                    \n" // Якщо 0 (Equal) -> використовувався MSP
        "mrseq r0, msp             \n" // R0 = покажчик на стек MSP
        "mrsne r0, psp             \n" // Якщо 1 (Not Equal) -> R0 = покажчик PSP
        "mov r1, lr                \n" // R1 = значення EXC_RETURN
        "b HardFault_Handler_C     \n" // Перехід у функцію розбору з аргументами (R0, R1)
    );
}

// Перевірка та друк збереженого дампу після перезапуску в main()
bool CrashDump_ProcessOnStartup(void) {
    if (g_crash_dump.magic != CRASH_MAGIC) {
        return false;
    }

    uint32_t calc_crc = CalcCRC32((const uint8_t *)&g_crash_dump, 
                                  sizeof(CrashDump) - sizeof(uint32_t));
    if (calc_crc != g_crash_dump.crc) {
        g_crash_dump.magic = 0; // Дамп пошкоджено
        return false;
    }

    // Якщо зафіксовано цикл падінь — перехід у безпечний режим
    if (g_crash_dump.crash_count >= MAX_CRASH_LOOP_THRESHOLD) {
        UART_SendStringBlocking("[CRASH-LOOP] Too many crashes! Entering recovery mode.\r\n");
    }

    // Дамп валідний: тут виконується логування на Flash або передача на сервер
    // Очищаємо маркер після успішного опрацювання
    g_crash_dump.magic = 0;
    return true;
}
