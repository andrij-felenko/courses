#include <stdint.h>

// командні байти nRF24 (даташит, розділ команд SPI)
#define R_REGISTER    0x00      // прочитати регістр: 0x00 | reg
#define W_REGISTER    0x20      // записати регістр:  0x20 | reg

// номери регістрів, що знадобляться далі
#define CONFIG        0x00
#define EN_AA         0x01      // авто-ACK по пайпах
#define EN_RXADDR     0x02      // які приймальні пайпи ввімкнені
#define SETUP_AW      0x03      // довжина адреси (3/4/5 байтів)
#define SETUP_RETR    0x04      // ARD (затримка) + ARC (к-сть повторів)
#define STATUS        0x07      // прапорці подій; повертається на кожен 1-й байт
#define OBSERVE_TX    0x08      // лічильники втрат і повторів
#define DYNPD         0x1C      // динамічний payload по пайпах
#define FEATURE       0x1D      // EN_DPL / EN_ACK_PAY / EN_DYN_ACK

// spi_xfer(b) — послати байт b, повернути прийнятий (апаратна ф-я платформи)
// csn_low()/csn_high() — опустити/підняти лінію CSN

// записати один байт value в регістр reg; повертає STATUS (перший прийнятий байт)
uint8_t nrf_write_reg(uint8_t reg, uint8_t value) {
    csn_low();
    uint8_t status = spi_xfer(W_REGISTER | reg);   // 1-й байт → назад іде STATUS
    spi_xfer(value);                                // 2-й байт → сам запис
    csn_high();
    return status;
}

// прочитати один байт регістра reg
uint8_t nrf_read_reg(uint8_t reg) {
    csn_low();
    spi_xfer(R_REGISTER | reg);                     // команда (STATUS нам тут не треба)
    uint8_t value = spi_xfer(0xFF);                 // женемо «сміття» 0xFF, щоб виштовхати дані
    csn_high();
    return value;
}
