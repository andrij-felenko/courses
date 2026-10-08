#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define GP2Y0A21_LUT_POINTS 11

// Структура вузла калібрувальної таблиці
typedef struct {
    uint16_t voltage_mv;
    uint16_t distance_mm;
} gp2y0a21_calib_node_t;

// Калібрувальний профіль, що зберігається в NVS / EEPROM
typedef struct {
    gp2y0a21_calib_node_t nodes[GP2Y0A21_LUT_POINTS];
    uint16_t crc16;
} gp2y0a21_calib_profile_t;

// Головна структура драйвера далекоміра
typedef struct {
    gp2y0a21_calib_profile_t calib;
    gp2y0a21_diag_t          diag;
    signal_filter_t          filter;
    bool                     is_calibrated;
} gp2y0a21_dev_t;

// Обчислення простої контрольної суми CRC16 для перевірки пам'яті
static uint16_t calculate_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

// Ініціалізація драйвера за замовчуванням
void gp2y0a21_init(gp2y0a21_dev_t *dev, float alpha) {
    signal_filter_init(&dev->filter, alpha);
    gp2y0a21_diag_init(&dev->diag);
    
    // Заводський стандартний профіль LUT
    static const gp2y0a21_calib_node_t default_lut[GP2Y0A21_LUT_POINTS] = {
        {3100, 100}, {2500, 120}, {2000, 150}, {1550, 200},
        {1250, 250}, {1050, 300}, {800,  400}, {650,  500},
        {520,  600}, {450,  700}, {400,  800}
    };
    memcpy(dev->calib.nodes, default_lut, sizeof(default_lut));
    dev->calib.crc16 = calculate_crc16((const uint8_t*)dev->calib.nodes, sizeof(default_lut));
    dev->is_calibrated = false;
}

// Завантаження індивідуального калібрування з пам'яті
bool gp2y0a21_load_calibration(gp2y0a21_dev_t *dev, const gp2y0a21_calib_profile_t *profile) {
    uint16_t expected_crc = calculate_crc16((const uint8_t*)profile->nodes, sizeof(profile->nodes));
    if (profile->crc16 != expected_crc) {
        return false; // Помилка цілісності даних
    }
    memcpy(&dev->calib, profile, sizeof(gp2y0a21_calib_profile_t));
    dev->is_calibrated = true;
    return true;
}

// Головна функція конвеєра: зчитування, фільтрація, діагностика та перерахунок
gp2y0a21_status_t gp2y0a21_read_distance(gp2y0a21_dev_t *dev, uint16_t raw_adc_mv, uint16_t *out_dist_mm) {
    // 1. Цифрова фільтрація (медіана + EMA)
    uint16_t filtered_mv = signal_filter_update(&dev->filter, raw_adc_mv);

    // 2. Перевірка граничних станів та сліпої зони
    gp2y0a21_status_t status = gp2y0a21_diagnose_voltage(&dev->diag, filtered_mv);
    if (status != GP2Y0A21_STATUS_OK) {
        if (status == GP2Y0A21_STATUS_BLIND_ZONE) {
            *out_dist_mm = dev->calib.nodes[0].distance_mm;
        } else if (status == GP2Y0A21_STATUS_TOO_FAR) {
            *out_dist_mm = dev->calib.nodes[GP2Y0A21_LUT_POINTS - 1].distance_mm;
        } else {
            *out_dist_mm = 0;
        }
        return status;
    }

    // 3. Таблична кусково-лінійна інтерполяція за індивідуальною LUT
    for (size_t i = 0; i < GP2Y0A21_LUT_POINTS - 1; i++) {
        if (filtered_mv <= dev->calib.nodes[i].voltage_mv && 
            filtered_mv >= dev->calib.nodes[i + 1].voltage_mv) {
            
            int32_t v1 = dev->calib.nodes[i].voltage_mv;
            int32_t v2 = dev->calib.nodes[i + 1].voltage_mv;
            int32_t d1 = dev->calib.nodes[i].distance_mm;
            int32_t d2 = dev->calib.nodes[i + 1].distance_mm;

            int32_t dist = d1 + ((int32_t)(filtered_mv - v1) * (d2 - d1)) / (v2 - v1);
            *out_dist_mm = (uint16_t)dist;
            return GP2Y0A21_STATUS_OK;
        }
    }

    *out_dist_mm = dev->calib.nodes[GP2Y0A21_LUT_POINTS - 1].distance_mm;
    return GP2Y0A21_STATUS_TOO_FAR;
}
