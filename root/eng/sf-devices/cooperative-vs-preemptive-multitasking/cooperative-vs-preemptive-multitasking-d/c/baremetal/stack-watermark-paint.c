#include <stdint.h>
#include <stdbool.h>

#define STACK_WATERMARK_PATTERN 0xA5A5A5A5UL

// -----------------------------------------------------------------------------
// 1. ДІАГНОСТИКА ВОДЯНОГО ЗНАКА СТЕКА
// -----------------------------------------------------------------------------

// Заливка виділеного стека діагностичним візерунком
void stack_watermark_paint(uint32_t *stack_base, uint32_t size_words) {
    for (uint32_t i = 0; i < size_words; ++i) {
        stack_base[i] = STACK_WATERMARK_PATTERN;
    }
}

// Підрахунок невикористаних слів стека (водяного знака)
uint32_t stack_watermark_get_free_words(const uint32_t *stack_base, uint32_t size_words) {
    uint32_t free_words = 0;
    // Скануємо знизу вгору: від найменшої адреси
    while (free_words < size_words && stack_base[free_words] == STACK_WATERMARK_PATTERN) {
        free_words++;
    }
    return free_words;
}

// -----------------------------------------------------------------------------
// 2. АПАРАТНЕ ПРОФІЛЮВАННЯ ЗАТРИМОК ЧЕРЕЗ DWT CYCCNT
// -----------------------------------------------------------------------------

#define DWT_CTRL    (*(volatile uint32_t *)0xE0001000)
#define DWT_CYCCNT  (*(volatile uint32_t *)0xE0001004)
#define DEMCR       (*(volatile uint32_t *)0xE000EDFC)

// Ініціалізація апаратного лічильника циклів
void dwt_cycle_counter_init(void) {
    // Вмикаємо біт TRCENA (Global enable for all DWT and ITM features) у регістрі DEMCR
    DEMCR |= (1UL << 24);
    // Скидаємо лічильник тактових циклів
    DWT_CYCCNT = 0;
    // Вмикаємо лічильник тактів (CYCCNTENA) у контрольному регістрі DWT
    DWT_CTRL |= 1UL;
}

// Замір тривалості виконання у тактах процесора
uint32_t profile_context_switch_cycles(void (*switch_fn)(void)) {
    uint32_t start_cycles = DWT_CYCCNT;
    switch_fn();
    uint32_t end_cycles = DWT_CYCCNT;
    return end_cycles - start_cycles;
}

// -----------------------------------------------------------------------------
// 3. ГІБРИДНА ЧЕРГА ВІДКЛАДЕНИХ РОБІТ НА СПІЛЬНОМУ ПОТОЦІ
// -----------------------------------------------------------------------------

typedef void (*work_handler_t)(void *arg);

typedef struct {
    work_handler_t handler;
    void *argument;
} deferred_work_t;

#define WORK_QUEUE_CAPACITY 8
static deferred_work_t g_work_queue[WORK_QUEUE_CAPACITY];
static volatile uint8_t g_work_head = 0;
static volatile uint8_t g_work_tail = 0;

bool work_queue_post(work_handler_t handler, void *arg) {
    uint8_t next_head = (g_work_head + 1) % WORK_QUEUE_CAPACITY;
    if (next_head == g_work_tail) {
        return false; // Черга переповнена
    }
    g_work_queue[g_work_head].handler = handler;
    g_work_queue[g_work_head].argument = arg;
    g_work_head = next_head;
    return true;
}

// Фонова витісняльна задача, яка послідовно виконує кооперативні обробники
void cooperative_worker_task(void *pvParameters) {
    (void)pvParameters;
    while (1) {
        if (g_work_tail != g_work_head) {
            deferred_work_t work = g_work_queue[g_work_tail];
            g_work_tail = (g_work_tail + 1) % WORK_QUEUE_CAPACITY;
            if (work.handler != 0) {
                work.handler(work.argument);
            }
        } else {
            // Очікування нових подій або передача кванта часу іншим задачам
            __asm volatile ("wfi");
        }
    }
}
