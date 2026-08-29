/* platform.h — контракт заліза для польового модуля.
 *
 * Усе, що вище цього шару (журнал причин перезапуску, порятунок шини,
 * супервізор середовища), про регістри не знає нічого. Порт один —
 * STM32F407, platform_stm32f4.c.
 */
#ifndef PLATFORM_H
#define PLATFORM_H

#include <stdbool.h>
#include <stdint.h>

/* Частота, яку виставив стартовий код до входу в main(). */
#define PLAT_HCLK_BASE_HZ 168000000u

/* Керовані навантаження: усе, що в полі здатне посадити шину живлення
 * або перегріти корпус, вмикається ЛИШЕ через цей перелік. */
typedef enum {
    PLAT_LOAD_RADIO = 0, /* передавач: імпульс до 2 А */
    PLAT_LOAD_HEATER,    /* плівковий підігрів плати */
    PLAT_LOAD_CHARGER,   /* дозвіл заряду акумулятора */
    PLAT_LOAD_COUNT
} plat_load_t;

/* Канали АЦП, розведені на платі. */
#define PLAT_ADC_CH_NTC 0u  /* PA0: дільник 10 кОм + NTC 10 кОм на землю */
#define PLAT_ADC_CH_VBAT 1u /* PA1: дільник 100к/100к від акумулятора */

#define PLAT_ADC_FULL_SCALE 4095u
#define PLAT_ADC_VREF_MV 3300u

/* Скільки 32-бітних слів має резервний домен RTC (BKP0R..BKP19R). */
#define PLAT_BKP_WORDS 20u

void plat_init(void);

/* --- причина перезапуску ------------------------------------------------- */

/* Сире значення RCC_CSR, зняте один раз при старті, без інтерпретації:
 * розшифровує його fault_log, бо саме там живе політика. */
uint32_t plat_reset_flags_raw(void);

/* --- час ----------------------------------------------------------------- */

uint32_t plat_millis(void);
void plat_delay_us(uint32_t us);

/* --- тактування ---------------------------------------------------------- */

/* Дільник шини ядра: 0 → /1, 1 → /2, 2 → /4, 3 → /8, 4 → /16.
 * Знижувати частоту можна без правки затримок флешу; піднімати —
 * лише назад до тієї, під яку затримки вже налаштовані. */
void plat_set_core_divider(uint8_t div_log2);
uint32_t plat_core_hz(void);

/* --- навантаження -------------------------------------------------------- */

void plat_load_set(plat_load_t load, bool on);
bool plat_load_get(plat_load_t load);

/* --- вимірювання --------------------------------------------------------- */

/* false → перетворення не завершилося у відведений час (АЦП завис,
 * зникло тактування). Значення *counts у цьому разі не чіпається. */
bool plat_adc_read(uint8_t channel, uint16_t *counts);

/* --- резервна пам'ять ---------------------------------------------------- */

bool plat_bkp_read(uint8_t index, uint32_t *value);
bool plat_bkp_write(uint8_t index, uint32_t value);

/* --- шина I2C ------------------------------------------------------------ */

typedef enum {
    PLAT_I2C_OK = 0,
    PLAT_I2C_TIMEOUT, /* шина не віддала очікувану подію — кандидат на порятунок */
    PLAT_I2C_NACK,    /* пристрій не відповів, але шина жива */
    PLAT_I2C_BUSY     /* лінія тримається низько ще до старту */
} plat_i2c_status_t;

void plat_i2c_init(void);

/* Коротка транзакція «чи ти тут»: адреса плюс нуль байтів даних. */
plat_i2c_status_t plat_i2c_probe(uint8_t addr7);
plat_i2c_status_t plat_i2c_read_reg(uint8_t addr7, uint8_t reg, uint8_t *buf, uint8_t len);

/* Ручне керування SCL/SDA для процедури порятунку шини. Ніжки лишаються
 * з відкритим стоком: писати можна лише нуль, «одиниця» — це відпускання
 * лінії на зовнішню підтяжку. */
void plat_i2c_pins_take(void);    /* AF → GPIO open-drain */
void plat_i2c_pins_release(void); /* GPIO → AF, назад під периферію */
void plat_i2c_scl_write(bool high);
void plat_i2c_sda_write(bool high);
bool plat_i2c_scl_read(void);
bool plat_i2c_sda_read(void);

/* --- сторожовий таймер і скидання ---------------------------------------- */

void plat_watchdog_start(uint32_t timeout_ms);
void plat_watchdog_kick(void);
void plat_system_reset(void);

#endif /* PLATFORM_H */
