#include <stdint.h>
#include <stdbool.h>

// Формування CAN ID для сервісних команд (MIT Protocol)
static uint32_t make_mit_can_id(uint8_t mode, uint8_t target_id, uint8_t master_id) {
    return (((uint32_t)mode & 0x1F) << 24) | (((uint32_t)target_id & 0xFF) << 8) | ((uint32_t)master_id & 0xFF);
}

// Перевірка прапорців помилок у байті статусу
bool check_servo_faults(uint8_t status_byte) {
    // Біти 0..3 вказують на апаратну аварію
    return (status_byte & 0x0F) != 0;
}

// Формування кадру скидання аварій (Clear Faults)
void build_clear_faults_frame(uint32_t* out_can_id, uint8_t payload[8], uint8_t target_id, uint8_t master_id) {
    *out_can_id = make_mit_can_id(0x04, target_id, master_id);
    for (int i = 0; i < 8; i++) {
        payload[i] = 0x00;
    }
}

// Формування кадру установки нуля (Set Zero Position)
void build_set_zero_frame(uint32_t* out_can_id, uint8_t payload[8], uint8_t target_id, uint8_t master_id) {
    *out_can_id = make_mit_can_id(0x03, target_id, master_id);
    for (int i = 0; i < 8; i++) {
        payload[i] = 0x00;
    }
}
