#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Опкоди строб-команд керування
#define CMD_SRES         0x30
#define CMD_SFSTXON      0x31
#define CMD_SXOFF        0x32
#define CMD_SCAL         0x33
#define CMD_SRX          0x34
#define CMD_STX          0x35
#define CMD_SIDLE        0x36
#define CMD_SFRX         0x3A
#define CMD_SFTX         0x3B
#define CMD_SNOP         0x3D

// Адреси ключових регістрів
#define REG_IOCFG0       0x00
#define REG_PKTLEN       0x06
#define REG_PKTCTRL0     0x08
#define REG_FREQ2        0x0D
#define REG_FREQ1        0x0E
#define REG_FREQ0        0x0F
#define REG_MDMCFG2      0x12
#define REG_RSSI         0x34
#define REG_RXBYTES      0x3B
#define REG_FIFO         0x3F

#define SPI_READ_SINGLE  0x80
#define SPI_READ_BURST   0xC0
#define SPI_WRITE_BURST  0x40

// Апаратно-залежний інтерфейс (HAL)
extern void radio_spi_cs_low(void);
extern void radio_spi_cs_high(void);
extern uint8_t radio_spi_transfer(uint8_t data);
extern void radio_delay_us(uint32_t us);
extern bool radio_get_irq_pin(void);

// Запис одного байта в регістр
void radio_write_reg(uint8_t addr, uint8_t value) {
    radio_spi_cs_low();
    radio_spi_transfer(addr & 0x3F);
    radio_spi_transfer(value);
    radio_spi_cs_high();
}

// Читання одного байта з регістра
uint8_t radio_read_reg(uint8_t addr) {
    radio_spi_cs_low();
    radio_spi_transfer(addr | SPI_READ_SINGLE);
    uint8_t val = radio_spi_transfer(0x00);
    radio_spi_cs_high();
    return val;
}

// Відправка строб-команди
uint8_t radio_strobe(uint8_t cmd) {
    radio_spi_cs_low();
    uint8_t status = radio_spi_transfer(cmd);
    radio_spi_cs_high();
    return status;
}

// Повна ініціалізація радіомодуля (868 МГц, GFSK, CRC ON, Data Whitening ON)
void radio_init(void) {
    radio_spi_cs_high();
    radio_delay_us(100);

    // Скидання чипа
    radio_strobe(CMD_SRES);
    radio_delay_us(200);

    // Налаштування виводу переривання GDO0 (активний рівень при прийомі валідного пакета)
    radio_write_reg(REG_IOCFG0, 0x06);

    // Конфігурація пакета: змінна довжина (Variable length), CRC ON, Whitening ON
    radio_write_reg(REG_PKTCTRL0, 0x45);
    radio_write_reg(REG_PKTLEN, 64); // Максимальна довжина пакета 64 байти

    // Модуляція: GFSK, виявлення 16-бітного синхрослова (0xD391)
    radio_write_reg(REG_MDMCFG2, 0x12);

    // Несуча частота: 868.000 МГц (для опорного кварцу 26 МГц)
    radio_write_reg(REG_FREQ2, 0x21);
    radio_write_reg(REG_FREQ1, 0x62);
    radio_write_reg(REG_FREQ0, 0x76);

    // Переведення в стан очікування
    radio_strobe(CMD_SIDLE);
}

// Відправка пакета даних
bool radio_send_packet(const uint8_t *payload, uint8_t length) {
    if (length == 0 || length > 63) return false;

    // Перехід в IDLE та очищення TX FIFO
    radio_strobe(CMD_SIDLE);
    radio_strobe(CMD_SFTX);

    // Запис пакета у FIFO через Burst Write
    radio_spi_cs_low();
    radio_spi_transfer(REG_FIFO | SPI_WRITE_BURST);
    radio_spi_transfer(length); // Байт довжини
    for (uint8_t i = 0; i < length; i++) {
        radio_spi_transfer(payload[i]);
    }
    radio_spi_cs_high();

    // Запуск передавача
    radio_strobe(CMD_STX);

    // Очікування підйому лінії IRQ (початок відправки) та спаду (завершення TX_DONE)
    uint32_t timeout = 50000;
    while (!radio_get_irq_pin() && --timeout) radio_delay_us(10);
    while (radio_get_irq_pin() && --timeout) radio_delay_us(10);

    radio_strobe(CMD_SIDLE);
    return (timeout > 0);
}

// Прийом пакета (перевірка наявності даних та читання)
bool radio_receive_packet(uint8_t *buffer, uint8_t *length, int8_t *rssi_dbm) {
    uint8_t rx_bytes = radio_read_reg(REG_RXBYTES);

    // Перевірка переповнення FIFO
    if (rx_bytes & 0x80) {
        radio_strobe(CMD_SIDLE);
        radio_strobe(CMD_SFRX);
        radio_strobe(CMD_SRX);
        return false;
    }

    if ((rx_bytes & 0x7F) == 0) {
        return false;
    }

    // Читання довжини та вмісту FIFO
    radio_spi_cs_low();
    radio_spi_transfer(REG_FIFO | SPI_READ_BURST);
    uint8_t pkt_len = radio_spi_transfer(0x00);

    if (pkt_len > 63) {
        radio_spi_cs_high();
        radio_strobe(CMD_SFRX);
        return false;
    }

    for (uint8_t i = 0; i < pkt_len; i++) {
        buffer[i] = radio_spi_transfer(0x00);
    }

    // Читання додаткових статусних байтів (RSSI та LQI/CRC_OK)
    uint8_t raw_rssi = radio_spi_transfer(0x00);
    uint8_t lqi_crc  = radio_spi_transfer(0x00);
    radio_spi_cs_high();

    // Перевірка апаратного біта CRC OK (біт 7 у LQI)
    if (!(lqi_crc & 0x80)) {
        return false;
    }

    *length = pkt_len;

    // Перерахунок RSSI у dBm
    if (raw_rssi >= 128) {
        *rssi_dbm = (int8_t)((raw_rssi - 256) / 2) - 74;
    } else {
        *rssi_dbm = (int8_t)(raw_rssi / 2) - 74;
    }

    return true;
}
