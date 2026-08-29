/*
 * device_hal_host.c — хостова реалізація контракту заліза.
 *
 * На платі тут були б регістри таймера підсвітки, драйвер дисплея та
 * контролер Flash; на хості кожна дія просто називає себе, щоб порядок
 * викликів Entry/Exit під час переходу можна було побачити очима.
 */
#include "device_hal.h"

#include <stdio.h>

static const char *const l_menu_names[] = {
    "Вимірювання",
    "Налаштування",
    "Про прилад"
};

/* Модель залізяки: генератор калібрувального сигналу і його показ. */
static bool l_calib_running = false;
static int16_t l_calib_raw = -37; /* те, що намірює АЦП цього разу */

void hal_lcd_backlight(uint8_t percent) {
    if (percent == 0U) {
        printf("  [LCD ] підсвітку вимкнено\n");
    } else {
        printf("  [LCD ] підсвітка %u%%\n", (unsigned)percent);
    }
}

void hal_menu_draw(uint8_t item) {
    const char *name = (item < 3U) ? l_menu_names[item] : "?";
    printf("  [LCD ] головне меню, виділено «%s»\n", name);
}

void hal_settings_draw(uint8_t brightness, int16_t adc_offset, bool calibrated) {
    printf("  [LCD ] налаштування: яскравість %u%%, зміщення %d (%s)\n",
           (unsigned)brightness, (int)adc_offset,
           calibrated ? "калібровано" : "заводське");
}

void hal_show_measurement(int16_t adc_offset) {
    printf("  [LCD ] вимірювання, поправка нуля %d\n", (int)adc_offset);
}

void hal_show_about(void) {
    printf("  [LCD ] калібратор, прошивка 1.4.0\n");
}

void hal_show_fault(uint8_t error_count) {
    printf("  [LCD ] АВАРІЯ давача, відмов поспіль: %u\n", (unsigned)error_count);
}

void hal_flash_save_settings(uint8_t brightness, int16_t adc_offset) {
    printf("  [FLASH] збережено: яскравість %u%%, зміщення %d\n",
           (unsigned)brightness, (int)adc_offset);
}

void hal_adc_calib_start(void) {
    l_calib_running = true;
    printf("  [ADC ] калібрувальний генератор увімкнено\n");
}

int16_t hal_adc_calib_stop(void) {
    if (!l_calib_running) {
        /* Подвійна зупинка означала б, що Q_EXIT_SIG прийшов двічі —
         * це вада рушія, а не заліза, і мовчати про неї не можна. */
        printf("  [ADC ] ПОМИЛКА: зупинка незапущеного генератора\n");
        return 0;
    }
    l_calib_running = false;
    printf("  [ADC ] генератор вимкнено, виміряне зміщення %d\n", (int)l_calib_raw);
    /* Наступний запуск дасть трохи інше значення — як і справжній АЦП. */
    l_calib_raw = (int16_t)(l_calib_raw + 5);
    return (int16_t)(l_calib_raw - 5);
}

void hal_enter_low_power(void) {
    printf("  [PWR ] режим мікроспоживання\n");
}

void hal_exit_low_power(void) {
    printf("  [PWR ] повне тактування ядра\n");
}

void hal_trace(const char *msg) {
    printf("  [ ] %s\n", msg);
}
