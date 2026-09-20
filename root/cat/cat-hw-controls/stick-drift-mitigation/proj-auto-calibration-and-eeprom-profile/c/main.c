#include <stdio.h>
#include "stick_calibration.h"

// Змінні симуляції апаратного АЦП для тестування
static uint16_t g_sim_adc_x = 2080; // Нейтраль X з невеликим дрейфом
static uint16_t g_sim_adc_y = 2010; // Нейтраль Y з невеликим дрейфом

static uint16_t mock_adc_read(uint8_t channel) {
    if (channel == 0) return g_sim_adc_x;
    if (channel == 1) return g_sim_adc_y;
    return 0;
}

void print_vector_info(const char *label, uint16_t raw_x, uint16_t raw_y, const stick_vector_t *vec) {
    printf("[%s]\n", label);
    printf("  Сирі АЦП: X=%4u, Y=%4u | Статус: 0x%02X\n", raw_x, raw_y, vec->status_flags);
    if (vec->status_flags == STICK_STATUS_OK) {
        printf("  Вектор: X=%+.3f, Y=%+.3f | Амплітуда: %.3f | Мертва зона: %s\n",
               vec->x, vec->y, vec->magnitude, vec->is_in_deadzone ? "ТАК" : "НІ");
    } else if (vec->status_flags & STICK_STATUS_ERR_CRC) {
        printf("  [ПОМИЛКА] Пошкоджено CRC16 профілю калібрування!\n");
    } else if (vec->status_flags & STICK_STATUS_ERR_SENSOR_FAULT) {
        printf("  [ПОМИЛКА] Апаратний збій сенсора АЦП (out-of-bounds)!\n");
    }
    printf("\n");
}

int main(void) {
    printf("=== Драйвер калібрування та обробки аналогового стіка (C) ===\n\n");

    stick_calibration_profile_t profile;
    const uint32_t eeprom_slot = 0x10;

    // 1. Проведення сесії автокалібрування нуля при старті
    printf("1. Збір 100 вибірок АЦП у нейтральному стані...\n");
    if (stick_calibrate_neutral(mock_adc_read, &profile, 100)) {
        printf("   Калібрування успішне: Center X=%u, Center Y=%u, CRC16=0x%04X\n\n",
               profile.adc_center_x, profile.adc_center_y, profile.crc16);
    } else {
        printf("   [ПОМИЛКА] Збій під час калібрування!\n");
        return 1;
    }

    // 2. Збереження профілю в EEPROM
    if (stick_save_profile(&profile, eeprom_slot)) {
        printf("2. Профіль успішно збережено в EEPROM (адреса 0x%02X).\n\n", eeprom_slot);
    }

    // 3. Зчитання та перевірка цілісності профілю з EEPROM
    stick_calibration_profile_t loaded_profile;
    if (stick_load_profile(&loaded_profile, eeprom_slot)) {
        printf("3. Профіль зчитано з EEPROM та верифіковано за CRC16.\n\n");
    } else {
        printf("3. [ПОМИЛКА] Не вдалося верифікувати профіль з EEPROM!\n\n");
        return 1;
    }

    // 4. Симуляція роботи стіка в різних положеннях
    stick_vector_t vec;

    // Тест 4.1: Стік у нейтралі (з дрейфом нуля)
    stick_apply_calibration(&loaded_profile, 2085, 2012, &vec);
    print_vector_info("Тест 1: Нейтраль у спокої (дрейф відфільтровано)", 2085, 2012, &vec);

    // Тест 4.2: Легке відхилення всередині мертвої зони
    stick_apply_calibration(&loaded_profile, 2200, 2010, &vec);
    print_vector_info("Тест 2: Легкий поштовх (всередині мертвої зони)", 2200, 2010, &vec);

    // Тест 4.3: Повне відхилення по діагоналі вгору-вправо
    stick_apply_calibration(&loaded_profile, 3800, 3750, &vec);
    print_vector_info("Тест 3: Рух по діагоналі вгору-вправо", 3800, 3750, &vec);

    // Тест 4.4: Апаратний збій (обрив провідника АЦП = 0)
    stick_apply_calibration(&loaded_profile, 0, 2010, &vec);
    print_vector_info("Тест 4: Апаратний збій сенсора АЦП", 0, 2010, &vec);

    // Тест 4.5: Пошкодження профілю в EEPROM (симуляція пошкодження CRC16)
    loaded_profile.crc16 ^= 0xFFFF;
    stick_apply_calibration(&loaded_profile, 3000, 3000, &vec);
    print_vector_info("Тест 5: Перевірка захисту від пошкодження CRC16", 3000, 3000, &vec);

    return 0;
}
