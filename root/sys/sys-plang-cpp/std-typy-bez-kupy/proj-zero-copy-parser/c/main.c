#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#define RING_BUF_SIZE 256

typedef struct {
    uint8_t rx_buffer[RING_BUF_SIZE];
    size_t tail; // Позиція читача
} CTelemetryReceiver;

typedef struct {
    uint8_t msg_type;
    const uint8_t* payload;
    size_t payload_len;
    uint16_t crc;
} CParsedFrame;

static uint16_t crc16_c(const uint8_t* data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; ++j) {
            crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
        }
    }
    return crc;
}

bool receiver_try_parse_c(CTelemetryReceiver* rx, size_t head, CParsedFrame* out_frame) {
    if (!rx || !out_frame) return false;

    // Обчислення доступної кількості байтів
    size_t available = (head >= rx->tail) ? (head - rx->tail) : (RING_BUF_SIZE - rx->tail + head);
    if (available < 6) return false; // Мінімальний розмір кадру: 2 (преамбула) + 1 (тип) + 1 (довжина) + 0 + 2 (CRC)

    // Лінійний пошук преамбули
    while (available >= 6) {
        uint8_t b0 = rx->rx_buffer[rx->tail];
        uint8_t b1 = rx->rx_buffer[(rx->tail + 1) % RING_BUF_SIZE];

        if (b0 == 0xAA && b1 == 0x55) {
            uint8_t msg_type = rx->rx_buffer[(rx->tail + 2) % RING_BUF_SIZE];
            uint8_t payload_len = rx->rx_buffer[(rx->tail + 3) % RING_BUF_SIZE];
            size_t total_frame_len = 4 + payload_len + 2;

            if (available < total_frame_len) {
                return false; // Кадр ще не до кінця прийнятий DMA
            }

            // Якщо кадр перетинає кінець кільцевого буфера, необхідний проміжний буфер
            uint8_t linear_temp[128];
            for (size_t i = 0; i < total_frame_len; ++i) {
                linear_temp[i] = rx->rx_buffer[(rx->tail + i) % RING_BUF_SIZE];
            }

            uint16_t calculated_crc = crc16_c(linear_temp + 2, total_frame_len - 4);
            uint16_t received_crc = (uint16_t)(linear_temp[total_frame_len - 2] | (linear_temp[total_frame_len - 1] << 8));

            if (calculated_crc == received_crc) {
                out_frame->msg_type = msg_type;
                out_frame->payload = linear_temp + 4;
                out_frame->payload_len = payload_len;
                out_frame->crc = received_crc;

                rx->tail = (rx->tail + total_frame_len) % RING_BUF_SIZE;
                return true;
            }
        }
        rx->tail = (rx->tail + 1) % RING_BUF_SIZE;
        available--;
    }
    return false;
}
