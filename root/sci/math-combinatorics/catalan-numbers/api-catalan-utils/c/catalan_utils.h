// catalan_utils.h — C89/C99 сумісний заголовок процедурного C API
#ifndef CATALAN_UTILS_H
#define CATALAN_UTILS_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    CATALAN_SUCCESS          =  0,
    CATALAN_ERR_OVERFLOW     = -1,
    CATALAN_ERR_INVALID_PARAM= -2,
    CATALAN_ERR_NO_MEMORY    = -3,
    CATALAN_ERR_INVALID_DYCK = -4
} catalan_status_t;

/**
 * Обчислює точне значення C_n за лінійний час O(n).
 * @param n Індекс числа Каталана (0 <= n <= 35).
 * @param out_val Вказівник на змінну для запису результату.
 * @return CATALAN_SUCCESS або код помилки.
 */
catalan_status_t catalan_compute(uint32_t n, uint64_t* out_val);

/**
 * Генерує масив усіх чисел Каталана від C_0 до C_n включно.
 * @param n Максимальний індекс (0 <= n <= 35).
 * @param out_array Вказівник на виділений масив (потрібно викликати free()).
 * @return CATALAN_SUCCESS або CATALAN_ERR_NO_MEMORY.
 */
catalan_status_t catalan_sequence_dp(uint32_t n, uint64_t** out_array);

/**
 * Перевіряє, чи є рядок дужок правильною послідовністю (Dyck path).
 * @param str Рядок з символів '(' та ')'.
 * @param len Довжина рядка.
 * @return true, якщо послідовність валідна, інакше false.
 */
bool dyck_validate(const char* str, size_t len);

#ifdef __cplusplus
}
#endif

#endif // CATALAN_UTILS_H
