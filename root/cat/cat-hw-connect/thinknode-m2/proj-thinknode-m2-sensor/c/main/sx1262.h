#pragma once

#include <stdint.h>
#include <stdbool.h>

#define SX1262_CMD_SET_STANDBY        0x80
#define SX1262_CMD_SET_PACKET_TYPE    0x8A
#define SX1262_CMD_SET_RF_FREQUENCY   0x86
#define SX1262_CMD_SET_BUFFER_BASE    0x8F
#define SX1262_CMD_WRITE_BUFFER       0x0E
#define SX1262_CMD_SET_TX             0x83

bool sx1262_init(void);
bool sx1262_transmit(const uint8_t *data, uint8_t len);
