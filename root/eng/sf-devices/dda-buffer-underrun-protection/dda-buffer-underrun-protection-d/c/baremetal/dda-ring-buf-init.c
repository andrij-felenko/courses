#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// -----------------------------------------------------------------------------
// 1. КОНСТАНТИ ТА СТРУКТУРИ ДАНИХ МОДУЛЯ DDA
// -----------------------------------------------------------------------------

#define DDA_RING_BUFFER_SIZE  128U  // Має бути ступенем двійки для маски (128 - 1)
#define DDA_BUFFER_MASK       (DDA_RING_BUFFER_SIZE - 1U)

// Стани автомата захисту від опустошення буфера DDA
typedef enum {
    DDA_BUF_STATE_NORMAL = 0,
    DDA_BUF_STATE_WARNING,
    DDA_BUF_STATE_DECELERATING,
    DDA_BUF_STATE_UNDERRUN_STOPPED,
    DDA_BUF_STATE_RECOVERY
} DdaProtectionState_t;

// Один квант руху (сегмент), що зберігається в буфері DDA
typedef struct {
    uint32_t step_ticks;     // Період таймера для даного кроку (в тиках апаратного таймера)
    uint8_t  dir_mask;       // Бітова маска напрямку осей (DIR)
    uint8_t  step_mask;      // Бітова маска активних осей (STEP)
    uint16_t duration_us;    // Тривалість кванта у мікросекундах для швидкого підрахунку T_avail
} DdaStepCommand_t;

// Структура безблокувального кільцевого буфера SPSC
typedef struct {
    DdaStepCommand_t buffer[DDA_RING_BUFFER_SIZE];
    volatile uint32_t head;  // Записується виключно задачею Планувальника (Producer)
    volatile uint32_t tail;  // Записується виключно в ISR таймера (Consumer)
    
    volatile uint32_t total_time_avail_us; // Загальний часовий запас руху в буфері (мкс)
    
    // Параметри конфігурації захисту
    uint32_t warning_threshold_us;   // Порог попередження (мкс)
    uint32_t decel_threshold_us;     // Критичний гальмівний порог (мкс)
    uint32_t max_decel_steps;        // Максимальна кількість кроків гальмування
    
    // Поточний стан автомата
    volatile DdaProtectionState_t state;
    
    // Змінні автономного гальмування в ISR
    uint32_t decel_step_count;
    uint32_t current_decel_ticks;
} DdaRingBuffer_t;

static DdaRingBuffer_t g_dda_ring_buf;

// -----------------------------------------------------------------------------
// 2. ІНІЦІАЛІЗАЦІЯ ТА БЕЗБЛОКУВАЛЬНІ ОПЕРАЦІЇ SPSC
// -----------------------------------------------------------------------------

void dda_ring_buf_init(DdaRingBuffer_t *rb, uint32_t warning_us, uint32_t decel_us) {
    rb->head = 0;
    rb->tail = 0;
    rb->total_time_avail_us = 0;
    rb->warning_threshold_us = warning_us;
    rb->decel_threshold_us = decel_us;
    rb->max_decel_steps = 100;
    rb->state = DDA_BUF_STATE_NORMAL;
    rb->decel_step_count = 0;
    rb->current_decel_ticks = 0;
}

// Перевірка кількості вільних елементів (докреслюється Планувальником)
static inline uint32_t dda_buf_capacity_available(const DdaRingBuffer_t *rb) {
    uint32_t h = rb->head;
    uint32_t t = rb->tail;
    return DDA_RING_BUFFER_SIZE - 1U - ((h - t) & DDA_BUFFER_MASK);
}

// Перевірка кількості доступних елементів для споживання в ISR
static inline uint32_t dda_buf_count(const DdaRingBuffer_t *rb) {
    uint32_t h = rb->head;
    uint32_t t = rb->tail;
    return (h - t) & DDA_BUFFER_MASK;
}

// Запис нової команди Планувальником (Producer)
bool dda_ring_buf_push(DdaRingBuffer_t *rb, const DdaStepCommand_t *cmd) {
    uint32_t h = rb->head;
    uint32_t t = rb->tail;

    if (((h + 1U) & DDA_BUFFER_MASK) == (t & DDA_BUFFER_MASK)) {
        return false; // Буфер повністю заповнений
    }

    rb->buffer[h & DDA_BUFFER_MASK] = *cmd;

    // Атомарна публікація покажчика head із бар'єром пам'яті
    __asm__ __volatile__("" ::: "memory"); // Бар'єр компілятора
    rb->head = (h + 1U) & DDA_BUFFER_MASK;

    // Оновлюємо доступний фізичний час руху
    rb->total_time_avail_us += cmd->duration_us;
    return true;
}

// -----------------------------------------------------------------------------
// 3. АППАРАТНИЙ ОБРОБНИК ПЕРЕРИВАННЯ ТАЙМЕРА (ISR)
// -----------------------------------------------------------------------------

void DDA_Timer_ISR_Handler(void) {
    DdaRingBuffer_t *rb = &g_dda_ring_buf;
    uint32_t t = rb->tail;
    uint32_t h = rb->head;

    // 1. Оцінка поточного стану та розрахунок часового запасу
    uint32_t available_count = (h - t) & DDA_BUFFER_MASK;

    if (rb->state != DDA_BUF_STATE_DECELERATING && rb->state != DDA_BUF_STATE_UNDERRUN_STOPPED) {
        if (rb->total_time_avail_us <= rb->decel_threshold_us || available_count <= 1U) {
            // Аварійний перехід у режим автономного гальмування безпосередньо в ISR!
            rb->state = DDA_BUF_STATE_DECELERATING;
            rb->decel_step_count = 1;
            // Початковий інтервал беруть з останньої виконаної команди або базисного значення
            if (rb->current_decel_ticks == 0) {
                rb->current_decel_ticks = 1000; // Базове значення у тиках
            }
        } else if (rb->total_time_avail_us <= rb->warning_threshold_us) {
            rb->state = DDA_BUF_STATE_WARNING;
            // Сигналізація задачі Планувальника про термінове поповнення
        } else {
            rb->state = DDA_BUF_STATE_NORMAL;
        }
    }

    // 2. Обробка виконання залежно від стану автомата
    if (rb->state == DDA_BUF_STATE_DECELERATING) {
        // АВТОНОМНЕ ГАЛЬМУВАННЯ В ISR ЗА ФОРМУЛОЮ ТЕЙЛОРА
        uint32_t n = rb->decel_step_count;
        uint32_t c_prev = rb->current_decel_ticks;

        // c_n = c_{n-1} + (2 * c_{n-1}) / (4 * n + 1)  (збільшуємо інтервал = зменшуємо швидкість)
        uint32_t c_next = c_prev + (2U * c_prev) / (4U * n + 1U);
        rb->current_decel_ticks = c_next;
        rb->decel_step_count++;

        // Подача імпульсу STEP на апаратні ніжки
        // TIM_SET_COMPARE(c_next);

        if (rb->decel_step_count >= rb->max_decel_steps || c_next > 50000U) {
            // Вісь повністю зупинена без втрати кроків
            rb->state = DDA_BUF_STATE_UNDERRUN_STOPPED;
        }
        return;
    }

    if (rb->state == DDA_BUF_STATE_UNDERRUN_STOPPED) {
        // Таймер переводиться у режим очікування, імпульси не генеруються
        return;
    }

    // 3. Звичайний режим виконання команди з буфера
    if (available_count > 0U) {
        DdaStepCommand_t *cmd = &rb->buffer[t & DDA_BUFFER_MASK];

        // Видача сигналів DIR та STEP на GPIO
        // GPIO_WRITE_DIR(cmd->dir_mask);
        // GPIO_PULSE_STEP(cmd->step_mask);

        rb->current_decel_ticks = cmd->step_ticks;

        if (rb->total_time_avail_us >= cmd->duration_us) {
            rb->total_time_avail_us -= cmd->duration_us;
        } else {
            rb->total_time_avail_us = 0;
        }

        // Просування покажчика зчитування tail
        __asm__ __volatile__("" ::: "memory");
        rb->tail = (t + 1U) & DDA_BUFFER_MASK;
    }
}
