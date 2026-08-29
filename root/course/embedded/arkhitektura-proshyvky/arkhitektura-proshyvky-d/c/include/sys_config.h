/* include/sys_config.h — загальносистемна конфігурація логера вібрації.
 * Єдине місце, де живуть числа, що залежать від конкретного виробу:
 * адреси мікросхем на шині, пороги аварій, розміри черг і періоди.
 * Жоден шар нижче застосунку сюди не заглядає. */
#ifndef SYS_CONFIG_H
#define SYS_CONFIG_H

/* --- Адреси мікросхем на шині I2C (7-бітні) --- */
#define SYS_I2C_ADDR_BME280        0x76u  /* вивід SDO притягнутий до землі */
#define SYS_I2C_ADDR_ADXL345       0x53u  /* ALT ADDRESS притягнутий до землі */

/* --- Розкладка черги подій --- */
#define SYS_EVENT_QUEUE_CAPACITY   32u

/* --- Періоди --- */
#define SYS_TICK_PERIOD_MS         100u   /* період системного тіку */
#define SYS_TELEMETRY_WINDOW_MS    10000u /* вікно усереднення телеметрії */

/* --- Пороги бізнес-політики --- */
#define SYS_TEMP_LIMIT_C           65.0f  /* перегрів насосної станції */
#define SYS_TEMP_HYSTERESIS_C      3.0f   /* гістерезис зняття тривоги */
#define SYS_VIBRATION_LIMIT_G      2.5f   /* аварійна вібрація підшипника */
#define SYS_SENSOR_FAULT_LIMIT     5u     /* невдалих опитувань поспіль до FAULT */

/* --- Індикація --- */
#define SYS_LED_BLINK_SLOW_MS      1000u
#define SYS_LED_BLINK_FAST_MS      150u

#endif /* SYS_CONFIG_H */
