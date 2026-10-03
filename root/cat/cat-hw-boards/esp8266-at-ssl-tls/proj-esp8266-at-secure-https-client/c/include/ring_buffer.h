#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Структура кільцевого буфера для асинхронного накопичення вхідних даних UART.
 * 
 * Реалізує lock-free обмін даними між перериванням UART (постачальник/ISR)
 * та неблокуючим автоматом FSM (споживач/головний цикл).
 */
typedef struct {
    uint8_t *buffer;          /**< Вказівник на виділений масив пам'яті */
    size_t capacity;          /**< Загальний розмір буфера в байтах (рекомендовано ступінь двійки) */
    size_t mask;              /**< Маска індексування (capacity - 1 для ступенів двійки, інакше 0) */
    volatile size_t head;     /**< Індекс запису (модифікується в ISR UART) */
    volatile size_t tail;     /**< Індекс зчитання (модифікується FSM-автоматом) */
} ring_buffer_t;

/**
 * @brief Ініціалізація структури кільцевого буфера.
 * @param rb Вказівник на екземпляр RingBuffer.
 * @param storage Вказівник на заздалегідь виділений масив байтів.
 * @param capacity Розмір масиву (в байтах).
 * @return true при успішній ініціалізації, false у разі некоректних параметрів.
 */
bool ring_buffer_init(ring_buffer_t *rb, uint8_t *storage, size_t capacity);

/**
 * @brief Запис одного байта в буфер (безпечно для виклику з ISR переривання UART).
 * @param rb Вказівник на буфер.
 * @param byte Байт даних з регістру UART RX.
 * @return true якщо байт успішно збережено, false якщо буфер переповнено.
 */
bool ring_buffer_push(ring_buffer_t *rb, uint8_t byte);

/**
 * @brief Пакетний запис масиву байтів у буфер.
 * @param rb Вказівник на буфер.
 * @param data Масив даних.
 * @param len Кількість байтів для запису.
 * @return Фактична кількість записаних байтів.
 */
size_t ring_buffer_push_bytes(ring_buffer_t *rb, const uint8_t *data, size_t len);

/**
 * @brief Вилучення одного байта з буфера.
 * @param rb Вказівник на буфер.
 * @param byte Посилання для вивантаження прочитаного значення.
 * @return true якщо байт прочитано, false якщо буфер порожній.
 */
bool ring_buffer_pop(ring_buffer_t *rb, uint8_t *byte);

/**
 * @brief Пакетне вилучення накопичених байтів з буфера.
 * @param rb Вказівник на буфер.
 * @param dest Запитуваний масив для збереження даних.
 * @param max_len Максимальна кількість байтів для читання.
 * @return Кількість прочитаних байтів.
 */
size_t ring_buffer_pop_bytes(ring_buffer_t *rb, uint8_t *dest, size_t max_len);

/**
 * @brief Перегляд байта за зміщенням від хвоста tail без його видалення з буфера.
 * @param rb Вказівник на буфер.
 * @param offset Зміщення відносно tail.
 * @param byte Посилання для збереження результату.
 * @return true якщо за вказаним зміщенням присутні дані.
 */
bool ring_buffer_peek(const ring_buffer_t *rb, size_t offset, uint8_t *byte);

/**
 * @brief Отримання кількості доступних для зчитання байтів у буфері.
 * @param rb Вказівник на буфер.
 * @return Кількість байтів, готових до зчитання.
 */
size_t ring_buffer_available(const ring_buffer_t *rb);

/**
 * @brief Отримання кількості вільного місця у буфері.
 * @param rb Вказівник на буфер.
 * @return Кількість байтів, яку можна додатково записати.
 */
size_t ring_buffer_free_space(const ring_buffer_t *rb);

/**
 * @brief Пропуск вказаної кількості байтів у буфері.
 * @param rb Вказівник на буфер.
 * @param len Кількість байтів для пропуску.
 * @return Фактична кількість пропущених байтів.
 */
size_t ring_buffer_skip(ring_buffer_t *rb, size_t len);

/**
 * @brief Повне очищення буфера (скидання індексів head та tail).
 * @param rb Вказівник на буфер.
 */
void ring_buffer_clear(ring_buffer_t *rb);

/**
 * @brief Неблокуючий пошук текстового шаблону або підрядка у буфері.
 * @param rb Вказівник на буфер.
 * @param pattern Нуль-термінована послідовність символів (наприклад "OK\r\n", "> ", "+IPD,").
 * @return Зміщення від tail до початку знайденого шаблону або -1, якщо шаблон не знайдено.
 */
int ring_buffer_find_pattern(const ring_buffer_t *rb, const char *pattern);

#ifdef __cplusplus
}
#endif

#endif /* RING_BUFFER_H */
