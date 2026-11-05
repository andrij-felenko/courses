#include <stdint.h>
#include <stdbool.h>

// Структура збереження апаратного стану маски переривань
typedef struct {
    uint32_t saved_mask;
} critical_section_state_t;

// Вхід у критичну секцію із збереженням регістра BASEPRI
static inline critical_section_state_t hardware_critical_enter(void) {
    critical_section_state_t state;
    // Зчитуємо BASEPRI, встановлюємо нову маску та виконуємо бар'єр ISB
    __asm__ __volatile__(
        "mrs %0, basepri \n\t"
        "msr basepri, %1 \n\t"
        "isb             \n\t"
        : "=r" (state.saved_mask)
        : "r" (0x20) // Маскуємо переривання з пріоритетом 0x20 і нижче
        : "memory"
    );
    return state;
}

// Вихід із критичної секції з відновленням попереднього стану
static inline void hardware_critical_exit(const critical_section_state_t *state) {
    __asm__ __volatile__(
        "msr basepri, %0 \n\t"
        "isb             \n\t"
        :
        : "r" (state->saved_mask)
        : "memory"
    );
}

// Автоматичне викликанная очищення при виході з області видимості
static inline void auto_critical_exit(critical_section_state_t *state) {
    hardware_critical_exit(state);
}

// Макрос для створення автоматичної критичної секції C
#define CRITICAL_SECTION_C() \
    critical_section_state_t __cs_state __attribute__((cleanup(auto_critical_exit))) = hardware_critical_enter()

// Структура кільцевого буфера
typedef struct {
    uint8_t buffer[64];
    volatile uint32_t head;
    volatile uint32_t tail;
} ring_buffer_t;

// Потокобезпечна вставка даних у буфер
bool ring_buffer_push(ring_buffer_t *ring, uint8_t byte) {
    CRITICAL_SECTION_C(); // Апаратний захист секції
    
    uint32_t next_head = (ring->head + 1) % 64;
    if (next_head == ring->tail) {
        return false; // Буфер переповнено
    }
    
    ring->buffer[ring->head] = byte;
    ring->head = next_head;
    return true;
}
