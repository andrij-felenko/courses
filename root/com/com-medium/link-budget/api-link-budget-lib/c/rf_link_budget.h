/* Файл: rf_link_budget.h */
#ifndef RF_LINK_BUDGET_H
#define RF_LINK_BUDGET_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Коди повернення методів розрахунку бюджету лінії
 */
typedef enum {
    RF_BUDGET_OK = 0,                   /**< Успішне виконання розрахунку */
    RF_BUDGET_ERR_INVALID_PARAM = -1,   /**< Передано нулевий вказівник або NaN/Inf */
    RF_BUDGET_ERR_FREQ_OUT_OF_RANGE = -2,/**< Частота поза межами допустимого діапазону */
    RF_BUDGET_ERR_ZERO_DISTANCE = -3    /**< Відстань дорівнює нулю або від'ємна */
} rf_budget_status_t;

/**
 * @brief Структура параметрів передавального тракту (TX)
 */
typedef struct {
    float power_dbm;       /**< Вихідна потужність передавача (-30.0 .. +53.0 dBm) */
    float tx_cable_loss_db;/**< Сумарні втрати фідерного тракту TX (dB) */
    float antenna_gain_dbi;/**< Коефіцієнт підсилення антени TX (dBi) */
} rf_tx_params_t;

/**
 * @brief Структура параметрів приймального тракту (RX)
 */
typedef struct {
    float rx_antenna_gain_dbi;/**< Коефіцієнт підсилення антени RX (dBi) */
    float rx_cable_loss_db;   /**< Сумарні втрати фідерного тракту RX (dB) */
    float bandwidth_hz;       /**< Еквівалентна шумова смуга приймача (Гц) */
    float noise_figure_db;    /**< Коефіцієнт шуму приймача N_F (dB) */
    float required_snr_db;    /**< Поріг демодуляції SNR_min (dB) */
} rf_rx_params_t;

/**
 * @brief Структура умов середовища поширення хвиль
 */
typedef struct {
    float frequency_mhz;   /**< Робоча частота (1.0 МГц .. 100 000.0 МГц) */
    float distance_km;     /**< Фізична відстань між антенами (км) */
    float atmospheric_loss_db;/**< Втрати в атмосфері (dB) */
    float fading_margin_db;   /**< Запас на інтерференційні завмирання (dB) */
    float polarization_loss_db;/**< Втрати розузгодження поляризації (dB) */
} rf_channel_params_t;

/**
 * @brief Структура підсумкових результатів розрахунку
 */
typedef struct {
    float eirp_dbm;         /**< EIRP передавача (dBm) */
    float fspl_db;          /**< Втрати у вільному просторі FSPL (dB) */
    float total_path_loss_db;/**< Повні сумарні втрати у трасі (dB) */
    float rx_power_dbm;     /**< Розрахункова потужність сигналу у RX (dBm) */
    float sensitivity_dbm;  /**< Порогова чутливість приймача (dBm) */
    float link_margin_db;   /**< Запас радіолінії Margin (dB) */
    float max_range_km;     /**< Гранична відстань зв'язку при Margin = 0 (км) */
} rf_budget_report_t;

/**
 * @brief Виконати повний розрахунок балансу потужності радіолінії
 * 
 * Функція обчислює всі параметри енергетичного балансу на основі наданих
 * структур передавача, каналу та приймача.
 * 
 * @param[in]  tx      Вказівник на конфігурацію передавача (не NULL)
 * @param[in]  channel Вказівник на параметри каналу поширення (не NULL)
 * @param[in]  rx      Вказівник на конфігурацію приймача (не NULL)
 * @param[out] report  Вказівник на структуру збереження результатів (не NULL)
 * @return RF_BUDGET_OK у разі успішного розрахунку, або код помилки
 */
rf_budget_status_t rf_calculate_link_budget(const rf_tx_params_t *tx,
                                            const rf_channel_params_t *channel,
                                            const rf_rx_params_t *rx,
                                            rf_budget_report_t *report);

/**
 * @brief Обчислити необхідну потужність передавача для забезпечення заданого запасу
 * 
 * @param[in]  target_margin_db Бажаний запас лінії (наприклад, +10.0 dB)
 * @param[in]  channel          Параметри каналу поширення
 * @param[in]  rx               Параметри приймача
 * @param[in]  tx_gain_dbi      Підсилення антени TX (dBi)
 * @param[in]  tx_cable_loss_db Втрати кабелю TX (dB)
 * @param[out] req_power_dbm    Розрахована вихідна потужність передавача (dBm)
 * @return RF_BUDGET_OK у разі успіху
 */
rf_budget_status_t rf_estimate_required_tx_power(float target_margin_db,
                                                 const rf_channel_params_t *channel,
                                                 const rf_rx_params_t *rx,
                                                 float tx_gain_dbi,
                                                 float tx_cable_loss_db,
                                                 float *req_power_dbm);

#ifdef __cplusplus
}
#endif

#endif /* RF_LINK_BUDGET_H */
