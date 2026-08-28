/* ========================================================================= */
/* Драйвер SPI Flash W25Q128 на C99 над абстракціями hal_spi_bus / gpio_pin */
/* ========================================================================= */

#define W25Q_CMD_WRITE_ENABLE    0x06
#define W25Q_CMD_WRITE_DISABLE   0x04
#define W25Q_CMD_READ_STATUS_1   0x05
#define W25Q_CMD_READ_DATA       0x03
#define W25Q_CMD_PAGE_PROGRAM    0x02
#define W25Q_CMD_SECTOR_ERASE    0x20
#define W25Q_CMD_JEDEC_ID        0x9F

#define W25Q_STATUS_BUSY_MASK    0x01
#define W25Q_PAGE_SIZE           256

typedef struct {
    const hal_spi_bus_t *spi;
    const hal_gpio_pin_t *cs_pin;
} w25q_driver_t;

static inline void w25q_cs_assert(const w25q_driver_t *dev) {
    hal_gpio_set(dev->cs_pin, HAL_GPIO_LEVEL_LOW);
}

static inline void w25q_cs_deassert(const w25q_driver_t *dev) {
    hal_gpio_set(dev->cs_pin, HAL_GPIO_LEVEL_HIGH);
}

hal_status_t w25q_init(w25q_driver_t *dev, const hal_spi_bus_t *spi, const hal_gpio_pin_t *cs) {
    if (!dev || !spi || !cs) return HAL_STATUS_INVALID_ARG;
    dev->spi = spi;
    dev->cs_pin = cs;

    /* Деактивація CS під час старту */
    w25q_cs_deassert(dev);

    /* Зчитування JEDEC ID: Winbond Manufacturer ID = 0xEF */
    uint8_t cmd = W25Q_CMD_JEDEC_ID;
    uint8_t id[3] = {0};

    w25q_cs_assert(dev);
    hal_status_t s = hal_spi_write(dev->spi, &cmd, 1, 100);
    if (s == HAL_STATUS_OK) {
        s = hal_spi_read(dev->spi, id, 3, 100);
    }
    w25q_cs_deassert(dev);

    if (s != HAL_STATUS_OK) return s;
    if (id[0] != 0xEF) return HAL_STATUS_ERROR; /* Некоректний виробник */

    return HAL_STATUS_OK;
}

static hal_status_t w25q_wait_busy(const w25q_driver_t *dev, uint32_t timeout_ms) {
    uint8_t cmd = W25Q_CMD_READ_STATUS_1;
    uint8_t status = 0;

    for (uint32_t i = 0; i < timeout_ms; ++i) {
        w25q_cs_assert(dev);
        hal_spi_write(dev->spi, &cmd, 1, 10);
        hal_spi_read(dev->spi, &status, 1, 10);
        w25q_cs_deassert(dev);

        if (!(status & W25Q_STATUS_BUSY_MASK)) {
            return HAL_STATUS_OK;
        }
    }
    return HAL_STATUS_TIMEOUT;
}

hal_status_t w25q_read(const w25q_driver_t *dev, uint32_t addr, uint8_t *buf, size_t len) {
    if (!dev || !buf || len == 0) return HAL_STATUS_INVALID_ARG;

    hal_status_t s = w25q_wait_busy(dev, 1000);
    if (s != HAL_STATUS_OK) return s;

    uint8_t cmd_buf[4] = {
        W25Q_CMD_READ_DATA,
        (uint8_t)((addr >> 16) & 0xFF),
        (uint8_t)((addr >> 8) & 0xFF),
        (uint8_t)(addr & 0xFF)
    };

    w25q_cs_assert(dev);
    s = hal_spi_write(dev->spi, cmd_buf, 4, 100);
    if (s == HAL_STATUS_OK) {
        s = hal_spi_read(dev->spi, buf, len, 1000);
    }
    w25q_cs_deassert(dev);

    return s;
}

hal_status_t w25q_write_page(const w25q_driver_t *dev, uint32_t addr, const uint8_t *data, size_t len) {
    if (!dev || !data || len == 0 || len > W25Q_PAGE_SIZE) return HAL_STATUS_INVALID_ARG;

    /* 1. Дозвіл запису (Write Enable) */
    uint8_t cmd_we = W25Q_CMD_WRITE_ENABLE;
    w25q_cs_assert(dev);
    hal_status_t s = hal_spi_write(dev->spi, &cmd_we, 1, 100);
    w25q_cs_deassert(dev);
    if (s != HAL_STATUS_OK) return s;

    /* 2. Команда програмування сторінки + 24-бітний адрес */
    uint8_t cmd_buf[4] = {
        W25Q_CMD_PAGE_PROGRAM,
        (uint8_t)((addr >> 16) & 0xFF),
        (uint8_t)((addr >> 8) & 0xFF),
        (uint8_t)(addr & 0xFF)
    };

    w25q_cs_assert(dev);
    s = hal_spi_write(dev->spi, cmd_buf, 4, 100);
    if (s == HAL_STATUS_OK) {
        s = hal_spi_write(dev->spi, data, len, 500);
    }
    w25q_cs_deassert(dev);
    if (s != HAL_STATUS_OK) return s;

    /* 3. Очікування завершення запису флеш-матриці */
    return w25q_wait_busy(dev, 100);
}
