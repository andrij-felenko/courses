#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>

#define RING_BUFFER_SIZE 16

typedef struct {
    uint32_t step_count;       // Загальна кількість кроків ведучої осі
    uint32_t phase_inc_start;  // Початковий приріст фази DDA
    int32_t  phase_accel;      // Приріст фази на один такт ISR (прискорення)
    uint32_t dir_mask;         // Маска напрямку руху для GPIO
    uint32_t follower_ratio;   // Коефіцієнт веденої осі з фіксованою комою
} MotionBlock;

typedef struct {
    MotionBlock buffer[RING_BUFFER_SIZE];
    atomic_size_t head;        // Індекс зчитування (використовується ISR)
    atomic_size_t tail;        // Індекс запису (використовується планувальником)
} MotionQueue;

static MotionQueue motion_queue;
static uint32_t dda_accumulator_lead = 0;
static uint32_t dda_accumulator_follow = 0;
static uint32_t current_step = 0;
static uint32_t current_phase_inc = 0;

bool planner_push_block(const MotionBlock *block) {
    size_t current_tail = atomic_load_explicit(&motion_queue.tail, memory_order_relaxed);
    size_t next_tail = (current_tail + 1) % RING_BUFFER_SIZE;
    size_t current_head = atomic_load_explicit(&motion_queue.head, memory_order_acquire);

    if (next_tail == current_head) {
        return false; // Кільцевий буфер переповнений
    }

    motion_queue.buffer[current_tail] = *block;
    atomic_store_explicit(&motion_queue.tail, next_tail, memory_order_release);
    return true;
}

void timer_isr_handler(void) {
    size_t current_head = atomic_load_explicit(&motion_queue.head, memory_order_relaxed);
    size_t current_tail = atomic_load_explicit(&motion_queue.tail, memory_order_acquire);

    if (current_head == current_tail && current_step == 0) {
        return; // Черга порожня, рух відсутній
    }

    MotionBlock *active_block = &motion_queue.buffer[current_head];

    if (current_step == 0 && current_phase_inc == 0) {
        current_phase_inc = active_block->phase_inc_start;
    }

    uint32_t prev_accum = dda_accumulator_lead;
    dda_accumulator_lead += current_phase_inc;
    current_phase_inc += active_block->phase_accel;

    if (dda_accumulator_lead < prev_accum) { // Переповнення 32-бітного акумулятора
        current_step++;
        dda_accumulator_follow += active_block->follower_ratio;

        if (current_step >= active_block->step_count) {
            current_step = 0;
            current_phase_inc = 0;
            dda_accumulator_lead = 0;
            dda_accumulator_follow = 0;
            size_t next_head = (current_head + 1) % RING_BUFFER_SIZE;
            atomic_store_explicit(&motion_queue.head, next_head, memory_order_release);
        }
    }
}
