#ifndef SX1280_H
#define SX1280_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Драйвер трансивера Semtech SX1280 у режимі FLRC. Опкоди й параметри —
// з таблиці команд даташита; жодних «зручних» надбудов тут немає.

#define SX1280_CMD_GET_STATUS         0xC0
#define SX1280_CMD_WRITE_REGISTER     0x18
#define SX1280_CMD_READ_REGISTER      0x19
#define SX1280_CMD_WRITE_BUFFER       0x1A
#define SX1280_CMD_READ_BUFFER        0x1B
#define SX1280_CMD_SET_STANDBY        0x80
#define SX1280_CMD_SET_RX             0x82
#define SX1280_CMD_SET_TX             0x83
#define SX1280_CMD_SET_SLEEP          0x84
#define SX1280_CMD_SET_RF_FREQUENCY   0x86
#define SX1280_CMD_SET_PACKET_TYPE    0x8A
#define SX1280_CMD_SET_MOD_PARAMS     0x8B
#define SX1280_CMD_SET_PACKET_PARAMS  0x8C
#define SX1280_CMD_SET_DIO_IRQ_PARAMS 0x8D
#define SX1280_CMD_SET_TX_PARAMS      0x8E
#define SX1280_CMD_SET_BUFFER_BASE    0x8F
#define SX1280_CMD_SET_REGULATOR_MODE 0x96
#define SX1280_CMD_CLR_IRQ_STATUS     0x97
#define SX1280_CMD_GET_IRQ_STATUS     0x15
#define SX1280_CMD_GET_RX_BUF_STATUS  0x17
#define SX1280_CMD_GET_PACKET_STATUS  0x1D

#define SX1280_STDBY_RC          0x00
#define SX1280_PACKET_TYPE_FLRC  0x03

// Швидкість 1.3 Мбіт/с у смузі 1.2 МГц, кодування 3/4, гаусів фільтр 0.5.
#define SX1280_FLRC_BR_1_300_BW_1_2 0x45
#define SX1280_FLRC_CR_3_4          0x02
#define SX1280_FLRC_BT_0_5          0x20

#define SX1280_PREAMBLE_32_BITS   0x70
#define SX1280_FLRC_SYNC_LEN_4B   0x04
#define SX1280_RX_MATCH_SYNC_1    0x10
#define SX1280_PACKET_FIXED_LEN   0x00
#define SX1280_CRC_OFF            0x00
#define SX1280_WHITENING_OFF      0x08
#define SX1280_RAMP_20_US         0xE0

#define SX1280_PERIOD_BASE_15US   0x00   // крок 15.625 мкс
#define SX1280_PERIOD_BASE_1MS    0x02

#define SX1280_IRQ_TX_DONE       0x0001
#define SX1280_IRQ_RX_DONE       0x0002
#define SX1280_IRQ_CRC_ERROR     0x0040
#define SX1280_IRQ_RX_TX_TIMEOUT 0x4000

// Синхрослово FLRC займає старші чотири байти поля SyncAddress1.
#define SX1280_REG_FLRC_SYNC_WORD1 0x09CF

#define SX1280_RF_HZ 2440000000u

void sx1280_reset(void);
bool sx1280_status(uint8_t *status);
bool sx1280_init(uint8_t payload_len);
bool sx1280_transmit(const uint8_t *payload, size_t len);
bool sx1280_listen(uint32_t window_us);
bool sx1280_wait_irq(uint16_t mask, uint32_t timeout_us, uint16_t *out_irq);
bool sx1280_irq_status(uint16_t *out);
bool sx1280_clear_irq(uint16_t mask);
size_t sx1280_read_packet(uint8_t *out, size_t max);
int8_t sx1280_last_rssi(void);
bool sx1280_standby(void);

#endif
