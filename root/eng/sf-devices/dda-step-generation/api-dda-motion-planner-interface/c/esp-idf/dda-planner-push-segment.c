#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>

#define DDA_RING_BUFFER_SIZE 16
#define DDA_AXES_COUNT 3

typedef struct {
    uint32_t steps_major;
    uint32_t steps_minor[DDA_AXES_COUNT - 1];
    uint8_t dominant_axis_idx;
    uint8_t dir_mask;
    uint32_t initial_period_ticks;
    int32_t period_change_fp16; // Фіксована крапка 16.16
} dda_segment_t;

typedef struct {
    dda_segment_t buffer[DDA_RING_BUFFER_SIZE];
    atomic_size_t head;
    atomic_size_t tail;
} dda_ring_buffer_t;

typedef struct {
    dda_segment_t current_seg;
    uint32_t current_step;
    uint32_t dda_acc[DDA_AXES_COUNT - 1];
    uint32_t period_accumulator_fp16;
    bool is_busy;
} dda_isr_state_t;

static dda_ring_buffer_t g_dda_buffer = { .head = 0, .tail = 0 };
static dda_isr_state_t g_isr_state = { .is_busy = false };

// API для фонового планувальника (Producer)
bool dda_planner_push_segment(const dda_segment_t *segment) {
    size_t head = atomic_load_explicit(&g_dda_buffer.head, memory_order_relaxed);
    size_t next_head = (head + 1) % DDA_RING_BUFFER_SIZE;
    size_t tail = atomic_load_explicit(&g_dda_buffer.tail, memory_order_acquire);

    if (next_head == tail) {
        return false; // Буфер переповнений
    }

    g_dda_buffer.buffer[head] = *segment;
    atomic_store_explicit(&g_dda_buffer.head, next_head, memory_order_release);
    return true;
}

// Таймерний обробник переривань (Consumer)
void IRAM_ATTR dda_timer_isr_handler(void) {
    if (!g_isr_state.is_busy) {
        size_t head = atomic_load_explicit(&g_dda_buffer.head, memory_order_acquire);
        size_t tail = atomic_load_explicit(&g_dda_buffer.tail, memory_order_relaxed);

        if (head == tail) {
            // Буфер порожній - зупинка руху
            return;
        }

        // Завантаження нового сегмента
        g_isr_state.current_seg = g_dda_buffer.buffer[tail];
        g_isr_state.current_step = 0;
        g_isr_state.period_accumulator_fp16 = g_isr_state.current_seg.initial_period_ticks << 16;
        
        for (int i = 0; i < DDA_AXES_COUNT - 1; i++) {
            g_isr_state.dda_acc[i] = g_isr_state.current_seg.steps_major / 2;
        }

        atomic_store_explicit(&g_dda_buffer.tail, (tail + 1) % DDA_RING_BUFFER_SIZE, memory_order_release);
        g_isr_state.is_busy = true;

        // Встановлення напрямку DIR GPIO
        // gpio_set_level_mask(g_isr_state.current_seg.dir_mask);
    }

    // Генерація кроку провідної осі
    uint8_t step_mask = (1 << g_isr_state.current_seg.dominant_axis_idx);

    // Алгоритм DDA для ведених осей
    for (int i = 0; i < DDA_AXES_COUNT - 1; i++) {
        g_isr_state.dda_acc[i] += g_isr_state.current_seg.steps_minor[i];
        if (g_isr_state.dda_acc[i] >= g_isr_state.current_seg.steps_major) {
            g_isr_state.dda_acc[i] -= g_isr_state.current_seg.steps_major;
            step_mask |= (1 << ((g_isr_state.current_seg.dominant_axis_idx + 1 + i) % DDA_AXES_COUNT));
        }
    }

    // Подача імпульсу на GPIO (STEP High)
    // gpio_set_step_pins(step_mask);

    // Інкремент кінематики періоду
    g_isr_state.period_accumulator_fp16 += g_isr_state.current_seg.period_change_fp16;
    uint32_t next_period_ticks = g_isr_state.period_accumulator_fp16 >> 16;
    
    // Переналаштування апаратного таймера
    // timer_set_alarm_value(next_period_ticks);

    g_isr_state.current_step++;
    if (g_isr_state.current_step >= g_isr_state.current_seg.steps_major) {
        g_isr_state.is_busy = false; // Сегмент завершено
    }
}
