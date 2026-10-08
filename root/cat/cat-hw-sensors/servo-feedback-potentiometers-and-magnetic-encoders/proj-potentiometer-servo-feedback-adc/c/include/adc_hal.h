#ifndef ADC_HAL_H
#define ADC_HAL_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Перелічення роздільної здатності АЦП мікроконтролера.
 */
typedef enum {
    ADC_RESOLUTION_10BIT = 1023,
    ADC_RESOLUTION_12BIT = 4095,
    ADC_RESOLUTION_16BIT = 65535
} adc_resolution_t;

/**
 * @brief Структура конфігурації аналогового каналу АЦП.
 */
typedef struct {
    uint8_t channel_id;           /**< Ідентифікатор аналогового каналу GPIO */
    adc_resolution_t resolution;  /**< Роздільна здатність АЦП (максимальне цифрове кодування) */
    float vref_volts;             /**< Опорна напруга живлення АЦП у вольтах (3.3V або 5.0V) */
    uint32_t sampling_time_cycles;/**< Час вибірки у циклах тактування АЦП */
} adc_channel_config_t;

/**
 * @brief Дескриптор периферійного модуля АЦП.
 */
typedef struct {
    adc_channel_config_t config;  /**< Налаштування аналогового каналу */
    bool is_initialized;          /**< Прапорець успішної ініціалізації периферії */
    float simulated_input_volts;  /**< Фізична напруга для симуляції сигналу зворотного зв'язку */
    float noise_amplitude_volts;  /**< Амплітуда високочастотного шуму на аналоговій лінії */
} adc_handle_t;

/**
 * @brief Ініціалізація апаратного модуля АЦП для зчитування потенціометра/енкодера.
 * 
 * @param handle Вказівник на дескриптор АЦП.
 * @param channel_id Номер аналогового каналу.
 * @param res Роздільна здатність АЦП.
 * @param vref_volts Опорна напруга АЦП у вольтах.
 * @return true Якщо ініціалізацію проведено успішно, false у разі помилки.
 */
bool adc_hal_init(adc_handle_t *handle, uint8_t channel_id, adc_resolution_t res, float vref_volts);

/**
 * @brief Зчитування сирого цифрового кодування з АЦП (0..ADC_RESOLUTION).
 * 
 * @param handle Вказівник на дескриптор АЦП.
 * @return uint16_t Сирий цифровий код АЦП.
 */
uint16_t adc_hal_read_raw(adc_handle_t *handle);

/**
 * @brief Перетворення сирого кодування АЦП у фізичну напругу (Вольти).
 * 
 * @param handle Вказівник на дескриптор АЦП.
 * @param raw_val Сирий код АЦП.
 * @return float Обчислена напруга у Вольтах.
 */
float adc_hal_raw_to_volts(const adc_handle_t *handle, uint16_t raw_val);

/**
 * @brief Встановлення симульованого значення напруги та рівня шуму (для тестування).
 * 
 * @param handle Вказівник на дескриптор АЦП.
 * @param target_volts Базова напруга зворотного зв'язку (V).
 * @param noise_volts Амплітуда випадкового електричного шуму (V).
 */
void adc_hal_set_simulated_input(adc_handle_t *handle, float target_volts, float noise_volts);

#endif /* ADC_HAL_H */
