#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FRAME_PREAMBLE 0x55AA

// Бінарна структура кадру пульта налагодження
typedef struct __attribute__((packed)) {
    uint16_t preamble;        // Маркер 0x55AA
    uint8_t  frame_type;      // Тип кадру
    uint8_t  sequence_id;     // Лічильник кадрів
    uint16_t payload_len;     // Довжина даних
    uint16_t safety_status;   // Регістр 0x0001
    uint16_t keypad_mask;     // Регістр 0x0002
    int16_t  joystick_axes[6];// Регістри 0x0003..0x0008
    uint16_t crc16;           // Контрольна сума
} TeachPendantFrame_t;

// Пакування кадру телеметрії перед відправкою
void pack_pendant_telemetry(TeachPendantFrame_t *frame, uint8_t seq, uint16_t safety, uint16_t keys, const int16_t joy[6]) {
    frame->preamble = FRAME_PREAMBLE;
    frame->frame_type = 0x01;
    frame->sequence_id = seq;
    frame->payload_len = 16; // 2 + 2 + 6*2 = 16 байтів
    frame->safety_status = safety;
    frame->keypad_mask = keys;
    memcpy(frame->joystick_axes, joy, sizeof(frame->joystick_axes));
    
    // Обчислення CRC по всіх полях крім самого CRC16
    size_t crc_len = sizeof(TeachPendantFrame_t) - sizeof(uint16_t);
    frame->crc16 = calculate_crc16_modbus((const uint8_t*)frame, crc_len);
}
