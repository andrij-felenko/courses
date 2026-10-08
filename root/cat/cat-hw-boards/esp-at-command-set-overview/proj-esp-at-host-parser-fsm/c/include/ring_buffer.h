#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * @file ring_buffer.h
 * @brief Оголошення асинхронного потокобезпечного кільцевого буфера для збереження байтів UART.
 *
 * Кільцевий буфер призначений для накопичення даних у перериваннях UART ISR
 * та їх подальшого неблокуючого читання в основному циклі FSM-парсера.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Структура кільцевого буфера для вибірки байтів з UART ISR.
 */
typedef struct {
    uint8_t *buffer;           /**< Вказівник на зовнішній масив пам'яті */
    uint16_t capacity;         /**< Максимальний розмір буфера в байтах */
    volatile uint16_t head;    /**< Індекс запису (збільшується у перериванні ISR) */
    volatile uint16_t tail;    /**< Індекс зчитування (збільшується в основному циклі) */
    volatile uint16_t count;   /**< Поточна кількість збережених байтів */
} ring_buffer_t;

/**
 * @brief Ініціалізація кільцевого буфера на базі зовнішньо виділеного масиву.
 *
 * @param rb Вказівник на екземпляр кільцевого буфера.
 * @param storage Вказівник на буфер пам'яті (масив uint8_t).
 * @param capacity Розмір масиву пам'яті в байтах.
 */
void ring_buffer_init(ring_buffer_t *rb, uint8_t *storage, uint16_t capacity);

/**
 * @brief Перевірка, чи порожній кільцевий буфер.
 *
 * @param rb Вказівник на буфер.
 * @return true Якщо буфер не містить даних, false в іншому випадку.
 */
bool ring_buffer_is_empty(const ring_buffer_t *rb);

/**
 * @brief Перевірка, чи заповнений кільцевий буфер.
 *
 * @param rb Вказівник на буфер.
 * @return true Якщо досягнуто максимальну ємність, false в іншому випадку.
 */
bool ring_buffer_is_full(const ring_buffer_t *rb);

/**
 * @brief Отримання кількості доступних для зчитування байтів.
 *
 * @param rb Вказівник на буфер.
 * @return Поточна кількість байтів у буфері.
 */
uint16_t ring_buffer_available(const ring_buffer_t *rb);

/**
 * @brief Неблокуючий запис одного байта у буфер (безпечно для виклику з UART ISR).
 *
 * @param rb Вказівник на буфер.
 * @param byte Записуваний бати.
 * @return true Якщо байт успішно додано, false у разі переповнення.
 */
bool ring_buffer_push(ring_buffer_t *rb, uint8_t byte);

/**
 * @brief Послідовне зчитування одного байта з буфера (для використання у FSM-парсері).
 *
 * @param rb Вказівник на буфер.
 * @param byte Вказівник на змінну для збереження зчитаного значення.
 * @return true Якщо байт прочитано успішно, false якщо буфер порожній.
 */
bool ring_buffer_pop(ring_buffer_t *rb, uint8_t *byte);

/**
 * @brief Перегляд наступного байта у буфері без його вилучення.
 *
 * @param rb Вказівник на буфер.
 * @param byte Вказівник на змінну для збереження зчитаного значення.
 * @return true Якщо байт є у буфері, false якщо буфер порожній.
 */
bool ring_buffer_peek(const ring_buffer_t *rb, uint8_t *byte);

/**
 * @brief Очищення змісту кільцевого буфера та скидання індексів.
 *
 * @param rb Вказівник на буфер.
 */
void ring_buffer_clear(ring_buffer_t *rb);

#ifdef __cplusplus
}
#endif

#endif /* RING_BUFFER_H */
