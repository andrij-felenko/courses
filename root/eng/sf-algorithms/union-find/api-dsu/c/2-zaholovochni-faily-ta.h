#ifndef DSU_H
#define DSU_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Статуси повернення функцій C DSU API.
 */
typedef enum {
    DSU_SUCCESS = 0,         /**< Операція виконана успішно */
    DSU_ERROR_NULL_POINTER,  /**< Передано нульовий покажчик */
    DSU_ERROR_OUT_OF_BOUNDS, /**< Індекс вузла виходить за межі [0, N-1] */
    DSU_ERROR_ALLOCATION    /**< Помилка виділення динамічної пам'яті */
} DSUStatus;

/**
 * @brief Непрозора структура даних DSU.
 */
typedef struct DSU DSU;

/**
 * @brief Створює та ініціалізує екземпляр DSU.
 * 
 * @param n Кількість елементів у множині (початково кожен елемент у власному класі).
 * @return DSU* Покажчик на створений екземпляр або NULL при помилці виділення пам'яті.
 * 
 * @note Часова складність: O(N). Просторова складність: O(N).
 */
DSU *dsu_create(size_t n);

/**
 * @brief Звільняє всі ресурси пам'яті, зайняті екземпляром DSU.
 * 
 * @param dsu Покажчик на екземпляр DSU (безпечно передавати NULL).
 */
void dsu_destroy(DSU *dsu);

/**
 * @brief Знаходить канонічного представника (корінь) множини для елемента x.
 * 
 * @param dsu Покажчик на екземпляр DSU.
 * @param x Індекс елемента [0, N-1].
 * @param out_root Покажчик для запису знайденого кореня.
 * @return DSUStatus DSU_SUCCESS або відповідний код помилки.
 * 
 * @note Використовує стиснення шляхів (Path Compression).
 * @note Часова складність: O(α(N)) амортизована.
 */
DSUStatus dsu_find(DSU *dsu, size_t x, size_t *out_root);

/**
 * @brief Об'єднує підмножини, що містять елементи x та y.
 * 
 * @param dsu Покажчик на екземпляр DSU.
 * @param x Індекс першого елемента.
 * @param y Індекс другого елемента.
 * @param out_unite_occurred Покажчик для запису прапорця (true якщо об'єднання відбулося).
 * @return DSUStatus DSU_SUCCESS або код помилки.
 * 
 * @note Використовує об'єднання за рангом (Union by Rank).
 * @note Часова складність: O(α(N)) амортизована.
 */
DSUStatus dsu_union(DSU *dsu, size_t x, size_t y, bool *out_unite_occurred);

/**
 * @brief Перевіряє, чи належать елементи x та y одній підмножині.
 * 
 * @param dsu Покажчик на екземпляр DSU.
 * @param x Індекс першого елемента.
 * @param y Індекс другого елемента.
 * @param out_is_connected Покажчик для запису результату перевірки.
 * @return DSUStatus DSU_SUCCESS або код помилки.
 */
DSUStatus dsu_is_connected(DSU *dsu, size_t x, size_t y, bool *out_is_connected);

/**
 * @brief Повертає кількість елементів у підмножині, до якої належить x.
 * 
 * @param dsu Покажчик на екземпляр DSU.
 * @param x Індекс елемента.
 * @param out_size Покажчик для запису розміру множини.
 * @return DSUStatus DSU_SUCCESS або код помилки.
 */
DSUStatus dsu_get_set_size(DSU *dsu, size_t x, size_t *out_size);

/**
 * @brief Повертає поточну кількість неперетинних підмножин.
 * 
 * @param dsu Покажчик на екземпляр DSU.
 * @param out_num_sets Покажчик для запису кількості множин.
 * @return DSUStatus DSU_SUCCESS або код помилки.
 */
DSUStatus dsu_get_num_sets(DSU *dsu, size_t *out_num_sets);

#ifdef __cplusplus
}
#endif

#endif // DSU_H
