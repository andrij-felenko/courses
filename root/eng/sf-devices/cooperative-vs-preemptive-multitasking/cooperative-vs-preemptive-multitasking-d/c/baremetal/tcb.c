#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// -----------------------------------------------------------------------------
// 1. КООПЕРАТИВНИЙ ПЛАНУВАЛЬНИК НА ОСНОВІ АВТОМАТА СТАНІВ
// -----------------------------------------------------------------------------

typedef enum {
    COOP_TASK_STATE_IDLE = 0,
    COOP_TASK_STATE_READY,
    COOP_TASK_STATE_SLEEPING
} coop_state_t;

typedef struct {
    void (*task_func)(void);  // Покажчик на функцію задачі
    coop_state_t state;       // Поточний стан задачі
    uint32_t delay_ticks;     // Кількість тиків очікування
} coop_task_t;

#define MAX_COOP_TASKS 4
static coop_task_t g_coop_tasks[MAX_COOP_TASKS];
static uint8_t g_coop_task_count = 0;

// Реєстрація кооперативної задачі
bool coop_task_create(void (*func)(void)) {
    if (g_coop_task_count >= MAX_COOP_TASKS) {
        return false;
    }
    g_coop_tasks[g_coop_task_count].task_func = func;
    g_coop_tasks[g_coop_task_count].state = COOP_TASK_STATE_READY;
    g_coop_tasks[g_coop_task_count].delay_ticks = 0;
    g_coop_task_count++;
    return true;
}

// Запуск кооперативного циклу планувальника
void coop_scheduler_start(void) {
    while (1) {
        for (uint8_t i = 0; i < g_coop_task_count; i++) {
            if (g_coop_tasks[i].state == COOP_TASK_STATE_READY) {
                // Виклик задачі (задача виконує один крок і сама повертає контроль)
                g_coop_tasks[i].task_func();
            }
        }
    }
}

// -----------------------------------------------------------------------------
// 2. ВИТІСНЯЛЬНЕ ЯДРО: СТРУКТУРА TCB ТА АЛГОРИТМ ПЕРЕМЕКАЛЬНИКА
// -----------------------------------------------------------------------------

typedef enum {
    TASK_STATE_READY = 0,
    TASK_STATE_RUNNING,
    TASK_STATE_BLOCKED,
    TASK_STATE_SUSPENDED
} task_state_t;

typedef struct tcb {
    uint32_t *sp;             // Покажчик на вершину стека (повинен бути першим полем!)
    uint8_t priority;         // Пріоритет задачі (0 - найнижчий)
    task_state_t state;       // Стан задачі з автомата станів
    uint32_t delay_ticks;     // Залишок часу блокування
    uint32_t *stack_base;     // Базова адреса виділеного стека
    uint32_t stack_size;      // Розмір стека в 32-бітних словах
} tcb_t;

#define MAX_PREEMPT_TASKS 4
#define STACK_SIZE_WORDS  256

static tcb_t g_tcbs[MAX_PREEMPT_TASKS];
static uint32_t g_stacks[MAX_PREEMPT_TASKS][STACK_SIZE_WORDS];
static uint8_t g_preempt_task_count = 0;

static tcb_t *g_current_tcb = NULL;
static tcb_t *g_next_tcb = NULL;
static uint32_t g_ready_bitmap = 0;

// Ініціалізація фейкового кадру стека для нової задачі (ARM Cortex-M)
void preempt_task_create(uint8_t id, void (*task_entry)(void), uint8_t priority) {
    tcb_t *tcb = &g_tcbs[id];
    uint32_t *sp = &g_stacks[id][STACK_SIZE_WORDS];

    // Апаратний кадр авто-збереження (xPSR, PC, LR, R12, R3-R0)
    *(--sp) = 0x01000000; // xPSR (Thumb mode bit = 1)
    *(--sp) = (uint32_t)task_entry; // PC (адреса входу в задачу)
    *(--sp) = 0xFFFFFFFD; // LR (EXC_RETURN: повернення в Thread mode з PSP)
    *(--sp) = 0x12121212; // R12
    *(--sp) = 0x03030303; // R3
    *(--sp) = 0x02020202; // R2
    *(--sp) = 0x01010101; // R1
    *(--sp) = 0x00000000; // R0

    // Програмний кадр збереження регістрів R4-R11
    for (int i = 0; i < 8; i++) {
        *(--sp) = 0x00000000;
    }

    tcb->sp = sp;
    tcb->priority = priority;
    tcb->state = TASK_STATE_READY;
    tcb->delay_ticks = 0;
    tcb->stack_base = g_stacks[id];
    tcb->stack_size = STACK_SIZE_WORDS;

    g_ready_bitmap |= (1U << priority);
    g_preempt_task_count++;
}

// Арбітраж вибору наступної задачі за O(1)
void schedule_select_next(void) {
    if (g_ready_bitmap == 0) return;
    
    // Знаходження найвищого встановленого біта пріоритету
    uint8_t top_priority = 31 - __builtin_clz(g_ready_bitmap);
    
    for (uint8_t i = 0; i < g_preempt_task_count; i++) {
        if (g_tcbs[i].priority == top_priority && g_tcbs[i].state == TASK_STATE_READY) {
            g_next_tcb = &g_tcbs[i];
            break;
        }
    }
}

// Обробник системного таймера SysTick
void SysTick_Handler_C(void) {
    // Оновлення таймерів блокування задач
    for (uint8_t i = 0; i < g_preempt_task_count; i++) {
        if (g_tcbs[i].state == TASK_STATE_BLOCKED) {
            if (--g_tcbs[i].delay_ticks == 0) {
                g_tcbs[i].state = TASK_STATE_READY;
                g_ready_bitmap |= (1U << g_tcbs[i].priority);
            }
        }
    }

    schedule_select_next();

    if (g_next_tcb != g_current_tcb) {
        // Установка прапорця відкладеного переривання PendSV
        *(volatile uint32_t *)0xE000ED04 = (1U << 28);
    }
}
