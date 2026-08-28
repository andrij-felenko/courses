// Тривкий стан: піднімається зі сховища при старті (конфіг + калібрування).
typedef struct {
    float set_point;   // конфіг: задана користувачем температура, °C
    float cal_offset;  // калібрування: зсув саме цього термістора, °C
    float cal_slope;   // калібрування: нахил (зазвичай близько 1.0)
} persist_t;

persist_t cfg;                 // живе так, ніби лежить у Flash
storage_load(&cfg);            // при старті — читаємо збережене

float raw  = read_thermistor();          // сирий вимір = 22.1 (у SRAM, не зберігаємо)
float temp = raw * cfg.cal_slope + cfg.cal_offset;   // застосовуємо калібрування
bool  heat = temp < cfg.set_point;       // рішення про обігрів
