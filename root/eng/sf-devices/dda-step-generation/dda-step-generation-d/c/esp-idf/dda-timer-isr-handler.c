#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include "driver/gpio.h"
#include "esp_attr.h"

#define AXIS_COUNT 3
#define RING_BUFFER_SIZE 16

// Структура блоку руху від планувальника траєкторії
typedef struct {
    uint32_t step_count_leading;              // Кількість кроків провідної осі
    uint32_t step_increment[AXIS_COUNT];      // Прирости DDA-акумуляторів для кожної осі
    uint8_t dir_mask;                         // Маска напрямку руху (GPIO DIR)
    uint32_t timer_ticks_per_step;            // Інтервал тактування (кінематика швидкості)
} dda_motion_block_t;

// Потокобезпечний кільцевий буфер
typedef struct {
    dda_motion_block_t blocks[RING_BUFFER_SIZE];
    atomic_size_t head;
    atomic_size_t tail;
} dda_ring_buffer_t;

static dda_ring_buffer_t g_planner_queue;
static uint32_t g_accumulators[AXIS_COUNT];
static uint32_t g_current_step_count = 0;
static dda_motion_block_t g_active_block;
static bool g_has_active_block = false;

// GPIO піни кроків та напрямку (X, Y, Z)
static const gpio_num_t STEP_PINS[AXIS_COUNT] = {GPIO_NUM_18, GPIO_NUM_19, GPIO_NUM_21};
static const gpio_num_t DIR_PINS[AXIS_COUNT]  = {GPIO_NUM_22, GPIO_NUM_23, GPIO_NUM_25};

// Високоефективний обробник переривань таймера (ISR)
void IRAM_ATTR dda_timer_isr_handler(void* arg) {
    // Скидаємо імпульси STEP з попереднього такту для формування чіткого фронту
    for (int i = 0; i < AXIS_COUNT; i++) {
        gpio_set_level(STEP_PINS[i], 0);
    }

    // Якщо немає активного блоку, намагаємося завантажити з буфера
    if (!g_has_active_block) {
        size_t current_tail = atomic_load_explicit(&g_planner_queue.tail, memory_order_relaxed);
        size_t current_head = atomic_load_explicit(&g_planner_queue.head, memory_order_acquire);

        if (current_tail != current_head) {
            g_active_block = g_planner_queue.blocks[current_tail];
            atomic_store_explicit(&g_planner_queue.tail, (current_tail + 1) % RING_BUFFER_SIZE, memory_order_release);
            
            // Встановлюємо напрямок DIR для всіх осей
            for (int i = 0; i < AXIS_COUNT; i++) {
                bool dir_val = (g_active_block.dir_mask >> i) & 0x01;
                gpio_set_level(DIR_PINS[i], dir_val);
                g_accumulators[i] = 0; // Скидаємо акумулятори
            }
            g_current_step_count = 0;
            g_has_active_block = true;
        } else {
            return; // Буфер порожній, привід зупинено
        }
    }

    // Обробка поточного такту DDA
    for (int i = 0; i < AXIS_COUNT; i++) {
        uint32_t prev_acc = g_accumulators[i];
        g_accumulators[i] += g_active_block.step_increment[i];

        // Переповнення акумулятора -> генеруємо крок
        if (g_accumulators[i] < prev_acc || g_accumulators[i] >= 0x80000000U) {
            gpio_set_level(STEP_PINS[i], 1);
        }
    }

    g_current_step_count++;
    if (g_current_step_count >= g_active_block.step_count_leading) {
        g_has_active_block = false; // Блок завершено
    }
}
