#ifndef LAMPORT_CLOCK_H
#define LAMPORT_CLOCK_H

#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Вирівнювання за розміром типової кеш-лінії L1/L2 (64 байти) для запобігання false sharing */
#define LAMPORT_CACHE_LINE_SIZE 64

/**
 * @brief Незмінний кортеж мітки часу Лампорта (значення лічильника + унікальний ID вузла).
 */
typedef struct {
    uint32_t node_id;
    uint64_t counter;
} lamport_timestamp_t;

/**
 * @brief Структура стану логічного годинника вузла.
 */
typedef struct {
    alignas(LAMPORT_CACHE_LINE_SIZE) _Atomic uint64_t counter;
    uint32_t node_id;
} lamport_clock_t;

/**
 * @brief Ініціалізує логічний годинник для конкретного вузла.
 * @param clock Вказівник на виділену пам'ять годинника.
 * @param node_id Унікальний числовий ідентифікатор вузла в кластері.
 * @param initial_counter Початкове значення лічильника (типово 0 або збережене значення після перезапуску).
 */
void lamport_clock_init(lamport_clock_t* clock, uint32_t node_id, uint64_t initial_counter);

/**
 * @brief Фіксує локальну подію: атомарно збільшує лічильник на 1 і повертає нову мітку.
 * @param clock Вказівник на годинник.
 * @return lamport_timestamp_t Присвоєна події мітка часу.
 */
lamport_timestamp_t lamport_clock_tick(lamport_clock_t* clock);

/**
 * @brief Формує мітку часу перед відправленням повідомлення в мережу.
 * @param clock Вказівник на годинник.
 * @return lamport_timestamp_t Мітка для розміщення в заголовку повідомлення.
 */
lamport_timestamp_t lamport_clock_send_event(lamport_clock_t* clock);

/**
 * @brief Оновлює стан годинника при отриманні вхідного мережевого повідомлення.
 *        Виконує lock-free цикл CAS (Compare-And-Swap): counter = max(current, incoming) + 1.
 * @param clock Вказівник на годинник.
 * @param incoming_counter Значення лічильника із заголовка отриманого повідомлення.
 * @return lamport_timestamp_t Мітка, присвоєна події отримання повідомлення.
 */
lamport_timestamp_t lamport_clock_recv_event(lamport_clock_t* clock, uint64_t incoming_counter);

/**
 * @brief Читає поточне значення годинника без його інкременту.
 * @param clock Вказівник на годинник.
 * @return uint64_t Поточний стан лічильника.
 */
uint64_t lamport_clock_read(const lamport_clock_t* clock);

/**
 * @brief Порівнює дві мітки у тотальному порядку за кортежем (counter, node_id).
 * @param a Перша мітка.
 * @param b Друга мітка.
 * @return int -1 якщо a < b; 0 якщо a == b; +1 якщо a > b.
 */
int lamport_timestamp_compare(lamport_timestamp_t a, lamport_timestamp_t b);

#ifdef __cplusplus
}
#endif

#endif /* LAMPORT_CLOCK_H */
