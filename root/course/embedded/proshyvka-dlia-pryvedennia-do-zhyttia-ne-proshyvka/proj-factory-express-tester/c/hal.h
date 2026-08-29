#ifndef FCT_HAL_H
#define FCT_HAL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Контракт нижнього рівня заводського тестера: усе, чого тестовий рушій
 * вимагає від плати-виробу й від стенда. Реалізація живе в BSP конкретного
 * виробу, сам рушій про неї нічого не знає. Жодна функція тут не блокує
 * назавжди: усе, що може не відповісти, дістає таймаут аргументом. */

/* --- Час, затримки, сторожовий таймер ---------------------------------- */

/* Монотонний лічильник мікросекунд. Читається ПРЯМО з регістра апаратного
 * таймера (крок 100 мкс), а не з лічильника переривань: під час March C-
 * переривання замасковані, і лічильник на перериваннях завмер би разом
 * з усіма таймаутами, які на нього спираються. Обгортка 32 біти. */
uint32_t hal_time_us(void);
void     hal_delay_us(uint32_t us);
void     hal_watchdog_kick(void);

/* --- Переривання -------------------------------------------------------- */

uint32_t hal_irq_disable(void);            /* повертає попередній PRIMASK */
void     hal_irq_restore(uint32_t primask);

/* --- АЦП ---------------------------------------------------------------- */

enum {
    HAL_ADC_CH_VREFINT = 0,  /* внутрішнє джерело опорної напруги */
    HAL_ADC_CH_VCORE   = 1   /* V_CORE через дільник 1:2 на технологічному купоні */
};

/* true — перетворення завершилося за timeout_us, raw заповнено (12 біт). */
bool     hal_adc_read(uint8_t channel, uint16_t *raw, uint32_t timeout_us);
/* Фабричне калібрувальне значення VREFINT (12 біт), зняте при 3.000 В. */
uint16_t hal_vrefint_cal(void);

/* --- Тактування --------------------------------------------------------- */

void     hal_clock_pll_start(void);        /* запускає PLL і одразу повертається */
bool     hal_clock_pll_locked(void);
/* Частота HSE, виміряна лічильником проти опорного 32768 Гц за вікно
 * gate_ms. Повертає 0, якщо кварц не збудився й вікно порожнє. */
uint32_t hal_clock_measure_hse_hz(uint32_t gate_ms);

/* --- I2C: піни в GPIO для розблокування і назад у периферію ------------- */

void     hal_i2c_pins_to_gpio(void);
void     hal_i2c_pins_to_peripheral(void);
void     hal_i2c_scl_write(bool level);
void     hal_i2c_sda_write(bool level);
bool     hal_i2c_sda_read(void);
void     hal_i2c_reinit(void);
/* Читання регістра веденого. false — NACK або таймаут шини. */
bool     hal_i2c_read_reg(uint8_t addr7, uint8_t reg, uint8_t *value,
                          uint32_t timeout_us);

/* --- SPI ---------------------------------------------------------------- */

void     hal_spi_cs(bool active);
bool     hal_spi_xfer(const uint8_t *tx, uint8_t *rx, size_t len,
                      uint32_t timeout_us);

/* --- Радіотракт --------------------------------------------------------- */

bool     hal_radio_init(void);
/* Неперервна несуча: частота в кГц, потужність у десятих частках dBm. */
bool     hal_radio_cw_start(uint32_t freq_khz, int16_t power_ddbm);
void     hal_radio_cw_stop(void);
uint8_t  hal_radio_xo_trim(void);           /* поточний код ємнісного масиву */
void     hal_radio_xo_trim_set(uint8_t trim); /* 0..HAL_XO_TRIM_MAX */
#define  HAL_XO_TRIM_MAX 63

/* --- OTP / eFuse -------------------------------------------------------- */

#define  HAL_OTP_WORD_XO_TRIM 4
bool     hal_otp_read(uint8_t word_index, uint32_t *value);
/* Пропалювання перемички: імпульс до 200 мА. Напругу перед викликом
 * перевіряє тестер, апаратура сама її не сторожує. */
bool     hal_otp_write(uint8_t word_index, uint32_t value);

/* --- Канал до стенда ---------------------------------------------------- */

typedef struct {
    uint16_t inrush_peak_ma;      /* піковий струм ввімкнення */
    uint16_t inrush_duration_us;  /* скільки він тривав */
    uint16_t iq_ua;               /* струм спокою при утриманому RESET */
} hal_stand_power_t;

typedef struct {
    int16_t power_ddbm;    /* виміряна потужність, десяті dBm */
    int32_t freq_error_hz; /* відхилення піку від замовленої частоти */
} hal_stand_rf_t;

/* Журнал фази 0: стенд зняв ці числа ще до відпускання RESET. */
bool hal_stand_read_power_log(hal_stand_power_t *log, uint32_t timeout_us);
/* Запит до вимірювача потужності стенда, поки несуча в ефірі. */
bool hal_stand_measure_rf(uint32_t freq_khz, hal_stand_rf_t *out,
                          uint32_t timeout_us);

void hal_uart_write(const char *data, size_t len);
void hal_result_indicate(bool pass);   /* дві лампи на голчастому ложі */
void hal_board_init(void);

#endif /* FCT_HAL_H */
