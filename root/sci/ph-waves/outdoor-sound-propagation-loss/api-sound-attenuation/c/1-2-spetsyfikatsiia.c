/**
 * Статуси виконання акустичного розрахунку.
 */
typedef enum {
    ISO9613_SUCCESS               =  0,  /* Успішне обчислення */
    ISO9613_ERR_INVALID_POINTER   = -1,  /* Передано NULL вказівник */
    ISO9613_ERR_FREQ_OUT_OF_RANGE = -2,  /* Частота поза межами [50 Гц..1 МГц] */
    ISO9613_ERR_TEMP_OUT_OF_RANGE = -3,  /* Температура поза межами [-20°C..+50°C] */
    ISO9613_ERR_PRESS_OUT_OF_BOUNDS = -4, /* Тиск поза межами [10 кПа..200 кПа] */
    ISO9613_ERR_HUMIDITY_OUT_OF_RANGE = -5/* Вологість поза межами [0%..100%] */
} iso9613_status_t;

/**
 * Структура входів навколишнього середовища.
 */
typedef struct {
    double temperature_c;     /**< Температура повітря, °C */
    double pressure_kpa;      /**< Атмосферний тиск, кПа */
    double humidity_pct;      /**< Відносна вологість, % */
} iso9613_environment_t;

/**
 * Структура результату поглинання звуку.
 */
typedef struct {
    double alpha_db_m;        /**< Коефіцієнт загасання, дБ/м */
    double alpha_db_km;       /**< Коефіцієнт загасання, дБ/км */
    double fr_oxygen_hz;      /**< Частота релаксації кисню O2, Гц */
    double fr_nitrogen_hz;    /**< Частота релаксації азоту N2, Гц */
    double molar_humidity;    /**< Концентрація водяної пари, % */
    double alpha_classical;   /**< Внесок Стокса-Кірхгофа, дБ/м */
    double alpha_oxygen;      /**< Внесок релаксації кисню, дБ/м */
    double alpha_nitrogen;    /**< Внесок релаксації азоту, дБ/м */
} iso9613_attenuation_result_t;
