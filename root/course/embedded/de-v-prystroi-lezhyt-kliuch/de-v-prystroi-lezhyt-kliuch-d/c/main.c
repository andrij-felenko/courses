#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ATECC_ADDR        0x60
#define CMD_WORD_ADDR     0x03
#define SLEEP_WORD_ADDR   0x01
#define OP_SIGN           0x41
#define SIGN_MODE_EXT     0x80

typedef struct {
    bool (*i2c_tx)(uint8_t addr, const uint8_t *buf, uint16_t len);
    bool (*i2c_rx)(uint8_t addr, uint8_t *buf, uint16_t len);
    void (*wake_pin_low)(void);
    void (*delay_ms)(uint32_t ms);
} crypto_hal_t;

// Розрахунок CRC16-CCITT зі зворотним бітовим порядком (поліном 0x8005)
static uint16_t calc_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0x0000;
    for (size_t i = 0; i < len; i++) {
        for (uint8_t bit = 0x01; bit > 0; bit <<= 1) {
            uint8_t data_bit = (data[i] & bit) ? 1 : 0;
            uint8_t crc_bit = (crc >> 15) & 0x01;
            crc <<= 1;
            if (data_bit ^ crc_bit) {
                crc ^= 0x8005;
            }
        }
    }
    return crc;
}

// Виконання цифрового підпису дайджесту приватним ключем зі слота
bool crypto_element_sign(const crypto_hal_t *hal, uint8_t slot,
                         const uint8_t digest[32], uint8_t signature[64]) {
    // 1. Пробудження чипа
    hal->wake_pin_low();
    hal->delay_ms(2);

    uint8_t wake_status[4] = {0};
    if (!hal->i2c_rx(ATECC_ADDR, wake_status, 4) || wake_status[1] != 0x11) {
        return false;
    }

    // 2. Формування пакета команди Sign
    uint8_t tx[40];
    tx[0] = CMD_WORD_ADDR;
    tx[1] = 39; // Count (Count + Op + P1 + P2(2B) + Data(32B) + CRC(2B))
    tx[2] = OP_SIGN;
    tx[3] = SIGN_MODE_EXT;
    tx[4] = (uint8_t)(slot & 0x0F);
    tx[5] = 0x00;
    memcpy(&tx[6], digest, 32);

    uint16_t crc = calc_crc16(&tx[1], 37);
    tx[38] = (uint8_t)(crc & 0xFF);
    tx[39] = (uint8_t)((crc >> 8) & 0xFF);

    if (!hal->i2c_tx(ATECC_ADDR, tx, sizeof(tx))) {
        return false;
    }

    // 3. Очікування виконання розрахунку еліптичної кривої
    hal->delay_ms(110);

    // 4. Зчитування 67-байтової відповіді: Count(1B) + R(32B) + S(32B) + CRC(2B)
    uint8_t rx[67] = {0};
    if (!hal->i2c_rx(ATECC_ADDR, rx, sizeof(rx)) || rx[0] != 67) {
        return false;
    }

    uint16_t rx_crc = (uint16_t)(rx[65] | (rx[66] << 8));
    if (calc_crc16(rx, 65) != rx_crc) {
        return false;
    }

    memcpy(signature, &rx[1], 64);

    // 5. Переведення чипа в режим сну
    uint8_t sleep_cmd = SLEEP_WORD_ADDR;
    hal->i2c_tx(ATECC_ADDR, &sleep_cmd, 1);

    return true;
}
