#ifndef HX711_PULLOUT_H
#define HX711_PULLOUT_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Структура конфігурації та стану тензодатчика HX711 для стенда виривання втулок.
 */
typedef struct {
    int sck_pin;             /**< Номер цифрового виводу синхронізації SCK */
    int dout_pin;            /**< Номер цифрового виводу послідовних даних DOUT */
    int32_t tare_offset;     /**< Зсув нуля (тари) у сирих відліках 24-бітного АЦП */
    float scale_factor;      /**< Калібрувальний коефіцієнт чутливості (відліків на 1 Ньютон) */
    float ema_alpha;         /**< Коефіцієнт експоненційного фільтра (0.0 ... 1.0) */
    float current_force_n;   /**< Поточне відфільтроване зусилля натягу (Н) */
    float peak_force_n;      /**< Максимальне зафіксоване пікове зусилля виривання (Н) */
} hx711_pullout_t;

/**
 * @brief Ініціалізує контекст вимірювального модуля HX711.
 * @param sensor Вказівник на екземпляр структури датчика.
 * @param sck_pin Номер виводу тактового сигналу.
 * @param dout_pin Номер виводу даних.
 * @param scale_factor Калібрувальний коефіцієнт (відліків/Н).
 * @param ema_alpha Ваговий коефіцієнт фільтра EMA.
 */
void hx711_init(hx711_pullout_t *sensor, int sck_pin, int dout_pin, float scale_factor, float ema_alpha);

/**
 * @brief Перевіряє готовність АЦП до видачі даних (DOUT знаходиться у низькому стані).
 * @param sensor Вказівник на датчик.
 * @return true, якщо перетворення завершено і лінія DOUT низька.
 */
bool hx711_is_ready(const hx711_pullout_t *sensor);

/**
 * @brief Зчитує 24-бітний сирий відлік АЦП зі знаковим розширенням до int32_t.
 * @param sensor Вказівник на датчик.
 * @return Сире знакове значення коду АЦП.
 */
int32_t hx711_read_raw(const hx711_pullout_t *sensor);

/**
 * @brief Виконує тарування (обчислює середній нульовий зсув за вказану кількість вибірок).
 * @param sensor Вказівник на датчик.
 * @param sample_count Кількість вибірок для усереднення.
 */
void hx711_tare(hx711_pullout_t *sensor, uint8_t sample_count);

/**
 * @brief Опитує датчик, оновлює поточне зусилля в Ньютонах з EMA-фільтрацією та фіксує пік.
 * @param sensor Вказівник на датчик.
 * @return Поточне відфільтроване зусилля виривання (Н).
 */
float hx711_update_force(hx711_pullout_t *sensor);

/**
 * @brief Скидає збережене пікове значення перед початком нового випробування.
 * @param sensor Вказівник на датчик.
 */
void hx711_reset_peak(hx711_pullout_t *sensor);

/**
 * @brief Повертає максимальне зареєстроване пікове зусилля виривання.
 * @param sensor Вказівник на датчик.
 * @return Пікове зусилля (Н).
 */
float hx711_get_peak_force(const hx711_pullout_t *sensor);

#ifdef __cplusplus
}
#endif

#endif /* HX711_PULLOUT_H */
