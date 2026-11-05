#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include "stm32f4xx.h"

#define MAX_ALARMS 32U
#define RING_BUFFER_SIZE 64U

typedef uint32_t bitmask32_t;

// Структура події для передачі з ISR у фонову задачу RTOS
typedef struct {
    uint16_t alarm_id;
    uint8_t  state;        // 1 - активна, 0 - неактивна
    uint32_t timestamp_us;
} AlarmEvent_t;

// Безблокувальний кільцевий буфер подій
typedef struct {
    AlarmEvent_t buffer[RING_BUFFER_SIZE];
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
    bitmask32_t active_in_queue; // Маска для дедуплікації в ISR
} LockFreeEventQueue_t;

// Конфігурація системи придушення у статичній пам'яті
typedef struct {
    bitmask32_t adj_matrix[MAX_ALARMS]; // Матриця суміжності графу причинності
    bitmask32_t mode_masks[4];          // Бітові маски режимів FSM
    bitmask32_t raw_vector;             // Вектор сирих тривог
    bitmask32_t shelved_vector;         // Вектор відкладених тривог
    bitmask32_t final_vector;           // Вектор підсумкових першопричин
    uint8_t     current_fsm_mode;       // Поточний режим FSM
} AlarmEngine_t;

static AlarmEngine_t g_alarm_engine;
static LockFreeEventQueue_t g_event_queue;

// Атомарне додавання події з контексту переривання ISR із дедуплікацією
bool Alarm_ISR_PushEvent(uint16_t alarm_id, uint8_t state) {
    if (alarm_id >= MAX_ALARMS) {
        return false;
    }
    
    // Дедуплікація: якщо подія для цієї тривоги вже є в черзі, ігноруємо
    bitmask32_t mask = (1U << alarm_id);
    if ((atomic_load(&g_event_queue.active_in_queue) & mask) != 0U) {
        return false; // Подія дедуплікована
    }

    uint32_t current_head = atomic_load_explicit(&g_event_queue.head, memory_order_relaxed);
    uint32_t next_head = (current_head + 1U) % RING_BUFFER_SIZE;
    uint32_t current_tail = atomic_load_explicit(&g_event_queue.tail, memory_order_acquire);

    if (next_head == current_tail) {
        return false; // Кільцевий буфер переповнений
    }

    // Запис події та часової мітки з апаратного лічильника DWT
    g_event_queue.buffer[current_head].alarm_id = alarm_id;
    g_event_queue.buffer[current_head].state = state;
    g_event_queue.buffer[current_head].timestamp_us = DWT->CYCCNT / (SystemCoreClock / 1000000U);

    atomic_fetch_or(&g_event_queue.active_in_queue, mask);
    atomic_store_explicit(&g_event_queue.head, next_head, memory_order_release);
    return true;
}

// Покроковий розрахунок вектора першопричин у фоновому такті RTOS
void Alarm_Process_Cycle(void) {
    // 1. Вичитання подій із кільцевого буфера
    uint32_t current_tail = atomic_load_explicit(&g_event_queue.tail, memory_order_relaxed);
    uint32_t current_head = atomic_load_explicit(&g_event_queue.head, memory_order_acquire);

    while (current_tail != current_head) {
        AlarmEvent_t evt = g_event_queue.buffer[current_tail];
        bitmask32_t mask = (1U << evt.alarm_id);

        if (evt.state != 0U) {
            g_alarm_engine.raw_vector |= mask;
        } else {
            g_alarm_engine.raw_vector &= ~mask;
        }

        atomic_fetch_and(&g_event_queue.active_in_queue, ~mask);
        current_tail = (current_tail + 1U) % RING_BUFFER_SIZE;
    }
    atomic_store_explicit(&g_event_queue.tail, current_tail, memory_order_release);

    // 2. Крок 1: Первинна фільтрація за режимом FSM та шелвінгом
    bitmask32_t mode_mask = g_alarm_engine.mode_masks[g_alarm_engine.current_fsm_mode];
    bitmask32_t candidates = g_alarm_engine.raw_vector & mode_mask & ~g_alarm_engine.shelved_vector;

    // 3. Крок 2: Накопичення маски придушення через інструкції ARM Cortex-M CLZ
    bitmask32_t suppress_mask = 0U;
    bitmask32_t temp_cand = candidates;

    while (temp_cand != 0U) {
        // __builtin_clz повертає кількість провідних нулів
        uint32_t leading_zeros = (uint32_t)__builtin_clz(temp_cand);
        uint32_t bit_index = 31U - leading_zeros;

        // Додаємо рядки причинності для кожного активного кандидата
        suppress_mask |= g_alarm_engine.adj_matrix[bit_index];

        // Скидаємо оброблений біт
        temp_cand &= ~(1U << bit_index);
    }

    // 4. Крок 3: Обчислення підсумкових першопричин
    g_alarm_engine.final_vector = candidates & ~suppress_mask;
}
