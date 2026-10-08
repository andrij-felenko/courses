#define RS360_CALIB_POINTS_MAX 8

typedef struct {
    float duty_percent; // Коефіцієнт заповнення ШІМ (0.0 .. 100.0%)
    float flow_ml_min;  // Прокачаний об'єм рідини за хвилину (мл/хв)
} rs360_calib_point_t;

typedef struct {
    rs360_calib_point_t points[RS360_CALIB_POINTS_MAX];
    uint8_t count;
} rs360_calib_table_t;

// Додавання або оновлення точки калібрування
rs360_error_t rs360_add_calib_point(rs360_handle_t dev, float duty_percent, float flow_ml_min);

// Розрахунок коефіцієнта заповнення ШІМ для заданої витрати методом шматочно-лінійної інтерполяції
float rs360_flow_to_duty(const rs360_calib_table_t *table, float target_flow_ml_min);
