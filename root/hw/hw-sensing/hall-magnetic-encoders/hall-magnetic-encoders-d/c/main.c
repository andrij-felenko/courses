#include <stdint.h>
#include <stdbool.h>

#define AS5048A_CPR             16384     // 14 біт = 16384 відліків на оберт
#define AS5048A_CMD_ANGLE       0xFFFF     // Команда читання кута з бітом парності
#define AS5048A_CMD_CLEAR_ERR   0x4001     // Команда очищення регістра помилок
#define AS5048A_LUT_POINTS      32        // Точки калібрувальної таблиці

typedef struct {
    int32_t total_turns;
    uint16_t prev_raw_angle;
    bool is_initialized;
    
    // Калібрувальна таблиця похибок (у LSB для кожної з 32 рівновіддалених точок)
    int16_t error_lut[AS5048A_LUT_POINTS];
} as5048a_driver_t;

// Розрахунок біта парності Even Parity для 16-бітного кадру
static inline uint16_t as5048a_calc_parity(uint16_t value) {
    uint16_t count = 0;
    for (int i = 0; i < 16; i++) {
        if ((value >> i) & 1) count++;
    }
    return (count % 2) ? 0x8000 : 0x0000;
}

// Перевірка коректності отриманого кадру SPI
static inline bool as5048a_validate_frame(uint16_t rx_frame) {
    uint16_t count = 0;
    for (int i = 0; i < 16; i++) {
        if ((rx_frame >> i) & 1) count++;
    }
    // Кількість одиниць у слові включно з бітом 15 мусить бути парною
    if ((count % 2) != 0) return false;
    
    // Перевірка прапорця помилки Error Flag (Bit 14)
    if (rx_frame & 0x4000) return false;
    
    return true;
}

// Ініціалізація драйвера
void as5048a_init(as5048a_driver_t *dev, const int16_t *lut_32_points) {
    dev->total_turns = 0;
    dev->prev_raw_angle = 0;
    dev->is_initialized = false;
    
    for (int i = 0; i < AS5048A_LUT_POINTS; i++) {
        dev->error_lut[i] = lut_32_points ? lut_32_points[i] : 0;
    }
}

// Кусково-лінійна інтерполяція похибки за калібрувальною таблицею
static float as5048a_interpolate_error(const as5048a_driver_t *dev, uint16_t raw_angle) {
    // Крок сітки: 16384 / 32 = 512 відліків
    const uint16_t step = AS5048A_CPR / AS5048A_LUT_POINTS;
    uint16_t index_low = raw_angle / step;
    uint16_t index_high = (index_low + 1) % AS5048A_LUT_POINTS;
    
    uint16_t fraction = raw_angle % step;
    float t = (float)fraction / (float)step;
    
    float err_low = (float)dev->error_lut[index_low];
    float err_high = (float)dev->error_lut[index_high];
    
    return err_low + t * (err_high - err_low);
}

// Обробка прийнятого SPI слова: розгортання кута та лінеаризація
bool as5048a_update(as5048a_driver_t *dev, uint16_t rx_spi_frame, double *out_total_degrees) {
    if (!as5048a_validate_frame(rx_spi_frame)) {
        return false; // Помилка парності або Error Flag від чипа
    }
    
    // Витягуємо 14-бітний сирий кут (0..16383)
    uint16_t raw = rx_spi_frame & 0x3FFF;
    
    if (!dev->is_initialized) {
        dev->prev_raw_angle = raw;
        dev->total_turns = 0;
        dev->is_initialized = true;
    }
    
    // Фазове розгортання переходу через нуль (Unwrapping)
    int32_t delta = (int32_t)raw - (int32_t)dev->prev_raw_angle;
    if (delta > (AS5048A_CPR / 2)) {
        dev->total_turns--; // Перехід 0 -> 16383 (обертання проти стрілки)
    } else if (delta < -(AS5048A_CPR / 2)) {
        dev->total_turns++; // Перехід 16383 -> 0 (обертання за стрілкою)
    }
    dev->prev_raw_angle = raw;
    
    // Віднімання інтерпольованої похибки нелінійності
    float error_lsb = as5048a_interpolate_error(dev, raw);
    double corrected_single_turn_lsb = (double)raw - (double)error_lsb;
    
    // Повний неперервний кут у градусах
    double total_counts = (double)dev->total_turns * (double)AS5048A_CPR + corrected_single_turn_lsb;
    *out_total_degrees = (total_counts * 360.0) / (double)AS5048A_CPR;
    
    return true;
}
