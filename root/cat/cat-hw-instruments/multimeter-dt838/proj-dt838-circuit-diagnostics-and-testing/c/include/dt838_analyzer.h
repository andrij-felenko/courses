#ifndef DT838_ANALYZER_H
#define DT838_ANALYZER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Порогові значення для режимів вимірювання DT-838 (у мВ та Омах)
 */
#define DT838_DIODE_SHORT_MV        50.0f   /**< Нижній поріг пробою p-n переходу (коротке замикання) */
#define DT838_DIODE_GE_MIN_MV      150.0f   /**< Мінімальний спад для германієвих діодів / Шотткі */
#define DT838_DIODE_GE_MAX_MV      400.0f   /**< Максимальний спад для германієвих діодів */
#define DT838_DIODE_SI_MIN_MV      450.0f   /**< Мінімальний спад для кремнієвих p-n переходів */
#define DT838_DIODE_SI_MAX_MV      850.0f   /**< Максимальний спад для кремнієвих p-n переходів */
#define DT838_DIODE_LED_MIN_MV    1500.0f   /**< Мінімальний спад для світлодіодів (LED) */
#define DT838_DIODE_LED_MAX_MV    2800.0f   /**< Максимальний спад для світлодіодів */
#define DT838_DIODE_OPEN_MV       3000.0f   /**< Поріг незамкненого кола (напруга холостого ходу АЦП) */

#define DT838_CONTINUITY_BEEP_OHM   50.0f   /**< Поріг спрацьовування звукового зумера прозвонки (Ом) */
#define DT838_TRANSISTOR_IB_UA      10.0f   /**< Струм бази в гнізді hFE (мкА) */

/**
 * @brief Класифікація результатів перевірки p-n переходу
 */
typedef enum {
    DIODE_TYPE_SHORT_CIRCUIT = 0, /**< Коротке замикання / пробитий p-n перехід */
    DIODE_TYPE_GERMANIUM,         /**< Германієвий діод або діод Шотткі (0.15–0.4 В) */
    DIODE_TYPE_SILICON,           /**< Кремнієвий діод або переход транзистора (0.45–0.85 В) */
    DIODE_TYPE_LED,               /**< Світлодіод (1.5–2.8 В) */
    DIODE_TYPE_OPEN_CIRCUIT,      /**< Обрив кола / зворотне включення */
    DIODE_TYPE_UNKNOWN            /**< Нетипове значення спаду напруги */
} dt838_diode_type_t;

/**
 * @brief Стан перевірки цілісності кола (прозвонки)
 */
typedef enum {
    CONTINUITY_CLOSED_BEEP = 0,   /**< Замкнене коло, активний зумер (R < 50 Ом) */
    CONTINUITY_RESISTIVE,         /**< Перехідний опір без звукового сигналу */
    CONTINUITY_OPEN               /**< Відкрите коло / перевищення діапазону (Оверлоад) */
} dt838_continuity_state_t;

/**
 * @brief Результат аналізу p-n переходу
 */
typedef struct {
    float voltage_drop_mv;         /**< Виміряний спад напруги (мВ) */
    dt838_diode_type_t type;       /**< Визначений тип напівпровідника */
    const char *description;       /**< Текстовий опис стану */
} dt838_diode_result_t;

/**
 * @brief Результат звукової прозвонки та вимірювання опору
 */
typedef struct {
    float resistance_ohm;          /**< Виміряний опір (Ом) */
    dt838_continuity_state_t state;/**< Стан цілісності кола */
    bool beeper_active;            /**< Прапор включення звукового сигналу */
} dt838_continuity_result_t;

/**
 * @brief Результат вимірювання параметрів транзистора в гнізді hFE
 */
typedef struct {
    float collector_current_ua;    /**< Виміряний струм колектора (мкА) */
    float hfe_gain;                /**< Обчислений коефіцієнт підсилення hFE */
    bool valid;                    /**< Прапор коректності вимірювання (0 <= hFE <= 1000) */
} dt838_hfe_result_t;

/* Функції первинного аналізу */
dt838_diode_result_t dt838_analyze_diode(float raw_voltage_mv);
dt838_continuity_result_t dt838_analyze_continuity(float raw_resistance_ohm);
dt838_hfe_result_t dt838_calculate_hfe(float measured_ic_ua);

#endif /* DT838_ANALYZER_H */
