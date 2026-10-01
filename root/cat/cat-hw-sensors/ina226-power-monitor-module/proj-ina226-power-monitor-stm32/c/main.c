#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include "ina226.h"
#include "oled_display.h"

// Прапор зовнішнього переривання EXTI від лінії ALERT монітора INA226
static volatile bool g_exti_alert_triggered = false;

// Апаратна імітація регістрів INA226 для демонстраційного запуску
typedef struct {
    uint16_t config;
    uint16_t shunt_volt;
    uint16_t bus_volt;
    uint16_t power;
    uint16_t current;
    uint16_t calibration;
    uint16_t mask_enable;
    uint16_t alert_limit;
    uint16_t manuf_id;
    uint16_t die_id;
} mock_ina226_regs_t;

static mock_ina226_regs_t g_mock_ina226 = {
    .config = 0x4127,
    .shunt_volt = 400,     // 400 * 2.5 мкВ = 1000 мкВ (1.0 мВ)
    .bus_volt = 9600,      // 9600 * 1.25 мВ = 12000 мВ (12.0 В)
    .power = 7200,         // Потужність
    .current = 1500,       // Струм
    .calibration = 0,
    .mask_enable = 0,
    .alert_limit = 0,
    .manuf_id = INA226_MANUFACTURER_ID_VAL,
    .die_id = INA226_DIE_ID_VAL
};

static bool g_alert_pin_state = false;

// Апаратний обробник зовнішнього переривання EXTI (лінія ALERT INA226)
void EXTI_ALERT_IRQHandler(void) {
    g_exti_alert_triggered = true;
    printf("   [EXTI ISR] -> Лінія ALERT активована! Запущено обробник переривання EXTI.\n");
}

// Низькорівнева функція запису по I2C
static bool hal_ina226_i2c_write(uint8_t dev_addr, const uint8_t *data, size_t len) {
    if (dev_addr != INA226_I2C_ADDR_DEFAULT || len < 1) return false;
    uint8_t reg = data[0];
    if (len == 1) return true;

    if (len == 3) {
        uint16_t val = ((uint16_t)data[1] << 8) | data[2];
        switch (reg) {
            case INA226_REG_CONFIG:
                g_mock_ina226.config = (val & INA226_CONFIG_RESET) ? 0x4127 : val;
                break;
            case INA226_REG_CALIBRATION:
                g_mock_ina226.calibration = val;
                break;
            case INA226_REG_MASK_ENABLE:
                g_mock_ina226.mask_enable = val;
                break;
            case INA226_REG_ALERT_LIMIT:
                g_mock_ina226.alert_limit = val;
                break;
            default:
                break;
        }
    }
    return true;
}

// Низькорівнева функція зчитування по I2C
static bool hal_ina226_i2c_read(uint8_t dev_addr, uint8_t *data, size_t len) {
    if (dev_addr != INA226_I2C_ADDR_DEFAULT || len != 2) return false;

    // Перевірка умови утворення тривоги ALERT (Power Over-Limit)
    if (g_mock_ina226.calibration > 0) {
        int32_t calc_curr = ((int32_t)(int16_t)g_mock_ina226.shunt_volt * g_mock_ina226.calibration) / 2048;
        g_mock_ina226.current = (uint16_t)calc_curr;

        uint32_t calc_pow = ((uint32_t)g_mock_ina226.current * g_mock_ina226.bus_volt) / 20000;
        g_mock_ina226.power = (uint16_t)calc_pow;

        if ((g_mock_ina226.mask_enable & INA226_MASK_POL) && 
            (g_mock_ina226.power > g_mock_ina226.alert_limit)) {
            g_mock_ina226.mask_enable |= INA226_FLAG_AFF;
            if (!g_alert_pin_state) {
                g_alert_pin_state = true;
                EXTI_ALERT_IRQHandler();
            }
        }
    }

    uint16_t reg_val = 0;
    if (data[0] == INA226_REG_CONFIG) reg_val = g_mock_ina226.config;
    else if (data[0] == INA226_REG_SHUNTVOLT) reg_val = g_mock_ina226.shunt_volt;
    else if (data[0] == INA226_REG_BUSVOLT) reg_val = g_mock_ina226.bus_volt;
    else if (data[0] == INA226_REG_POWER) reg_val = g_mock_ina226.power;
    else if (data[0] == INA226_REG_CURRENT) reg_val = g_mock_ina226.current;
    else if (data[0] == INA226_REG_CALIBRATION) reg_val = g_mock_ina226.calibration;
    else if (data[0] == INA226_REG_MASK_ENABLE) reg_val = g_mock_ina226.mask_enable;
    else if (data[0] == INA226_REG_ALERT_LIMIT) reg_val = g_mock_ina226.alert_limit;
    else if (data[0] == INA226_REG_MANUFACTURER_ID) reg_val = g_mock_ina226.manuf_id;
    else if (data[0] == INA226_REG_DIE_ID) reg_val = g_mock_ina226.die_id;
    else reg_val = g_mock_ina226.bus_volt;

    // Конвертація в порядок байтів Big-Endian
    data[0] = (uint8_t)(reg_val >> 8);
    data[1] = (uint8_t)(reg_val & 0xFF);
    return true;
}

// Заглушка I2C для графічного екрана OLED
static bool hal_oled_i2c_write(uint8_t dev_addr, const uint8_t *data, size_t len) {
    (void)dev_addr;
    (void)data;
    (void)len;
    return true;
}

int main(void) {
    printf("=========================================================\n");
    printf("  МОДУЛЬ ЦИФРОВОГО МОНІТОРА ЖИВЛЕННЯ INA226 ТА OLED (C)\n");
    printf("=========================================================\n\n");

    // 1. Початкове налаштування драйвера INA226
    // Параметри вимірювання: R_shunt = 10 мОм, Current LSB = 100 мкА (0.1 мА)
    ina226_config_t ina_cfg = {
        .i2c_addr       = INA226_I2C_ADDR_DEFAULT,
        .r_shunt_mohm   = 10,                        // 10 мОм
        .current_lsb_ua = 100,                       // 100 мкА/LSB
        .avg_samples    = INA226_AVG_16,             // Усереднення 16 вибірок
        .vbus_ct        = INA226_VBUS_1100US,        // 1.1 мс час перетворення Vbus
        .vsh_ct         = INA226_VSH_1100US,         // 1.1 мс час перетворення Vshunt
        .mode           = INA226_MODE_SHUNT_BUS_CONT // Безперервний вимір
    };

    ina226_t ina226;
    printf("[1/4] Ініціалізація модуля INA226 по I2C (Адреса: 0x%02X)...\n", ina_cfg.i2c_addr);
    if (!ina226_init(&ina226, &ina_cfg, hal_ina226_i2c_write, hal_ina226_i2c_read)) {
        printf("ПОМИЛКА: Не вдалося ініціалізувати пристрій INA226!\n");
        return EXIT_FAILURE;
    }

    printf("      Обчислене значення калібрувального регістру CAL = %u (0x%04X)\n", 
           ina226.cal_value, ina226.cal_value);
    printf("      Перевірка ID чипа: Manufacturer ID = 0x5449 (TI), Die ID = 0x2260 - УСПІШНО!\n");

    // 2. Налаштування межі ALERT (Power Over-Limit: 15 Вт = 15000 мВт)
    // Power LSB = 25 * Current LSB = 25 * 100 мкА = 2.5 мВт
    // Raw limit = 15000 мВт / 2.5 мВт = 6000
    uint16_t alert_limit_raw = 6000;
    uint16_t mask_flags = INA226_MASK_POL | INA226_MASK_LEN; // Фіксований режим (Latched)
    printf("\n[2/4] Налаштування лінії ALERT (EXTI):\n");
    printf("      Поріг Power Over-Limit (POL) = 15000 мВт (Raw limit = %u)\n", alert_limit_raw);
    ina226_configure_alert(&ina226, mask_flags, alert_limit_raw);

    // 3. Ініціалізація дисплея OLED SSD1306
    oled_t oled;
    printf("\n[3/4] Ініціалізація OLED дисплея SSD1306 (128x64, I2C 0x3C)...\n");
    if (!oled_init(&oled, OLED_I2C_ADDR_DEFAULT, hal_oled_i2c_write)) {
        printf("ПОМИЛКА: Не вдалося ініціалізувати OLED-дисплей!\n");
        return EXIT_FAILURE;
    }
    printf("      ОГО-дисплей успішно ініціалізовано.\n");

    // 4. Головний суперцикл вимірювання та відображення
    printf("\n[4/4] Запуск головного циклу вимірювань у реальному часі:\n");
    printf("---------------------------------------------------------\n");

    for (int cycle = 1; cycle <= 3; cycle++) {
        printf("\n>>> КРОК СУПЕРЦИКЛУ #%d <<<\n", cycle);

        // Симуляція стрибка струму на другому кроці для виклику переривання EXTI
        if (cycle == 2) {
            printf("   [СИМУЛЯЦІЯ]: Стрибок струму навантаження! (ShuntVolt = 6000 мкВ -> I = 1.5 А, P = 18 Вт)\n");
            g_mock_ina226.shunt_volt = 6000; // 15 мВ на 10 мОм = 1.5 А
        }

        ina226_data_t data;
        // Зчитування виміряних параметрів
        if (ina226_read_all(&ina226, &data)) {
            printf("   Фізичні параметри живлення (цілочисельні розрахунки):\n");
            printf("   - Напруга шини (Vbus):   %u мВ (%u.%03u В)\n", 
                   data.bus_voltage_mv, data.bus_voltage_mv / 1000, data.bus_voltage_mv % 1000);
            printf("   - Напруга шунта (Vshunt): %d мкВ (%d.%03d мВ)\n", 
                   data.shunt_voltage_uv, data.shunt_voltage_uv / 1000, abs(data.shunt_voltage_uv % 1000));
            printf("   - Струм (Current):        %d мА\n", data.current_ma);
            printf("   - Потужність (Power):     %u мВт (%u.%03u Вт)\n", 
                   data.power_mw, data.power_mw / 1000, data.power_mw % 1000);
        }

        // Обробка спрацьовування зовнішьного переривання EXTI
        bool alert_active = false;
        if (g_exti_alert_triggered) {
            alert_active = true;
            printf("   [ГОЛОВНИЙ ЦИКЛ]: Отримано сигнал ALERT від лінії EXTI!\n");

            uint16_t mask_reg = 0;
            if (ina226_read_mask_enable(&ina226, &mask_reg)) {
                if (mask_reg & INA226_FLAG_AFF) {
                    printf("   [ДІАГНОСТИКА]: Підтверджено прапор AFF в регістрі Mask/Enable INA226.\n");
                }
            }
            g_exti_alert_triggered = false; // Очищення прапора після обробки
        }

        // Рендеринг виміряних даних на екрані OLED
        oled_display_measurements(&oled, data.bus_voltage_mv, data.current_ma, data.power_mw, alert_active);
        printf("   [OLED]: Рендеринг даних на дисплеї завершено.\n");
    }

    printf("\n=========================================================\n");
    printf("  РОБОТУ ПРИКЛАДУ INA226 УСПІШНО ЗАВЕРШЕНО\n");
    printf("=========================================================\n");

    return EXIT_SUCCESS;
}
