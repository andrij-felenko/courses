/**
 * @brief Оцінка ймовірності виявлення радіометром.
 */
typedef struct {
    double bandwidth_hz;     /**< Смуга аналізу радіометра, Гц */
    double integration_time_s; /**< Час інтегрування енергії, с */
    double target_snr_db;    /**< Рівень сигналу цілі відносно шуму, дБ */
    double prob_false_alarm; /**< Задана ймовірність хибної тривоги (наприклад, 1e-4) */
    double prob_detection;   /**< Розрахована ймовірність виявлення [0.0 .. 1.0] */
    double detection_margin_db; /**< Запас скритності (від'ємне значення = сигнал приховано) */
} rf_detection_margin_t;
