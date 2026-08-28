/* c */
typedef struct {
    /* Вектор зсуву твердого заліза (Hard-Iron Bias, [мкТл]) */
    float hard_iron_bias[3];
    
    /* 3x3 симетрична матриця масштабу й повороту м'якого заліза (Soft-Iron Matrix) */
    float soft_iron_matrix[3][3];
    
    /* Очікуваний повний модуль поля Землі у цій локації [мкТл] */
    float expected_total_field_uT;
    
    /* Нормалізований кут магнітного нахилу цієї локації [градуси] */
    float expected_inclination_deg;
} mag_calibration_t;
