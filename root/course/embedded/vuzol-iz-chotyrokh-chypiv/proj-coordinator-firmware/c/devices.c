#include "stm32l4xx.h"
#include "node.h"
#include "i2c.h"
#include "devices.h"

/* ══ BME280 ═══════════════════════════════════════════════════════════════ */

#define BME280_ADDR      0x76u
#define BME280_REG_ID    0xD0u
#define BME280_REG_RESET 0xE0u
#define BME280_REG_CTRL_HUM  0xF2u
#define BME280_REG_STATUS    0xF3u
#define BME280_REG_CTRL_MEAS 0xF4u
#define BME280_REG_CONFIG    0xF5u
#define BME280_REG_DATA      0xF7u

static struct {
    uint16_t T1; int16_t T2, T3;
    uint16_t P1; int16_t P2, P3, P4, P5, P6, P7, P8, P9;
    uint8_t  H1; int16_t H2; uint8_t H3; int16_t H4, H5; int8_t H6;
    int32_t  t_fine;
    bool     ready;
} cal;

static bool bme280_read_calibration(void)
{
    uint8_t a[26];
    uint8_t b[7];

    if (i2c_read_regs(BME280_ADDR, 0x88u, a, sizeof(a)) != I2C_OK) return false;
    if (i2c_read_regs(BME280_ADDR, 0xE1u, b, sizeof(b)) != I2C_OK) return false;

    cal.T1 = (uint16_t)(a[0]  | (a[1]  << 8));
    cal.T2 = (int16_t) (a[2]  | (a[3]  << 8));
    cal.T3 = (int16_t) (a[4]  | (a[5]  << 8));
    cal.P1 = (uint16_t)(a[6]  | (a[7]  << 8));
    cal.P2 = (int16_t) (a[8]  | (a[9]  << 8));
    cal.P3 = (int16_t) (a[10] | (a[11] << 8));
    cal.P4 = (int16_t) (a[12] | (a[13] << 8));
    cal.P5 = (int16_t) (a[14] | (a[15] << 8));
    cal.P6 = (int16_t) (a[16] | (a[17] << 8));
    cal.P7 = (int16_t) (a[18] | (a[19] << 8));
    cal.P8 = (int16_t) (a[20] | (a[21] << 8));
    cal.P9 = (int16_t) (a[22] | (a[23] << 8));
    /* a[24] — резерв, a[25] = dig_H1 за адресою 0xA1 */
    cal.H1 = a[25];

    cal.H2 = (int16_t)(b[0] | (b[1] << 8));
    cal.H3 = b[2];
    /* H4 і H5 упаковані в півбайти навколо 0xE5 — класична пастка датчика */
    cal.H4 = (int16_t)(((int16_t)(int8_t)b[3] << 4) | (b[4] & 0x0Fu));
    cal.H5 = (int16_t)(((int16_t)(int8_t)b[5] << 4) | (b[4] >> 4));
    cal.H6 = (int8_t)b[6];

    cal.ready = true;
    return true;
}

bool bme280_init(void)
{
    uint8_t id = 0;

    cal.ready = false;

    if (i2c_read_regs(BME280_ADDR, BME280_REG_ID, &id, 1u) != I2C_OK) {
        /* Найімовірніша причина мовчання — зависла шина після скидання ядра. */
        i2c_bus_recover();
        if (i2c_read_regs(BME280_ADDR, BME280_REG_ID, &id, 1u) != I2C_OK) return false;
    }
    if (id != 0x60u) return false;

    if (i2c_write_reg(BME280_ADDR, BME280_REG_RESET, 0xB6u) != I2C_OK) return false;
    /* Внутрішнє копіювання NVM після скидання — 2 мс за паспортом. */
    uint32_t t0 = millis();
    while ((millis() - t0) < 3u) { }

    if (!bme280_read_calibration()) return false;

    /* Фільтр вимкнено, режим очікування нас не обходить: вимірюємо силоміць
     * раз на секунду, а між вимірами чип у сні. */
    if (i2c_write_reg(BME280_ADDR, BME280_REG_CTRL_HUM, 0x01u) != I2C_OK) return false;
    if (i2c_write_reg(BME280_ADDR, BME280_REG_CONFIG,   0x00u) != I2C_OK) return false;
    return true;
}

bool bme280_start(void)
{
    if (!cal.ready) return false;
    /* osrs_t=1, osrs_p=1, mode=forced */
    if (i2c_write_reg(BME280_ADDR, BME280_REG_CTRL_HUM, 0x01u) != I2C_OK) return false;
    return i2c_write_reg(BME280_ADDR, BME280_REG_CTRL_MEAS, 0x25u) == I2C_OK;
}

bool bme280_ready(void)
{
    uint8_t status = 0;

    if (i2c_read_regs(BME280_ADDR, BME280_REG_STATUS, &status, 1u) != I2C_OK) return false;
    return (status & 0x08u) == 0u;      /* measuring == 0 */
}

/* Компенсація за паспортом Bosch — цілочислова, без плаваючої крапки. */
static int32_t compensate_temperature(int32_t adc_T)
{
    int32_t v1 = ((((adc_T >> 3) - ((int32_t)cal.T1 << 1))) * (int32_t)cal.T2) >> 11;
    int32_t v2 = (((((adc_T >> 4) - (int32_t)cal.T1) *
                    ((adc_T >> 4) - (int32_t)cal.T1)) >> 12) * (int32_t)cal.T3) >> 14;

    cal.t_fine = v1 + v2;
    return (cal.t_fine * 5 + 128) >> 8;      /* °C × 100 */
}

static uint32_t compensate_pressure(int32_t adc_P)
{
    int64_t v1 = (int64_t)cal.t_fine - 128000;
    int64_t v2 = v1 * v1 * (int64_t)cal.P6;

    v2 += (v1 * (int64_t)cal.P5) << 17;
    v2 += ((int64_t)cal.P4) << 35;
    v1 = ((v1 * v1 * (int64_t)cal.P3) >> 8) + ((v1 * (int64_t)cal.P2) << 12);
    v1 = (((((int64_t)1) << 47) + v1)) * ((int64_t)cal.P1) >> 33;

    if (v1 == 0) return 0;                   /* ділення на нуль при битій калібровці */

    int64_t p = 1048576 - adc_P;
    p = (((p << 31) - v2) * 3125) / v1;
    v1 = (((int64_t)cal.P9) * (p >> 13) * (p >> 13)) >> 25;
    v2 = (((int64_t)cal.P8) * p) >> 19;
    p = ((p + v1 + v2) >> 8) + (((int64_t)cal.P7) << 4);   /* Па у форматі Q24.8 */

    if (p < 0) return 0;
    return (uint32_t)(((uint64_t)p * 100u) >> 8);          /* Па × 100 */
}

static uint32_t compensate_humidity(int32_t adc_H)
{
    int32_t v = cal.t_fine - 76800;

    v = ((((adc_H << 14) - (((int32_t)cal.H4) << 20) - (((int32_t)cal.H5) * v)) + 16384) >> 15) *
        (((((((v * ((int32_t)cal.H6)) >> 10) *
             (((v * ((int32_t)cal.H3)) >> 11) + 32768)) >> 10) + 2097152) *
             ((int32_t)cal.H2) + 8192) >> 14);
    v = v - (((((v >> 15) * (v >> 15)) >> 7) * ((int32_t)cal.H1) >> 4));

    if (v < 0) v = 0;
    if (v > 419430400) v = 419430400;
    return (uint32_t)(v >> 12);              /* %RH × 1024 */
}

bool bme280_fetch(int32_t *temp_c100, uint32_t *press_pa100, uint32_t *hum_rh1024)
{
    uint8_t d[8];

    if (!cal.ready) return false;
    if (i2c_read_regs(BME280_ADDR, BME280_REG_DATA, d, sizeof(d)) != I2C_OK) return false;

    int32_t adc_P = ((int32_t)d[0] << 12) | ((int32_t)d[1] << 4) | (d[2] >> 4);
    int32_t adc_T = ((int32_t)d[3] << 12) | ((int32_t)d[4] << 4) | (d[5] >> 4);
    int32_t adc_H = ((int32_t)d[6] << 8)  |  (int32_t)d[7];

    /* 0x80000 і 0x8000 — значення після скидання: вимірювання не відбулося
     * або АЦП пішов за межу. Такі відліки в журнал не пускаємо. */
    if (adc_T == 0x80000 || adc_P == 0x80000 || adc_H == 0x8000) return false;

    *temp_c100   = compensate_temperature(adc_T);   /* спершу T: дає t_fine */
    *press_pa100 = compensate_pressure(adc_P);
    *hum_rh1024  = compensate_humidity(adc_H);
    return *press_pa100 != 0u;
}

/* ══ DS3231 ═══════════════════════════════════════════════════════════════ */

#define DS3231_ADDR    0x68u
#define DS3231_REG_SEC 0x00u
#define DS3231_REG_CTL 0x0Eu
#define DS3231_REG_STS 0x0Fu

static uint8_t bcd_to_bin(uint8_t bcd)
{
    return (uint8_t)((bcd >> 4) * 10u + (bcd & 0x0Fu));
}

/* Дні від 1970-01-01 — алгоритм Говарда Гіннанта, без таблиць і циклів. */
static uint32_t days_from_civil(uint32_t y, uint32_t m, uint32_t d)
{
    y -= (m <= 2u);
    uint32_t era = y / 400u;
    uint32_t yoe = y - era * 400u;                                  /* 0..399 */
    uint32_t doy = (153u * (m + (m > 2u ? -3u : 9u)) + 2u) / 5u + d - 1u;
    uint32_t doe = yoe * 365u + yoe / 4u - yoe / 100u + doy;        /* 0..146096 */

    return era * 146097u + doe - 719468u;
}

bool ds3231_init(void)
{
    uint8_t ctl = 0;

    if (i2c_read_regs(DS3231_ADDR, DS3231_REG_CTL, &ctl, 1u) != I2C_OK) {
        i2c_bus_recover();
        if (i2c_read_regs(DS3231_ADDR, DS3231_REG_CTL, &ctl, 1u) != I2C_OK) return false;
    }

    /* INTCN=0 і RS2:RS1=00 → на виводі INT/SQW меандр 1 Гц. Саме цей фронт
     * будить ядро зі Stop 2 і породжує подію вимірювання: власний таймер
     * мікроконтролера тут не потрібен взагалі. */
    ctl &= (uint8_t)~0x1Cu;      /* скинути INTCN, RS2, RS1 */
    ctl &= (uint8_t)~0x80u;      /* EOSC=0 — генератор працює й від батареї */
    if (i2c_write_reg(DS3231_ADDR, DS3231_REG_CTL, ctl) != I2C_OK) return false;

    /* 32 кГц вихід нам не потрібен — зайві мікроампери з резервної батареї. */
    uint8_t sts = 0;
    if (i2c_read_regs(DS3231_ADDR, DS3231_REG_STS, &sts, 1u) != I2C_OK) return false;
    sts &= (uint8_t)~0x08u;
    return i2c_write_reg(DS3231_ADDR, DS3231_REG_STS, sts) == I2C_OK;
}

bool ds3231_time(uint32_t *unix_time, bool *clock_valid)
{
    uint8_t r[7];
    uint8_t sts = 0;

    if (i2c_read_regs(DS3231_ADDR, DS3231_REG_SEC, r, sizeof(r)) != I2C_OK) return false;
    if (i2c_read_regs(DS3231_ADDR, DS3231_REG_STS, &sts, 1u) != I2C_OK) return false;

    uint32_t sec  = bcd_to_bin(r[0] & 0x7Fu);
    uint32_t min  = bcd_to_bin(r[1] & 0x7Fu);
    uint32_t hour = bcd_to_bin(r[2] & 0x3Fu);       /* 24-годинний формат */
    uint32_t day  = bcd_to_bin(r[4] & 0x3Fu);
    uint32_t mon  = bcd_to_bin(r[5] & 0x1Fu);
    uint32_t year = 2000u + bcd_to_bin(r[6]) + ((r[5] & 0x80u) ? 100u : 0u);

    if (sec > 59u || min > 59u || hour > 23u || day == 0u || day > 31u ||
        mon == 0u || mon > 12u) {
        return false;                                /* BCD побито на шині */
    }

    *unix_time = days_from_civil(year, mon, day) * 86400u + hour * 3600u + min * 60u + sec;

    /* OSF: генератор колись зупинявся — час у чипі не має довіри. Прапорець
     * скидаємо, щоб наступний запис уже показував відновлену синхронність. */
    *clock_valid = (sts & 0x80u) == 0u;
    if (!*clock_valid) {
        i2c_write_reg(DS3231_ADDR, DS3231_REG_STS, (uint8_t)(sts & ~0x80u));
    }
    return true;
}

/* ══ W25Q128JV на SPI1 ════════════════════════════════════════════════════ */

#define CMD_WRITE_ENABLE 0x06u
#define CMD_READ_STATUS1 0x05u
#define CMD_READ_DATA    0x03u
#define CMD_PAGE_PROGRAM 0x02u
#define CMD_SECTOR_ERASE 0x20u
#define CMD_JEDEC_ID     0x9Fu

#define SR1_BUSY 0x01u
#define SR1_WEL  0x02u

static void cs_low(void)  { GPIOA->BSRR = (1u << (4u + 16u)); }
static void cs_high(void) { GPIOA->BSRR = (1u << 4u); }

static uint8_t spi_xfer(uint8_t out)
{
    while ((SPI1->SR & SPI_SR_TXE) == 0u) { }
    *(volatile uint8_t *)&SPI1->DR = out;               /* саме байтовий доступ */
    while ((SPI1->SR & SPI_SR_RXNE) == 0u) { }
    return *(volatile uint8_t *)&SPI1->DR;
}

void flash_init(void)
{
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;

    /* PA5/PA6/PA7 → AF5 (SPI1), PA4 → вихід CS, спокійний рівень високий. */
    GPIOA->AFR[0] = (GPIOA->AFR[0] & ~0xFFF00000u) | 0x55500000u;
    GPIOA->MODER  = (GPIOA->MODER & ~0x0000FF00u) | 0x0000A800u;  /* PA5..7 = AF */
    GPIOA->MODER  = (GPIOA->MODER & ~0x00000300u) | 0x00000100u;  /* PA4 = вихід */
    GPIOA->OSPEEDR |= 0x0000FF00u;                                 /* швидкі виводи */
    cs_high();

    /* Ведучий, режим 0, SYSCLK/8 = 10 МГц, програмний NSS, кадр 8 бітів. */
    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI | (2u << SPI_CR1_BR_Pos);
    SPI1->CR2 = SPI_CR2_FRXTH | (7u << SPI_CR2_DS_Pos);
    SPI1->CR1 |= SPI_CR1_SPE;
}

bool flash_present(void)
{
    uint8_t id[3];

    cs_low();
    spi_xfer(CMD_JEDEC_ID);
    id[0] = spi_xfer(0xFFu);
    id[1] = spi_xfer(0xFFu);
    id[2] = spi_xfer(0xFFu);
    cs_high();

    return id[0] == 0xEFu && id[1] == 0x40u && id[2] == 0x18u;
}

static uint8_t read_status1(void)
{
    cs_low();
    spi_xfer(CMD_READ_STATUS1);
    uint8_t sr = spi_xfer(0xFFu);
    cs_high();
    return sr;
}

bool flash_busy(void)
{
    return (read_status1() & SR1_BUSY) != 0u;
}

bool flash_last_op_ok(void)
{
    uint8_t sr = read_status1();
    /* Успішна команда сама знімає WEL. Якщо він досі стоїть, а BUSY немає —
     * чип команду відкинув (захист сектора, збій живлення посеред запису). */
    return (sr & (SR1_BUSY | SR1_WEL)) == 0u;
}

static void write_enable(void)
{
    cs_low();
    spi_xfer(CMD_WRITE_ENABLE);
    cs_high();
}

static void send_address(uint32_t addr)
{
    spi_xfer((uint8_t)(addr >> 16));
    spi_xfer((uint8_t)(addr >> 8));
    spi_xfer((uint8_t)addr);
}

bool flash_read(uint32_t addr, uint8_t *dst, uint32_t len)
{
    if (addr + len > FLASH_TOTAL_SIZE) return false;
    if (flash_busy()) return false;

    cs_low();
    spi_xfer(CMD_READ_DATA);
    send_address(addr);
    for (uint32_t i = 0; i < len; i++) {
        dst[i] = spi_xfer(0xFFu);
    }
    cs_high();
    return true;
}

bool flash_page_program_start(uint32_t addr, const uint8_t *src, uint16_t len)
{
    if (len == 0u || len > FLASH_PAGE_SIZE) return false;
    /* Сторінковий запис не переходить межу сторінки: чип загорне адресу
     * на початок тієї самої сторінки й тихо зіпсує дані. */
    if ((addr % FLASH_PAGE_SIZE) + len > FLASH_PAGE_SIZE) return false;
    if (addr + len > FLASH_TOTAL_SIZE) return false;
    if (flash_busy()) return false;

    write_enable();
    if ((read_status1() & SR1_WEL) == 0u) return false;   /* чип не прийняв WREN */

    cs_low();
    spi_xfer(CMD_PAGE_PROGRAM);
    send_address(addr);
    for (uint16_t i = 0; i < len; i++) {
        spi_xfer(src[i]);
    }
    cs_high();          /* саме підняття CS запускає програмування, ~0.7 мс */
    return true;
}

bool flash_sector_erase_start(uint32_t addr)
{
    if (addr % FLASH_SECTOR_SIZE != 0u) return false;
    if (addr >= FLASH_TOTAL_SIZE) return false;
    if (flash_busy()) return false;

    write_enable();
    if ((read_status1() & SR1_WEL) == 0u) return false;

    cs_low();
    spi_xfer(CMD_SECTOR_ERASE);
    send_address(addr);
    cs_high();          /* стирання 4 КБ: 45 мс типово, до 400 мс за паспортом */
    return true;
}
