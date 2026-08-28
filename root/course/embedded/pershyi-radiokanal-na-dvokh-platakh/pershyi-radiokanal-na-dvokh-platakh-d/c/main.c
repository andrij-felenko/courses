#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Адреси регістрів nRF24L01+ */
#define REG_CONFIG      0x00
#define REG_EN_AA       0x01
#define REG_EN_RXADDR   0x02
#define REG_SETUP_AW    0x03
#define REG_SETUP_RETR  0x04
#define REG_RF_CH       0x05
#define REG_RF_SETUP    0x06
#define REG_STATUS      0x07
#define REG_OBSERVE_TX  0x08
#define REG_RX_ADDR_P0  0x0A
#define REG_TX_ADDR     0x10
#define REG_FIFO_STATUS 0x17
#define REG_DYNPD       0x1C
#define REG_FEATURE     0x1D

/* Біти статусних прапорців */
#define STATUS_RX_DR    (1 << 6)
#define STATUS_TX_DS    (1 << 5)
#define STATUS_MAX_RT   (1 << 4)

/* Команди SPI */
#define CMD_R_REGISTER    0x00
#define CMD_W_REGISTER    0x20
#define CMD_R_RX_PAYLOAD  0x61
#define CMD_W_TX_PAYLOAD  0xA0
#define CMD_FLUSH_TX      0xE1
#define CMD_FLUSH_RX      0xE2
#define CMD_R_RX_PL_WID   0x60

/* Апаратний інтерфейс викликів платформи */
typedef struct {
    void (*spi_transfer)(const uint8_t *tx, uint8_t *rx, uint16_t len);
    void (*set_csn)(bool level);
    void (*set_ce)(bool level);
    void (*delay_us)(uint32_t us);
} nrf_hal_t;

typedef struct {
    nrf_hal_t hal;
    uint8_t channel;
} nrf24_t;

/* Читання одиночного регістру */
static uint8_t nrf_read_reg(nrf24_t *dev, uint8_t reg) {
    uint8_t tx[2] = { (uint8_t)(CMD_R_REGISTER | (reg & 0x1F)), 0xFF };
    uint8_t rx[2] = { 0 };
    dev->hal.set_csn(false);
    dev->hal.spi_transfer(tx, rx, 2);
    dev->hal.set_csn(true);
    return rx[1];
}

/* Запис одиночного регістру */
static void nrf_write_reg(nrf24_t *dev, uint8_t reg, uint8_t val) {
    uint8_t tx[2] = { (uint8_t)(CMD_W_REGISTER | (reg & 0x1F)), val };
    uint8_t rx[2] = { 0 };
    dev->hal.set_csn(false);
    dev->hal.spi_transfer(tx, rx, 2);
    dev->hal.set_csn(true);
}

/* Запис багатобайтового буфера (адреси тощо) */
static void nrf_write_buf(nrf24_t *dev, uint8_t reg, const uint8_t *buf, uint8_t len) {
    uint8_t cmd = (uint8_t)(CMD_W_REGISTER | (reg & 0x1F));
    dev->hal.set_csn(false);
    dev->hal.spi_transfer(&cmd, NULL, 1);
    dev->hal.spi_transfer(buf, NULL, len);
    dev->hal.set_csn(true);
}

/* Ініціалізація радіотракту */
void nrf24_init(nrf24_t *dev, uint8_t channel) {
    dev->channel = channel;
    dev->hal.set_ce(false);
    dev->hal.set_csn(true);
    dev->hal.delay_us(5000);

    /* 5-байтова адресація */
    nrf_write_reg(dev, REG_SETUP_AW, 0x03);

    /* ARD = 1500 мкс (0x50), ARC = 10 спроб (0x0A) */
    nrf_write_reg(dev, REG_SETUP_RETR, 0x5A);

    /* Встановлення частотного каналу */
    nrf_write_reg(dev, REG_RF_CH, dev->channel);

    /* Швидкість 2 Мбіт/с (RF_DR_HIGH=1), потужність 0 dBm (RF_PWR=11) */
    nrf_write_reg(dev, REG_RF_SETUP, 0x0E);

    /* Увімкнення Dynamic Payload (DPL) та Auto-ACK */
    nrf_write_reg(dev, REG_FEATURE, 0x04);   /* EN_DPL = 1 */
    nrf_write_reg(dev, REG_DYNPD, 0x01);     /* DPL для Pipe 0 */
    nrf_write_reg(dev, REG_EN_AA, 0x01);     /* Auto-ACK для Pipe 0 */
    nrf_write_reg(dev, REG_EN_RXADDR, 0x01); /* Дозвіл Pipe 0 */

    /* Скидання статусу та очищення черг */
    nrf_write_reg(dev, REG_STATUS, 0x70);
    
    uint8_t flush_tx = CMD_FLUSH_TX;
    dev->hal.set_csn(false);
    dev->hal.spi_transfer(&flush_tx, NULL, 1);
    dev->hal.set_csn(true);

    uint8_t flush_rx = CMD_FLUSH_RX;
    dev->hal.set_csn(false);
    dev->hal.spi_transfer(&flush_rx, NULL, 1);
    dev->hal.set_csn(true);

    /* Увімкнення живлення Power Up, 2 байти CRC */
    nrf_write_reg(dev, REG_CONFIG, 0x0C);
    dev->hal.delay_us(1500);
}

/* Налаштування на передачу та відправка пакета */
bool nrf24_send_packet(nrf24_t *dev, const uint8_t *addr5, const uint8_t *data, uint8_t len) {
    /* Для роботи Auto-ACK адреса RX Pipe 0 має збігатися з TX_ADDR */
    nrf_write_buf(dev, REG_TX_ADDR, addr5, 5);
    nrf_write_buf(dev, REG_RX_ADDR_P0, addr5, 5);

    /* Перехід у режим TX (PRIM_RX = 0, PWR_UP = 1) */
    nrf_write_reg(dev, REG_CONFIG, 0x0E);

    /* Запис корисного навантаження */
    uint8_t cmd = CMD_W_TX_PAYLOAD;
    dev->hal.set_csn(false);
    dev->hal.spi_transfer(&cmd, NULL, 1);
    dev->hal.spi_transfer(data, NULL, len);
    dev->hal.set_csn(true);

    /* Короткий імпульс на ніжку CE для старту передачі */
    dev->hal.set_ce(true);
    dev->hal.delay_us(15);
    dev->hal.set_ce(false);

    /* Очікування результату (по перериванню або опитуванню STATUS) */
    while (1) {
        uint8_t status = nrf_read_reg(dev, REG_STATUS);
        if (status & STATUS_TX_DS) {
            nrf_write_reg(dev, REG_STATUS, STATUS_TX_DS); /* Скидання прапорця */
            return true; /* Пакет успішно доставлено і підтверджено */
        }
        if (status & STATUS_MAX_RT) {
            nrf_write_reg(dev, REG_STATUS, STATUS_MAX_RT);
            uint8_t flush = CMD_FLUSH_TX;
            dev->hal.set_csn(false);
            dev->hal.spi_transfer(&flush, NULL, 1);
            dev->hal.set_csn(true);
            return false; /* Перевищено ліміт повторів */
        }
        dev->hal.delay_us(50);
    }
}

/* Налаштування приймача на безперервне прослуховування */
void nrf24_start_listening(nrf24_t *dev, const uint8_t *addr5) {
    nrf_write_buf(dev, REG_RX_ADDR_P0, addr5, 5);
    nrf_write_reg(dev, REG_CONFIG, 0x0F); /* PRIM_RX = 1, PWR_UP = 1 */
    dev->hal.set_ce(true);
    dev->hal.delay_us(130);
}

/* Обробка надходження кадру в приймачі */
bool nrf24_read_packet(nrf24_t *dev, uint8_t *data, uint8_t *out_len, uint8_t max_len) {
    uint8_t status = nrf_read_reg(dev, REG_STATUS);
    if (!(status & STATUS_RX_DR)) {
        return false;
    }

    /* Запит динамічної довжини прийнятого пакета */
    uint8_t cmd_len = CMD_R_RX_PL_WID;
    uint8_t rx_len_buf[2] = { 0 };
    uint8_t tx_len_buf[2] = { cmd_len, 0xFF };
    dev->hal.set_csn(false);
    dev->hal.spi_transfer(tx_len_buf, rx_len_buf, 2);
    dev->hal.set_csn(true);

    uint8_t payload_len = rx_len_buf[1];
    if (payload_len > 32) {
        /* Спотворений розмір: скидаємо буфер */
        uint8_t flush = CMD_FLUSH_RX;
        dev->hal.set_csn(false);
        dev->hal.spi_transfer(&flush, NULL, 1);
        dev->hal.set_csn(true);
        nrf_write_reg(dev, REG_STATUS, STATUS_RX_DR);
        return false;
    }

    /* Вичитування даних */
    uint8_t cmd_read = CMD_R_RX_PAYLOAD;
    dev->hal.set_csn(false);
    dev->hal.spi_transfer(&cmd_read, NULL, 1);
    dev->hal.spi_transfer(NULL, data, payload_len > max_len ? max_len : payload_len);
    dev->hal.set_csn(true);

    *out_len = payload_len;
    nrf_write_reg(dev, REG_STATUS, STATUS_RX_DR); /* Очищення прапорця */
    return true;
}
