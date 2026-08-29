/* Прошивка для стендового випробування: раз на дві секунди знімає відлік
   і виводить його в UART. Прив'язка драйвера до заліза — три короткі
   функції внизу файла, більше драйвер про платформу нічого не знає.

   HAL_* надає бібліотека STM32Cube; hi2c1, huart2 та функції MX_*_Init
   лежать у коді, згенерованому CubeMX. */

#include "stm32f4xx_hal.h"

#include <stdio.h>
#include <string.h>

#include "sht3x.h"

extern I2C_HandleTypeDef hi2c1;
extern UART_HandleTypeDef huart2;

void SystemClock_Config(void);
void MX_GPIO_Init(void);
void MX_I2C1_Init(void);
void MX_USART2_UART_Init(void);

#define I2C_TIMEOUT_MS 100u
#define POLL_PERIOD_MS 2000u

/* --- Прив'язка до заліза ------------------------------------------------ */

static bool hal_i2c_write(uint8_t addr7, const uint8_t *data, size_t len, void *ctx)
{
    /* HAL чекає 8-бітну адресу, тобто вже зсунуту ліворуч: 0x44 -> 0x88. */
    return HAL_I2C_Master_Transmit((I2C_HandleTypeDef *)ctx,
                                   (uint16_t)(addr7 << 1),
                                   (uint8_t *)data,
                                   (uint16_t)len,
                                   I2C_TIMEOUT_MS) == HAL_OK;
}

static bool hal_i2c_read(uint8_t addr7, uint8_t *data, size_t len, void *ctx)
{
    return HAL_I2C_Master_Receive((I2C_HandleTypeDef *)ctx,
                                  (uint16_t)(addr7 << 1),
                                  data,
                                  (uint16_t)len,
                                  I2C_TIMEOUT_MS) == HAL_OK;
}

static void hal_delay(uint32_t ms, void *ctx)
{
    (void)ctx;
    HAL_Delay(ms);
}

/* --- Вивід -------------------------------------------------------------- */

static void uart_print(const char *text)
{
    HAL_UART_Transmit(&huart2, (uint8_t *)text, (uint16_t)strlen(text), I2C_TIMEOUT_MS);
}

static void print_measurement(const char *tag, const sht3x_meas_t *m)
{
    char line[80];

    /* Друкуємо цілочисельні величини вручну: printf("%f") на дрібному МК
       тягне за собою кілька кілобайтів емуляції float. */
    const int32_t  t      = m->temperature_mc;
    const int32_t  t_int  = t / 1000;
    const int32_t  t_frac = (t < 0 ? -t : t) % 1000;
    const char    *sign   = (t < 0 && t_int == 0) ? "-" : "";

    int n = snprintf(line, sizeof line,
                     "%s T = %s%ld.%03ld C   RH = %lu.%02lu %%\r\n",
                     tag, sign, (long)t_int, (long)t_frac,
                     (unsigned long)(m->humidity_cpm / 100u),
                     (unsigned long)(m->humidity_cpm % 100u));
    if (n > 0) {
        uart_print(line);
    }
}

/* --- Діагностика нагрівачем --------------------------------------------- */

/* Вмикаємо нагрівач на дві секунди: справний сенсор мусить показати
   помітний підйом температури й падіння вологості. Нема реакції —
   мембрана забруднена або чип механічно пошкоджено. */
static void heater_selftest(sht3x_t *dev)
{
    sht3x_meas_t cold, hot;

    if (sht3x_measure_retry(dev, SHT3X_REP_HIGH, &cold, 3u) != SHT3X_OK) {
        uart_print("samoperevirka: bazovyi vidlik ne znialy\r\n");
        return;
    }
    if (sht3x_heater(dev, true) != SHT3X_OK) {
        uart_print("samoperevirka: nahrivach ne uvimknuvsia\r\n");
        return;
    }

    HAL_Delay(2000u);
    sht3x_status_t st = sht3x_measure_retry(dev, SHT3X_REP_HIGH, &hot, 3u);

    /* Нагрівач гасимо в будь-якому разі, навіть якщо читання провалилось. */
    (void)sht3x_heater(dev, false);

    if (st != SHT3X_OK) {
        uart_print("samoperevirka: vidlik pid nahrivom ne znialy\r\n");
        return;
    }

    print_measurement("holodnyi:", &cold);
    print_measurement("nahritnyi:", &hot);

    const int32_t dt  = hot.temperature_mc - cold.temperature_mc;
    const int32_t drh = (int32_t)cold.humidity_cpm - (int32_t)hot.humidity_cpm;

    if (dt > 1000 && drh > 300) {
        uart_print("samoperevirka: OK\r\n");
    } else {
        uart_print("samoperevirka: PROVAL, membrana zabrudnena?\r\n");
    }
}

/* --- Точка входу -------------------------------------------------------- */

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_I2C1_Init();
    MX_USART2_UART_Init();

    sht3x_t sensor = {
        .i2c_write = hal_i2c_write,
        .i2c_read  = hal_i2c_read,
        .delay_ms  = hal_delay,
        .ctx       = &hi2c1,
        .addr7     = SHT3X_ADDR_GND,
    };

    uart_print("\r\nSHT3x: start\r\n");

    sht3x_status_t st = sht3x_init(&sensor);
    if (st != SHT3X_OK) {
        char line[64];
        snprintf(line, sizeof line, "sensor nedostupnyi: %s\r\n", sht3x_strerror(st));
        uart_print(line);
        /* Далі йти нема куди: без давача прошивка не має що вимірювати. */
        for (;;) {
            HAL_Delay(1000u);
        }
    }

    heater_selftest(&sensor);

    for (;;) {
        sht3x_meas_t m;
        st = sht3x_measure_retry(&sensor, SHT3X_REP_HIGH, &m, 3u);

        if (st == SHT3X_OK) {
            print_measurement("vidlik:", &m);
        } else {
            char line[80];
            snprintf(line, sizeof line, "zbii: %s (shyna %lu, CRC %lu)\r\n",
                     sht3x_strerror(st),
                     (unsigned long)sensor.bus_errors,
                     (unsigned long)sensor.crc_errors);
            uart_print(line);
        }

        /* Дві секунди паузи — не лінощі, а боротьба із самопідігрівом:
           при безперервному опитуванні кристал грітиметься на 1..1.8 °C
           і вологість піде вниз на 5..6 %RH. */
        HAL_Delay(POLL_PERIOD_MS);
    }
}
