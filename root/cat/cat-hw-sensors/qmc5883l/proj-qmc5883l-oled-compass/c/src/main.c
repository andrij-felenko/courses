#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include "i2c_driver.h"
#include "qmc5883l.h"
#include "ssd1306.h"

/**
 * @file main.c
 * @brief Приклад використання цифрового компаса QMC5883L з візуалізацією на OLED SSD1306.
 */

/* Імітація затримки мікроконтролера в мілісекундах */
static void delay_ms(uint32_t ms) {
    volatile uint32_t count = ms * 4000U;
    while (count--) {
        __asm__("nop");
    }
}

/* Формування текстової назви сторони світу за кутом */
static const char* get_cardinal_name(float heading) {
    if (heading >= 337.5f || heading < 22.5f)  return "N";
    if (heading >= 22.5f  && heading < 67.5f)  return "NE";
    if (heading >= 67.5f  && heading < 112.5f) return "E";
    if (heading >= 112.5f && heading < 157.5f) return "SE";
    if (heading >= 157.5f && heading < 202.5f) return "S";
    if (heading >= 202.5f && heading < 247.5f) return "SW";
    if (heading >= 247.5f && heading < 292.5f) return "W";
    if (heading >= 292.5f && heading < 337.5f) return "NW";
    return "N";
}

int main(void) {
    qmc5883l_t mag;
    ssd1306_t disp;

    /* 1. Ініціалізація апаратного модуля I2C на швидкості 400 кГц */
    if (i2c_init(I2C_SPEED_FAST) != I2C_OK) {
        return -1;
    }

    /* 2. Ініціалізація OLED-дисплея SSD1306 */
    if (ssd1306_init(&disp, SSD1306_I2C_ADDR_DEFAULT) != SSD1306_OK) {
        return -1;
    }

    /* Початковий заставка на дисплеї */
    ssd1306_clear(&disp);
    ssd1306_draw_string(&disp, 10, 10, "QMC5883L COMPASS", SSD1306_COLOR_WHITE);
    ssd1306_draw_string(&disp, 15, 30, "Initializing...", SSD1306_COLOR_WHITE);
    ssd1306_update(&disp);
    delay_ms(1000);

    /* 3. Ініціалізація магнітометра QMC5883L
     * Continuous mode, 100Hz ODR, ±8 Gauss Range, 512 OSR
     */
    qmc5883l_err_t err = qmc5883l_init(&mag, QMC5883L_I2C_ADDR,
                                       QMC5883L_MODE_CONTINUOUS,
                                       QMC5883L_ODR_100HZ,
                                       QMC5883L_RNG_8G,
                                       QMC5883L_OSR_512);
    if (err != QMC5883L_OK) {
        ssd1306_clear(&disp);
        ssd1306_draw_string(&disp, 10, 20, "SENSOR ERROR!", SSD1306_COLOR_WHITE);
        ssd1306_update(&disp);
        return -1;
    }

    /* Налаштування магнітного схилення (наприклад, +6.5° для Києва) */
    mag.declination_deg = 6.5f;

    /* 4. Фаза динамічного калібрування Min-Max (обертання пристрою у просторі) */
    ssd1306_clear(&disp);
    ssd1306_draw_string(&disp, 5, 5, "CALIBRATION MODE", SSD1306_COLOR_WHITE);
    ssd1306_draw_string(&disp, 5, 25, "Rotate 360 deg...", SSD1306_COLOR_WHITE);
    ssd1306_update(&disp);

    uint32_t calib_samples = 0;
    while (calib_samples < 300) {
        if (qmc5883l_is_data_ready(&mag)) {
            qmc5883l_raw_t raw;
            if (qmc5883l_read_raw(&mag, &raw) == QMC5883L_OK) {
                qmc5883l_calib_update(&mag.calib, &raw);
                calib_samples++;

                if (calib_samples % 30 == 0) {
                    char progress_buf[20];
                    snprintf(progress_buf, sizeof(progress_buf), "Progress: %lu%%", (unsigned long)(calib_samples * 100 / 300));
                    ssd1306_clear(&disp);
                    ssd1306_draw_string(&disp, 5, 5, "CALIBRATION MODE", SSD1306_COLOR_WHITE);
                    ssd1306_draw_string(&disp, 5, 25, "Rotate 360 deg...", SSD1306_COLOR_WHITE);
                    ssd1306_draw_string(&disp, 5, 45, progress_buf, SSD1306_COLOR_WHITE);
                    ssd1306_update(&disp);
                }
            }
        }
        delay_ms(10);
    }

    /* 5. Головний робочий цикл читання давача та візуалізації компаса */
    while (1) {
        if (qmc5883l_is_data_ready(&mag)) {
            qmc5883l_raw_t raw;
            if (qmc5883l_read_raw(&mag, &raw) == QMC5883L_OK) {
                /* Застосування калібрування Hard-Iron / Soft-Iron */
                float cal_x, cal_y, cal_z;
                qmc5883l_calib_apply(&mag.calib, &raw, &cal_x, &cal_y, &cal_z);

                /* Обчислення азимута */
                float heading = qmc5883l_compute_heading(cal_x, cal_y, mag.declination_deg);
                const char *cardinal = get_cardinal_name(heading);

                /* Малювання інтерфейсу компаса на OLED */
                ssd1306_clear(&disp);

                /* Циферблат компаса у лівій частині екрана (cx=32, cy=32, r=26) */
                ssd1306_draw_compass(&disp, 32, 32, 26, heading);

                /* Інформаційна панель у правій частині екрана */
                char text_buf[20];
                snprintf(text_buf, sizeof(text_buf), "%s", cardinal);
                ssd1306_draw_string(&disp, 75, 5, "DIR:", SSD1306_COLOR_WHITE);
                ssd1306_draw_string(&disp, 105, 5, text_buf, SSD1306_COLOR_WHITE);

                snprintf(text_buf, sizeof(text_buf), "%.1f deg", heading);
                ssd1306_draw_string(&disp, 68, 25, text_buf, SSD1306_COLOR_WHITE);

                snprintf(text_buf, sizeof(text_buf), "X:%-5d", (int)cal_x);
                ssd1306_draw_string(&disp, 68, 42, text_buf, SSD1306_COLOR_WHITE);

                snprintf(text_buf, sizeof(text_buf), "Y:%-5d", (int)cal_y);
                ssd1306_draw_string(&disp, 68, 52, text_buf, SSD1306_COLOR_WHITE);

                /* Оновлення екрана */
                ssd1306_update(&disp);
            }
        }
        delay_ms(50);
    }

    return 0;
}
