/* Польотний контролер на STM32H743: три шини, вісім чипів, жодного очікування
 * в головному циклі.
 *
 *   SPI1 — ICM-42688P (IMU), режим 3, ~20 МГц, опитування 1 кГц від TIM6.
 *          Контролер відданий давачеві повністю: інші обміни не зсунуть вибірку.
 *   SPI2 — MB85RS64 (FRAM журналу, режим 0) і ADS1118 (АЦП, режим 1).
 *          Різні CPOL/CPHA на одній шині — диспетчер перемикає їх перед CS.
 *   I2C1 — BMP280 (0x76), LIS3MDL (0x1E), INA226 (0x40), 24C64 (0x50) на 400 кГц.
 */
#include "bus.h"

#include <string.h>

/* Дескриптори периферії та функції ініціалізації — зі згенерованого CubeMX коду. */
extern SPI_HandleTypeDef hspi1;
extern SPI_HandleTypeDef hspi2;
extern I2C_HandleTypeDef hi2c1;
extern TIM_HandleTypeDef htim6;

void SystemClock_Config(void);
void MX_GPIO_Init(void);
void MX_DMA_Init(void);
void MX_SPI1_Init(void);
void MX_SPI2_Init(void);
void MX_I2C1_Init(void);
void MX_TIM6_Init(void);

/* ---- карта пристроїв ------------------------------------------------------- */

static const bus_device_t dev_imu = {
    .cs_port = GPIOA, .cs_pin = GPIO_PIN_4,
    .spi_polarity = SPI_POLARITY_HIGH, .spi_phase = SPI_PHASE_2EDGE,  /* режим 3 */
    .spi_prescaler = SPI_BAUDRATEPRESCALER_8
};

static const bus_device_t dev_fram = {
    .cs_port = GPIOB, .cs_pin = GPIO_PIN_12,
    .spi_polarity = SPI_POLARITY_LOW, .spi_phase = SPI_PHASE_1EDGE,   /* режим 0 */
    .spi_prescaler = SPI_BAUDRATEPRESCALER_4
};

static const bus_device_t dev_adc = {
    .cs_port = GPIOB, .cs_pin = GPIO_PIN_1,
    .spi_polarity = SPI_POLARITY_LOW, .spi_phase = SPI_PHASE_2EDGE,   /* режим 1 */
    .spi_prescaler = SPI_BAUDRATEPRESCALER_32
};

static const bus_device_t dev_baro   = { .i2c_addr = 0x76 };
static const bus_device_t dev_mag    = { .i2c_addr = 0x1E };
static const bus_device_t dev_power  = { .i2c_addr = 0x40 };
static const bus_device_t dev_eeprom = { .i2c_addr = 0x50 };

static bus_t bus_spi1;
static bus_t bus_spi2;
static bus_t bus_i2c1;

/* ---- буфери DMA ------------------------------------------------------------
 * Вирівняні на рядок кешу й лежать у секції, яку лінкер кладе в SRAM, доступну
 * контролерам DMA (домен D2). Кеш узгоджує сам диспетчер. */
#define DMA_BUF __attribute__((section(".dma_buffer"), aligned(32)))

static DMA_BUF uint8_t imu_raw[14];
static DMA_BUF uint8_t baro_raw[6];
static DMA_BUF uint8_t mag_raw[6];
static DMA_BUF uint8_t power_raw[2];
static DMA_BUF uint8_t adc_tx[2];
static DMA_BUF uint8_t adc_rx[2];
static DMA_BUF uint8_t eeprom_raw[32];
static DMA_BUF uint8_t log_record[16];

/* ---- стан, який наповнюють колбеки ----------------------------------------- */

typedef struct {
    volatile bool fresh;
    volatile uint32_t missed;   /* вибірок, які не встигли забрати з черги */
    int16_t accel[3];
    int16_t gyro[3];
    int16_t temperature;
} imu_state_t;

static imu_state_t imu;

static volatile bool     baro_fresh;
static volatile bool     mag_fresh;
static volatile uint16_t bus_voltage_raw;
static volatile int16_t  ext_adc_raw;
static volatile uint32_t i2c_failures;

static int16_t be16(const uint8_t *p)
{
    return (int16_t)(((uint16_t)p[0] << 8) | p[1]);
}

/* ---- колбеки завершення (контекст переривання) ------------------------------ */

static void on_imu_done(bus_result_t result, void *ctx)
{
    (void)ctx;
    if (result != BUS_OK) {
        imu.missed++;
        return;
    }
    if (imu.fresh) {
        imu.missed++;   /* головний цикл не забрав попередню — рахуємо чесно */
    }
    imu.temperature = be16(&imu_raw[0]);
    for (uint32_t i = 0u; i < 3u; ++i) {
        imu.accel[i] = be16(&imu_raw[2 + 2 * i]);
        imu.gyro[i]  = be16(&imu_raw[8 + 2 * i]);
    }
    imu.fresh = true;
}

static void on_baro_done(bus_result_t result, void *ctx)
{
    (void)ctx;
    if (result == BUS_OK) {
        baro_fresh = true;
    } else {
        i2c_failures++;
    }
}

static void on_mag_done(bus_result_t result, void *ctx)
{
    (void)ctx;
    if (result == BUS_OK) {
        mag_fresh = true;
    } else {
        i2c_failures++;
    }
}

static void on_power_done(bus_result_t result, void *ctx)
{
    (void)ctx;
    if (result == BUS_OK) {
        bus_voltage_raw = (uint16_t)(((uint16_t)power_raw[0] << 8) | power_raw[1]);
    } else {
        i2c_failures++;
    }
}

static void on_adc_done(bus_result_t result, void *ctx)
{
    (void)ctx;
    if (result == BUS_OK) {
        ext_adc_raw = be16(adc_rx);
    }
}

static void on_log_done(bus_result_t result, void *ctx)
{
    (void)result;
    (void)ctx;   /* запис у FRAM або пройшов, або загубився — політ це не спиняє */
}

/* ---- планування транзакцій ------------------------------------------------- */

/* IMU опитуємо з переривання таймера: 1 кГц треба тримати рівно, а головний
 * цикл гуляє за часом залежно від того, що саме він щойно порахував. */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance != TIM6) {
        return;
    }

    bus_txn_t txn = {
        .dev = &dev_imu,
        .op  = BUS_OP_READ,
        .cmd = { 0x1Du | 0x80u },   /* TEMP_DATA1, старший біт — ознака читання */
        .cmd_len = 1u,
        .rx  = imu_raw,
        .len = sizeof imu_raw,
        .timeout_ms = 2u,
        .done = on_imu_done
    };
    if (!bus_submit(&bus_spi1, &txn)) {
        imu.missed++;
    }
}

static void request_baro(void)
{
    bus_txn_t txn = {
        .dev = &dev_baro, .op = BUS_OP_READ,
        .cmd = { 0xF7u }, .cmd_len = 1u,      /* press_msb, далі 5 байтів поспіль */
        .rx = baro_raw, .len = sizeof baro_raw,
        .done = on_baro_done
    };
    (void)bus_submit(&bus_i2c1, &txn);
}

static void request_mag(void)
{
    bus_txn_t txn = {
        .dev = &dev_mag, .op = BUS_OP_READ,
        .cmd = { 0x28u | 0x80u }, .cmd_len = 1u,  /* OUT_X_L з автоінкрементом */
        .rx = mag_raw, .len = sizeof mag_raw,
        .done = on_mag_done
    };
    (void)bus_submit(&bus_i2c1, &txn);
}

static void request_power(void)
{
    bus_txn_t txn = {
        .dev = &dev_power, .op = BUS_OP_READ,
        .cmd = { 0x02u }, .cmd_len = 1u,      /* Bus Voltage Register */
        .rx = power_raw, .len = sizeof power_raw,
        .done = on_power_done
    };
    (void)bus_submit(&bus_i2c1, &txn);
}

static void request_ext_adc(void)
{
    /* ADS1118 повнодуплексний: у той самий момент, коли ми віддаємо нову
     * конфігурацію, чип зсуває результат попереднього перетворення. */
    adc_tx[0] = 0x85u;   /* SS=1, AIN0-GND, ±4.096 В */
    adc_tx[1] = 0x8Bu;   /* 128 SPS, одиночне перетворення, DOUT з підтяжкою */

    bus_txn_t txn = {
        .dev = &dev_adc, .op = BUS_OP_TRANSFER,
        .tx = adc_tx, .rx = adc_rx, .len = sizeof adc_tx,
        .done = on_adc_done
    };
    (void)bus_submit(&bus_spi2, &txn);
}

/* Журнал у FRAM: спершу дозвіл запису окремою командою без даних, далі сам
 * запис за 16-бітною адресою. Дві транзакції поспіль у черзі однієї шини
 * підуть саме в цьому порядку — між ними CS підніметься, як і вимагає чип. */
static void append_log_record(uint16_t slot)
{
    uint32_t now = HAL_GetTick();
    uint16_t addr = (uint16_t)(slot * sizeof log_record);

    memcpy(&log_record[0], &now, sizeof now);
    memcpy(&log_record[4], baro_raw, 6u);
    log_record[10] = (uint8_t)(bus_voltage_raw >> 8);
    log_record[11] = (uint8_t)bus_voltage_raw;
    memcpy(&log_record[12], &imu.gyro[2], sizeof(int16_t));
    log_record[14] = (uint8_t)(imu.missed >> 8);
    log_record[15] = (uint8_t)imu.missed;

    bus_txn_t write_enable = {
        .dev = &dev_fram, .op = BUS_OP_WRITE,
        .cmd = { 0x06u }, .cmd_len = 1u,   /* WREN, даних немає */
        .len = 0u
    };
    bus_txn_t write_data = {
        .dev = &dev_fram, .op = BUS_OP_WRITE,
        .cmd = { 0x02u, (uint8_t)(addr >> 8), (uint8_t)addr }, .cmd_len = 3u,
        .tx = log_record, .len = sizeof log_record,
        .done = on_log_done
    };

    if (bus_submit(&bus_spi2, &write_enable)) {
        (void)bus_submit(&bus_spi2, &write_data);
    }
}

static void load_calibration(void)
{
    bus_txn_t txn = {
        .dev = &dev_eeprom, .op = BUS_OP_READ,
        .cmd = { 0x00u, 0x00u }, .cmd_len = 2u,   /* 24C64 має 16-бітну адресу */
        .rx = eeprom_raw, .len = sizeof eeprom_raw,
        .timeout_ms = 20u,
        .done = NULL
    };
    (void)bus_submit(&bus_i2c1, &txn);
}

/* ---- головний цикл --------------------------------------------------------- */

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_DMA_Init();
    MX_SPI1_Init();
    MX_SPI2_Init();
    MX_I2C1_Init();
    MX_TIM6_Init();

    const i2c_lines_t i2c1_lines = {
        .scl_port = GPIOB, .scl_pin = GPIO_PIN_8,
        .sda_port = GPIOB, .sda_pin = GPIO_PIN_9,
        .alternate = GPIO_AF4_I2C1
    };

    bus_init_spi(&bus_spi1, &hspi1);
    bus_init_spi(&bus_spi2, &hspi2);
    bus_init_i2c(&bus_i2c1, &hi2c1, &i2c1_lines);

    /* Ведений міг лишитися завислим ще від попереднього польоту: перше, що
     * робимо на I2C, — знімаємо з нього можливий замок. */
    (void)i2c_bus_recover(&hi2c1, &i2c1_lines);

    /* CS усіх чипів тримаємо у високому стані з першої ж мілісекунди. */
    HAL_GPIO_WritePin(dev_imu.cs_port,  dev_imu.cs_pin,  GPIO_PIN_SET);
    HAL_GPIO_WritePin(dev_fram.cs_port, dev_fram.cs_pin, GPIO_PIN_SET);
    HAL_GPIO_WritePin(dev_adc.cs_port,  dev_adc.cs_pin,  GPIO_PIN_SET);

    load_calibration();
    HAL_TIM_Base_Start_IT(&htim6);   /* 1 кГц: опитування IMU */

    uint32_t next_baro  = HAL_GetTick();
    uint32_t next_mag   = next_baro;
    uint32_t next_power = next_baro;
    uint32_t next_adc   = next_baro;
    uint32_t next_log   = next_baro;
    uint16_t log_slot   = 0u;

    for (;;) {
        uint32_t now = HAL_GetTick();

        if ((int32_t)(now - next_baro) >= 0) {
            next_baro += 20u;          /* 50 Гц */
            request_baro();
        }
        if ((int32_t)(now - next_mag) >= 0) {
            next_mag += 10u;           /* 100 Гц */
            request_mag();
        }
        if ((int32_t)(now - next_power) >= 0) {
            next_power += 100u;        /* 10 Гц */
            request_power();
        }
        if ((int32_t)(now - next_adc) >= 0) {
            next_adc += 100u;
            request_ext_adc();
        }
        if ((int32_t)(now - next_log) >= 0) {
            next_log += 200u;          /* 5 Гц */
            append_log_record(log_slot);
            log_slot = (uint16_t)((log_slot + 1u) % 512u);
        }

        if (imu.fresh) {
            imu.fresh = false;
            /* Тут працює контур стабілізації: свіжий вектор уже в imu.accel/gyro,
             * і жоден виклик шини його не затримав. */
        }
        if (baro_fresh) {
            baro_fresh = false;
        }
        if (mag_fresh) {
            mag_fresh = false;
        }

        /* Нагляд за таймаутами й відкладене лікування I2C. */
        bus_poll(&bus_spi1);
        bus_poll(&bus_spi2);
        bus_poll(&bus_i2c1);
    }
}
