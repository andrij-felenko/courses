#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>

#define SMBUS_ARA_ADDR      0x0C    /* 7-бітна адреса Alert Response Address */
#define CRC8_POLYNOMIAL     0x07    /* Твірний поліном PEC: x^8 + x^2 + x + 1 */

/* Апаратне обчислення байта PEC (CRC-8) за алгоритмом LFSR */
static uint8_t smbus_crc8_byte(uint8_t crc, uint8_t data) {
    crc ^= data;
    for (int bit = 0; bit < 8; ++bit) {
        if (crc & 0x80) {
            crc = (uint8_t)((crc << 1) ^ CRC8_POLYNOMIAL);
        } else {
            crc = (uint8_t)(crc << 1);
        }
    }
    return crc;
}

/* Обчислення контрольної суми PEC для довільного масиву байтів */
static uint8_t smbus_calc_pec(const uint8_t *bytes, size_t len) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < len; ++i) {
        crc = smbus_crc8_byte(crc, bytes[i]);
    }
    return crc;
}

/* Зчитування адреси ініціатора переривання через ARA */
static int smbus_read_ara(int i2c_fd, uint8_t *alerting_slave_addr) {
    uint8_t addr_byte = 0;
    struct i2c_msg msgs[1];
    struct i2c_rdwr_ioctl_data rdwr;

    msgs[0].addr = SMBUS_ARA_ADDR;
    msgs[0].flags = I2C_M_RD;       /* Операція зчитування */
    msgs[0].len = 1;
    msgs[0].buf = &addr_byte;

    rdwr.msgs = msgs;
    rdwr.nmsgs = 1;

    if (ioctl(i2c_fd, I2C_RDWR, &rdwr) < 0) {
        return -1;
    }

    /* 7-бітна адреса веденого повертається у бітах 7:1 */
    *alerting_slave_addr = (uint8_t)(addr_byte >> 1);
    return 0;
}

/* Обробник повної черги подій на лінії SMBALERT# */
void smbus_service_alerts(int i2c_fd) {
    uint8_t slave_addr = 0;
    int processed_count = 0;

    /* Вичитуємо адреси доти, доки ведені відповідають ACK */
    while (smbus_read_ara(i2c_fd, &slave_addr) == 0) {
        processed_count++;
        printf("[SMBALERT] Сповіщення від веденого пристрою: 0x%02X\n", slave_addr);

        /* Диспетчеризація аварійних повідомлень */
        switch (slave_addr) {
            case 0x16:
                printf(" -> Оброблено тривогу Smart Battery: перевірка напруги комірок\n");
                break;
            case 0x24:
                printf(" -> Оброблено тривогу PMBus VRM: перевищення струму фази\n");
                break;
            case 0x48:
                printf(" -> Оброблено тривогу термодавача LM75: критичний перегрів!\n");
                break;
            default:
                printf(" -> Загальне сповіщення периферійного вузла 0x%02X\n", slave_addr);
                break;
        }

        /* Захист від зациклення при апаратному замиканні лінії на землю */
        if (processed_count > 32) {
            fprintf(stderr, "[УВАГА] Перевищено ліміт подій ARA: можливе замикання лінії SMBALERT#!\n");
            break;
        }
    }
}
