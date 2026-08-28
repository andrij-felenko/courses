#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ATECC_I2C_ADDR           0x60
#define ATECC_CMD_WORD_ADDR      0x03
#define ATECC_SLEEP_WORD_ADDR    0x01
#define ATECC_OP_SIGN            0x41
#define ATECC_SIGN_MODE_EXTERNAL 0x80
#define ATECC_EXEC_TIME_SIGN_MS  115

typedef struct {
    bool (*i2c_write)(uint8_t addr, const uint8_t *data, uint16_t len);
    bool (*i2c_read)(uint8_t addr, uint8_t *data, uint16_t len);
    void (*wake_pulse)(void);
    void (*delay_ms)(uint32_t ms);
} atecc_hal_t;

typedef enum {
    ATECC_OK = 0,
    ATECC_ERR_HAL,
    ATECC_ERR_CRC,
    ATECC_ERR_STATUS,
    ATECC_ERR_TIMEOUT
} atecc_status_t;

static uint16_t atecc_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0x0000;
    for (size_t i = 0; i < length; i++) {
        for (uint8_t shift = 0x01; shift > 0x00; shift <<= 1) {
            uint8_t data_bit = (data[i] & shift) ? 1 : 0;
            uint8_t crc_bit = (crc >> 15) & 0x01;
            crc <<= 1;
            if (data_bit ^ crc_bit) {
                crc ^= 0x8005;
            }
        }
    }
    return crc;
}

atecc_status_t atecc_wake(const atecc_hal_t *hal) {
    hal->wake_pulse();
    hal->delay_ms(2); // Очікування готовності (t_WHI)

    uint8_t resp[4] = {0};
    if (!hal->i2c_read(ATECC_I2C_ADDR, resp, 4)) {
        return ATECC_ERR_HAL;
    }
    if (resp[0] != 0x04 || resp[1] != 0x11) {
        return ATECC_ERR_STATUS;
    }
    return ATECC_OK;
}

void atecc_sleep(const atecc_hal_t *hal) {
    uint8_t sleep_cmd = ATECC_SLEEP_WORD_ADDR;
    hal->i2c_write(ATECC_I2C_ADDR, &sleep_cmd, 1);
}

atecc_status_t atecc_sign_digest(const atecc_hal_t *hal, uint8_t slot_id,
                                const uint8_t digest[32], uint8_t signature[64]) {
    uint8_t tx_buf[40]; // 1(WordAddr) + 1(Count) + 1(Op) + 1(P1) + 2(P2) + 32(Data) + 2(CRC)
    uint8_t count = 39;

    tx_buf[0] = ATECC_CMD_WORD_ADDR;
    tx_buf[1] = count;
    tx_buf[2] = ATECC_OP_SIGN;
    tx_buf[3] = ATECC_SIGN_MODE_EXTERNAL;
    tx_buf[4] = (uint8_t)(slot_id & 0x0F);
    tx_buf[5] = 0x00;
    memcpy(&tx_buf[6], digest, 32);

    uint16_t crc = atecc_crc16(&tx_buf[1], count - 2);
    tx_buf[38] = (uint8_t)(crc & 0xFF);
    tx_buf[39] = (uint8_t)((crc >> 8) & 0xFF);

    if (!hal->i2c_write(ATECC_I2C_ADDR, tx_buf, 40)) {
        return ATECC_ERR_HAL;
    }

    hal->delay_ms(ATECC_EXEC_TIME_SIGN_MS);

    // Відповідь: 1 байт Count (67) + 64 байти (R, S) + 2 байти CRC
    uint8_t rx_buf[67];
    if (!hal->i2c_read(ATECC_I2C_ADDR, rx_buf, sizeof(rx_buf))) {
        return ATECC_ERR_HAL;
    }

    if (rx_buf[0] != 67) {
        return ATECC_ERR_STATUS;
    }

    uint16_t expected_crc = (uint16_t)(rx_buf[65] | (rx_buf[66] << 8));
    uint16_t calc_crc = atecc_crc16(rx_buf, 65);
    if (expected_crc != calc_crc) {
        return ATECC_ERR_CRC;
    }

    memcpy(signature, &rx_buf[1], 64);
    return ATECC_OK;
}
