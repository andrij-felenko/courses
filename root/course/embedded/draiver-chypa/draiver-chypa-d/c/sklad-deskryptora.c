// C99: Структура дескриптора пристрою (Device Context)
typedef struct {
    const chip_bus_ops_t *bus_ops;      // Вказівники на функції читання/запису/затримки
    void                 *user_ctx;     // Непрозорий контекст платформи (хендл I2C/SPI)
    uint8_t               dev_addr;     // 7-бітна I2C адреса або індекс піна CS у SPI
    
    chip_range_t          range;        // Поточний налаштований діапазон вимірювань
    float                 scale_factor; // Чутливість: множник для переведення відліків у SI
    
    uint8_t               shadow_ctrl1; // Тіньова копія регістру CTRL1 в ОЗП
    uint8_t               shadow_ctrl4; // Тіньова копія регістру CTRL4 в ОЗП
    
    chip_calib_t          calib;        // Заводські коефіцієнти калібрування з NVM
    bool                  is_initialized; // Прапорець успішного завершення ініціалізації
} chip_dev_t;
