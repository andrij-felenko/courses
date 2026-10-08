#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file ring_buffer.h
 * @brief Оголошення потокобезпечного кільцевого буфера для збереження подій імпульсів Холла.
 * 
 * Буфер призначений для швидкої неблокуючої реєстрації часових міток і лічильників імпульсів
 * у контексті переривань (ISR) з подальшою обробкою в основному фоновому потоці або за таймером.
 */

/** @brief Розмір кільцевого буфера (мусить бути ступенем двійки для оптимізації маскування) */
#define RING_BUFFER_CAPACITY 64U

/**
 * @brief Елемент кільцевого буфера, що описує одну подію імпульсу.
 */
typedef struct {
    uint32_t timestamp_us;  /**< Часова мітка виникнення імпульсу в мікросекундах */
    uint16_t pulse_increment; /**< Кількість зафіксованих імпульсів у пачці (зазвичай 1) */
} ring_buffer_element_t;

/**
 * @brief Структура кільцевого буфера з атомарними вказівниками.
 */
typedef struct {
    ring_buffer_element_t data[RING_BUFFER_CAPACITY]; /**< Масив даних буфера */
    volatile uint16_t head;  /**< Вказівник на позицію запису (модифікується в ISR) */
    volatile uint16_t tail;  /**< Вказівник на позицію зчитування (модифікується у фоні) */
    volatile uint32_t overflow_count; /**< Лічильник втрачених імпульсів при переповненні */
} ring_buffer_t;

/**
 * @brief Ініціалізація кільцевого буфера.
 * @param rb Вказівник на екземпляр кільцевого буфера.
 */
void ring_buffer_init(ring_buffer_t *rb);

/**
 * @brief Неблокуюче додавання елемента до буфера з контексту переривання (ISR).
 * @param rb Вказівник на кільцевий буфер.
 * @param element Елемент даних для запису.
 * @return true, якщо елемент успішно додано, false при переповненні.
 */
bool ring_buffer_push(ring_buffer_t *rb, ring_buffer_element_t element);

/**
 * @brief Зчитування та вилучення найстарішого елемента з буфера.
 * @param rb Вказівник на кільцевий буфер.
 * @param element Вказівник для збереження прочитаного елемента.
 * @return true, якщо елемент успішно вилучено, false якщо буфер порожній.
 */
bool ring_buffer_pop(ring_buffer_t *rb, ring_buffer_element_t *element);

/**
 * @brief Перевірка, чи порожній кільцевий буфер.
 * @param rb Вказівник на кільцевий буфер.
 * @return true, якщо порожній.
 */
bool ring_buffer_is_empty(const ring_buffer_t *rb);

/**
 * @brief Перевірка, чи повний кільцевий буфер.
 * @param rb Вказівник на кільцевий буфер.
 * @return true, якщо повний.
 */
bool ring_buffer_is_full(const ring_buffer_t *rb);

/**
 * @brief Отримання поточної кількості елементів у буфері.
 * @param rb Вказівник на кільцевий буфер.
 * @return Кількість елементів.
 */
uint16_t ring_buffer_count(const ring_buffer_t *rb);

/**
 * @brief Обчислення згладженої середньої частоти імпульсів за доступними елементами буфера.
 * @param rb Вказівник на кільцевий буфер.
 * @param window_us Вікно усереднення у мікросекундах.
 * @return Розрахована частота імпульсів у Гц.
 */
float ring_buffer_calculate_average_frequency(ring_buffer_t *rb, uint32_t window_us);

#endif /* RING_BUFFER_H */
