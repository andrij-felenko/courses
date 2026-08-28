#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * Додає ключ до фільтра Блума.
 * 
 * Часова складність: O(k).
 * Потокобезпека: Потрібне зовнішнє блокування запису (Write Lock).
 * 
 * @param filter Вказівник на ініціалізований фільтр Блума.
 * @param data Вказівник на буфер ключа.
 * @param len Довжина буфера в байтах.
 */
void bloom_add(bloom_filter_t *filter, const void *data, size_t len);

/**
 * Перевіряє наявність ключа у фільтрі.
 * 
 * Часова складність: O(k) в найгіршому випадку, O(1) пересічно завдяки раній зупинці.
 * Потокобезпека: Дозволяється паралельне зчитання декількома потоками без блокувань.
 * 
 * @param filter Вказівник на фільтр Блума.
 * @param data Вказівник на буфер ключа.
 * @param len Довжина ключа у байтах.
 * @return false якщо ключ ГАРАНТОВАНО відсутній; true якщо ключ ІМОВІРНО є.
 */
bool bloom_contains(const bloom_filter_t *filter, const void *data, size_t len);
