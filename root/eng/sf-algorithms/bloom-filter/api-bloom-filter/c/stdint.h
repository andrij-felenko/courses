#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/**
 * Автоматично обчислює m і k та ініціалізує фільтр Блума.
 * 
 * Контракт виконання:
 * - expected_elements мусить бути більшим за 0.
 * - fp_rate мусить перебувати у відкритому інтервалі (0.0, 1.0).
 * 
 * @param filter Вказівник на виділену користувачем структуру bloom_filter_t.
 * @param expected_elements Очікувана кількість ключів (n).
 * @param fp_rate Допустима ймовірність хибнопозитивного спрацьовування (p).
 * @return true при успішному виділенні пам'яті, false у разі помилки malloc/aligned_alloc.
 */
bool bloom_init(bloom_filter_t *filter, size_t expected_elements, double fp_rate);

/**
 * Створює фільтр Блума з ручним специфікуванням точних параметрів m та k.
 * 
 * @param filter Вказівник на структуру фільтра.
 * @param num_bits Загальний розмір масиву в бітах (m).
 * @param num_hashes Кількість хеш-функцій (k).
 * @return true у разі успішної виділеної пам'яті, false при помилці.
 */
bool bloom_init_explicit(bloom_filter_t *filter, size_t num_bits, size_t num_hashes);

/**
 * Звільняє динамічний бітовий масив та скидає лічильники.
 * 
 * @param filter Вказівник на структуру фільтра Блума.
 */
void bloom_free(bloom_filter_t *filter);
