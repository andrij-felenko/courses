/*
 * device_hal.h — контракт заліза портативного калібратора.
 *
 * Автомат станів не знає, чим саме керує: під цим заголовком може лежати
 * і драйвер дисплея з АЦП, і хостова заглушка, що просто друкує рядки.
 * Важливо лише те, що кожна дія входу/виходу стану має справжнього
 * виконавця, а не порожній коментар.
 */
#ifndef DEVICE_HAL_H
#define DEVICE_HAL_H

#include <stdbool.h>
#include <stdint.h>

/* Дисплей */
void hal_lcd_backlight(uint8_t percent);
void hal_menu_draw(uint8_t item);
void hal_settings_draw(uint8_t brightness, int16_t adc_offset, bool calibrated);
void hal_show_measurement(int16_t adc_offset);
void hal_show_about(void);
void hal_show_fault(uint8_t error_count);

/* Енергонезалежна пам'ять */
void hal_flash_save_settings(uint8_t brightness, int16_t adc_offset);

/* АЦП і калібрувальний генератор */
void hal_adc_calib_start(void);
int16_t hal_adc_calib_stop(void); /* повертає виміряне зміщення нуля */

/* Живлення */
void hal_enter_low_power(void);
void hal_exit_low_power(void);

/* Службовий друк для спостереження за порядком дій */
void hal_trace(const char *msg);

#endif /* DEVICE_HAL_H */
