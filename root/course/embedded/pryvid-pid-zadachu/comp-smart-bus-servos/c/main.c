#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define SERVO_HEADER        0xFF
#define INST_WRITE_DATA     0x03
#define REG_GOAL_POSITION   0x2A

typedef struct {
    uint8_t buffer[16];
    size_t length;
} ServoPacket;

ServoPacket build_position_packet(uint8_t id, uint16_t position_raw, uint16_t speed_raw) {
    ServoPacket pkt;
    pkt.buffer[0] = SERVO_HEADER;
    pkt.buffer[1] = SERVO_HEADER;
    pkt.buffer[2] = id;
    pkt.buffer[3] = 7; // Length = Instruction(1) + Reg(1) + Data(4) + Checksum(1)
    pkt.buffer[4] = INST_WRITE_DATA;
    pkt.buffer[5] = REG_GOAL_POSITION;
    pkt.buffer[6] = (uint8_t)(position_raw & 0xFF);
    pkt.buffer[7] = (uint8_t)((position_raw >> 8) & 0xFF);
    pkt.buffer[8] = (uint8_t)(speed_raw & 0xFF);
    pkt.buffer[9] = (uint8_t)((speed_raw >> 8) & 0xFF);

    uint32_t sum = 0;
    for (size_t i = 2; i <= 9; i++) {
        sum += pkt.buffer[i];
    }
    pkt.buffer[10] = (uint8_t)(~sum & 0xFF);
    pkt.length = 11;
    return pkt;
}
