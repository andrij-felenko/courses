#include <stdint.h>
#include <stdbool.h>

// -----------------------------------------------------------------------------
// 1. АПАРАТНИЙ ТА ПРОГРАМНИЙ КАДРИ СТЕКА ЯДРА CORTEX-M
// -----------------------------------------------------------------------------

// Повна структура стекового кадру збереженої задачі
typedef struct {
    // Програмний кадр (зберігається кодом PendSV_Handler)
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t r8;
    uint32_t r9;
    uint32_t r10;
    uint32_t r11;

    // Апаратний кадр (автоматично зберігається ядром при вході у виняток)
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t xpsr;
} stack_frame_t;

// Контрольний блок задачі
typedef struct {
    uint32_t *stack_pointer;    // Поточна вершина стека задачі
    uint32_t *stack_base;       // Нижня адреса виділеного буфера стека
    uint32_t stack_size_words;  // Розмір стека у 32-бітних словах
} task_tcb_t;

static task_tcb_t *g_current_tcb = 0;
static task_tcb_t *g_next_tcb = 0;

// Функція захисту від випадкового завершення задачі
static void task_exit_trap(void) {
    while (1) {
        // Задача завершила нескінченний цикл: блокуємо виконання
        __asm volatile ("wfi");
    }
}

// Ініціалізація початкового штучного кадру стека
uint32_t *task_stack_init(void (*entry)(void *), void *arg, uint32_t *stack_top) {
    // Вирівнювання адреси вершини стека по межі 8 байтів згідно з AAPCS
    stack_top = (uint32_t *)((uint32_t)stack_top & ~0x07UL);

    // Виділення місця під повний кадр
    stack_top -= sizeof(stack_frame_t) / sizeof(uint32_t);
    stack_frame_t *frame = (stack_frame_t *)stack_top;

    // Заповнення апаратного кадру
    frame->xpsr = 0x01000000UL;              // Біт 24 (Thumb) обов'язково встановлено в 1
    frame->pc   = (uint32_t)entry;           // Адреса точки входу функції задачі
    frame->lr   = (uint32_t)task_exit_trap;  // Адреса пастки при поверненні
    frame->r12  = 0x12121212UL;              // Тестова сигнатура регістра R12
    frame->r3   = 0x03030303UL;
    frame->r2   = 0x02020202UL;
    frame->r1   = 0x01010101UL;
    frame->r0   = (uint32_t)arg;             // Покажчик на аргумент задачі

    // Заповнення програмного кадру (сигнатури для діагностики)
    frame->r11  = 0x11111111UL;
    frame->r10  = 0x10101010UL;
    frame->r9   = 0x09090909UL;
    frame->r8   = 0x08080808UL;
    frame->r7   = 0x07070707UL;
    frame->r6   = 0x06060606UL;
    frame->r5   = 0x05050505UL;
    frame->r4   = 0x04040404UL;

    return stack_top;
}

// -----------------------------------------------------------------------------
// 2. АСЕМБЛЕРНИЙ ПЕРЕМИКАЧ КОНТЕКСТУ ВИТІСНЯЛЬНОГО ПЛАНУВАЛЬНИКА
// -----------------------------------------------------------------------------

__attribute__((naked)) void PendSV_Handler(void) {
    __asm volatile (
        "mrs     r0, psp                 \n" // Завантажуємо покажчик стека задачі PSP у R0
        "isb                             \n" // Бар'єр синхронізації інструкцій
        "stmdb   r0!, {r4-r11}           \n" // Зберігаємо програмний кадр R4-R11 у стек задачі
        "ldr     r1, =g_current_tcb      \n" // Завантажуємо адресу покажчика на поточний TCB
        "ldr     r2, [r1]                \n" // Завантажуємо адресу поточного TCB
        "str     r0, [r2]                \n" // Оновлюємо збережений stack_pointer у TCB

        "ldr     r3, =g_next_tcb         \n" // Завантажуємо адресу покажчика на наступний TCB
        "ldr     r4, [r3]                \n" // Завантажуємо адресу наступного TCB
        "str     r4, [r1]                \n" // g_current_tcb = g_next_tcb

        "ldr     r0, [r4]                \n" // Завантажуємо новий stack_pointer із нового TCB
        "ldmia   r0!, {r4-r11}           \n" // Відновлюємо програмний кадр R4-R11
        "msr     psp, r0                 \n" // Записуємо нову вершину стека у регістр PSP
        "isb                             \n" // Бар'єр синхронізації конвеєра
        "bx      lr                      \n" // Повернення з винятку: апаратура відновлює R0-R3, R12, LR, PC, xPSR
        ".align 4                        \n"
    );
}

// -----------------------------------------------------------------------------
// 3. КРИТИЧНІ СЕКЦІЇ НА БАЗІ РЕГІСТРУ BASEPRI
// -----------------------------------------------------------------------------

#define RTOS_MAX_SYSCALL_PRIORITY 0x50 // Поріг маскування переривань (пріоритет 5)

static inline uint32_t enter_critical_section(void) {
    uint32_t prev_basepri;
    __asm volatile (
        "mrs     %0, basepri             \n" // Читаємо поточне значення BASEPRI
        "msr     basepri, %1             \n" // Встановлюємо маскування переривань планувальника
        "isb                             \n"
        : "=r" (prev_basepri)
        : "r" (RTOS_MAX_SYSCALL_PRIORITY)
        : "memory"
    );
    return prev_basepri;
}

static inline void exit_critical_section(uint32_t prev_basepri) {
    __asm volatile (
        "msr     basepri, %0             \n" // Відновлюємо попередній стан маскування
        "isb                             \n"
        :
        : "r" (prev_basepri)
        : "memory"
    );
}

// Кооперативна добровільна передача управління процесором
void task_yield(void) {
    // Встановлюємо біт PENDSVSET у регістрі керування винятками ICSR
    *(volatile uint32_t *)0xE000ED04 = (1UL << 28);
    __asm volatile ("dsb \n isb");
}
