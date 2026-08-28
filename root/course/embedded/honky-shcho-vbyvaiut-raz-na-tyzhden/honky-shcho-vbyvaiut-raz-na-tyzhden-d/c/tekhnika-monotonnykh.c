#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define SPSC_FIFO_SIZE 64U /* Обов'язково ступінь двійки (2^6) */
#define SPSC_FIFO_MASK (SPSC_FIFO_SIZE - 1U)

typedef struct {
    uint8_t buffer[SPSC_FIFO_SIZE];
    /* Розділені індекси з вирівнюванням */
    volatile uint32_t head; /* Модифікується ТІЛЬКИ виробником */
    volatile uint32_t tail; /* Модифікується ТІЛЬКИ споживачем */
} spsc_fifo_t;

static inline void spsc_fifo_init(spsc_fifo_t *fifo) {
    fifo->head = 0;
    fifo->tail = 0;
}

/* Запис у буфер: викликається ТІЛЬКИ Виробником (наприклад, ISR) */
static inline bool spsc_fifo_push(spsc_fifo_t *fifo, uint8_t byte) {
    uint32_t current_head = fifo->head;
    uint32_t current_tail = fifo->tail;

    /* Перевірка на заповнення буфера */
    if ((current_head - current_tail) >= SPSC_FIFO_SIZE) {
        return false; /* Буфер переповнений */
    }

    /* 1. Записуємо дані у виділений слот */
    fifo->buffer[current_head & SPSC_FIFO_MASK] = byte;

    /* 2. Бар'єр пам'яті: дані гарантовано мають потрапити в ОЗП 
     * ДО того, як буде оновлено покажчик head */
    #if defined(__ARM_ARCH)
    __asm volatile ("DMB" ::: "memory");
    #endif

    /* 3. Оновлюємо покажчик head (атомарний 32-бітний запис) */
    fifo->head = current_head + 1U;
    return true;
}

/* Зчитування з буфера: викликається ТІЛЬКИ Споживачем (Головний цикл) */
static inline bool spsc_fifo_pop(spsc_fifo_t *fifo, uint8_t *byte) {
    uint32_t current_tail = fifo->tail;
    uint32_t current_head = fifo->head;

    /* Перевірка на порожнечу буфера */
    if (current_head == current_tail) {
        return false; /* Даних немає */
    }

    /* 1. Бар'єр пам'яті перед читанням даних */
    #if defined(__ARM_ARCH)
    __asm volatile ("DMB" ::: "memory");
    #endif

    /* 2. Зчитуємо дані зі слота */
    *byte = fifo->buffer[current_tail & SPSC_FIFO_MASK];

    /* 3. Бар'єр пам'яті перед оновленням tail */
    #if defined(__ARM_ARCH)
    __asm volatile ("DMB" ::: "memory");
    #endif

    /* 4. Оновлюємо покажчик tail */
    fifo->tail = current_tail + 1U;
    return true;
}
