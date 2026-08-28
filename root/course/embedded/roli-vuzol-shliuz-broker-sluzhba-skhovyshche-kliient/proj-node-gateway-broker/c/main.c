#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define FRAME_MAGIC_TELEMETRY 0xAA
#define FRAME_TYPE_TELEMETRY  0x01
#define FRAME_TYPE_COMMAND    0x02
#define FRAME_TYPE_ACK        0x03

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;
    uint8_t  type;
    uint16_t node_id;
    uint32_t seq_num;
    int16_t  temperature_c_celsius; // x100 (2235 = 22.35 C)
    uint16_t battery_mv;
    uint8_t  flags;
    uint8_t  reserved;
    uint16_t crc16;
} telemetry_frame_t;

typedef struct {
    uint8_t  magic;
    uint8_t  type;
    uint16_t node_id;
    uint32_t seq_num;
    uint8_t  command_id;
    uint8_t  payload_val;
    uint16_t crc16;
} command_frame_t;
#pragma pack(pop)

/* Табличне або пряме обчислення CRC-16-CCITT (Poly: 0x1021, Init: 0xFFFF) */
uint16_t crc16_ccitt(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

void node_build_telemetry(telemetry_frame_t *frame, uint16_t node_id, uint32_t seq, int16_t temp_c, uint16_t bat_mv, uint8_t flags) {
    frame->magic = FRAME_MAGIC_TELEMETRY;
    frame->type = FRAME_TYPE_TELEMETRY;
    frame->node_id = node_id;
    frame->seq_num = seq;
    frame->temperature_c_celsius = temp_c;
    frame->battery_mv = bat_mv;
    frame->flags = flags;
    frame->reserved = 0x00;
    
    // Рахуємо CRC для всіх полів, крім самого поля crc16
    size_t data_len = sizeof(telemetry_frame_t) - sizeof(uint16_t);
    frame->crc16 = crc16_ccitt((const uint8_t *)frame, data_len);
}

bool node_process_command(const command_frame_t *cmd, uint16_t my_node_id, bool *relay_state) {
    if (cmd->magic != FRAME_MAGIC_TELEMETRY || cmd->type != FRAME_TYPE_COMMAND) {
        return false;
    }
    if (cmd->node_id != my_node_id) {
        return false;
    }
    size_t data_len = sizeof(command_frame_t) - sizeof(uint16_t);
    uint16_t expected_crc = crc16_ccitt((const uint8_t *)cmd, data_len);
    if (cmd->crc16 != expected_crc) {
        return false;
    }
    
    if (cmd->command_id == 0x10) { // Команда: встановити стан реле
        *relay_state = (cmd->payload_val != 0);
        return true;
    }
    return false;
}
