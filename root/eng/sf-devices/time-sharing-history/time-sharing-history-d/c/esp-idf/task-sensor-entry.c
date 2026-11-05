#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// Структура кадру збереження контексту процесора ARM Cortex-M
typedef struct {
    // Регістри, збережені програмно (Software-stacked frame)
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t r8;
    uint32_t r9;
    uint32_t r10;
    uint32_t r11;

    // Регістри, збережені апаратно при винятку (Hardware auto-stacked frame)
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t xpsr;
} context_frame_t;

// Блок управління задачею (Task Control Block, TCB)
typedef struct {
    uint32_t *top_of_stack;       // Покажчик на вершину стека (перше поле!)
    uint32_t stack_base[256];    // Виділений масив оперативної пам'яті під стек
    uint32_t task_id;            // Ідентифікатор задачі
} tcb_t;

static tcb_t g_tasks[2];
static tcb_t *g_current_tcb = NULL;

// Функції-задачі
void task_sensor_entry(void) {
    while (1) {
        // Логіка збору даних з датчиків
    }
}

void task_display_entry(void) {
    while (1) {
        // Логіка оновлення дисплея
    }
}

// Ініціалізація початкового стека задачі для перемикання контексту
void init_task_stack(tcb_t *tcb, void (*task_entry)(void), uint32_t id) {
    tcb->task_id = id;
    
    // Покажчик стека встановлюється на кінець масиву (стек росте донизу)
    uint32_t *sp = &tcb->stack_base[256];
    
    // Резервуємо місце під кадр контексту
    sp -= sizeof(context_frame_t) / sizeof(uint32_t);
    context_frame_t *frame = (context_frame_t *)sp;
    
    memset(frame, 0, sizeof(context_frame_t));
    frame->pc = (uint32_t)task_entry;        // Адреса входу в задачу
    frame->xpsr = 0x01000000;                // Стандартне значення прапорця Thumb-режиму
    frame->lr = 0xFFFFFFFD;                  // Спеціальний код повернення з винятку EXC_RETURN
    
    tcb->top_of_stack = sp;                  // Записуємо покажчик стека в TCB
}

// Модель атомарної зміни покажчика стека в планувальнику
void switch_context_tcb(tcb_t *next_tcb) {
    // Зміна активного TCB
    g_current_tcb = next_tcb;
}

void setup_scheduler(void) {
    init_task_stack(&g_tasks[0], task_sensor_entry, 1);
    init_task_stack(&g_tasks[1], task_display_entry, 2);
    g_current_tcb = &g_tasks[0];
}
