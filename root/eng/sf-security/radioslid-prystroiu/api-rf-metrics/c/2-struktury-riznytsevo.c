/**
 * @brief Просторові координати географічної точки у системі WGS-84 або локальній площині.
 */
typedef struct {
    double x_meters;  /**< Координата X (Схід / Easting), метри */
    double y_meters;  /**< Координата Y (Північ / Northing), метри */
    double z_meters;  /**< Висота над рівнем моря (Altitude), метри */
} rf_geo_point_t;

/**
 * @brief Приймальна станція когерентної пеленгаційної мережі.
 */
typedef struct {
    uint32_t station_id;       /**< Унікальний ідентифікатор станції перехоплення */
    rf_geo_point_t location;   /**< Точні координати фазового центру антени станції */
    uint64_t timestamp_raw_ns; /**< Відмітка часу прийому фронту імпульсу (GPS/PTP), наносекунди */
    double snr_db;             /**< Рівень сигналу на приймачі, дБ */
    bool sync_locked;          /**< Прапорець наявності фазового замикання синхронізатора 1PPS */
} tdoa_sensor_node_t;

/**
 * @brief Результат розв'язання гіперболічної задачі позиціонування.
 */
typedef struct {
    rf_geo_point_t estimated_pos;  /**< Розраховані координати цілі */
    double gdop;                   /**< Геометричний фактор погіршення точності (Geometric Dilution) */
    double confidence_radius_m;    /**< Радіус круга ймовірного положення (CEP 95%), метри */
    uint32_t iterations_used;      /**< Кількість ітерацій алгоритму Гаусса-Ньютона */
    bool converged;                /**< Статус успішної збіжності розв'язку */
} tdoa_localization_result_t;
