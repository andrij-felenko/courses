#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct {
    uint8_t buffer[64];
    size_t received_bytes;
} DmaReceiver;

bool process_packet_c(const uint8_t* data, size_t len) {
    if (data == NULL || len < 4) {
        return false;
    }
    uint8_t packet_id = data[0];
    const uint8_t* payload = data + 1;
    size_t payload_len = len - 3; // 1 байт ID + 2 байти CRC
    uint16_t expected_crc = (uint16_t)(data[len - 2] | (data[len - 1] << 8));

    // Обробка payload через вказівник і довжину...
    (void)packet_id;
    (void)payload;
    (void)payload_len;
    (void)expected_crc;
    return true;
}
