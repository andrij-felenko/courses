#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FLEXRAY_HEADER_SIZE       5
#define FLEXRAY_TRAILER_SIZE      3
#define FLEXRAY_MAX_PAYLOAD_WORDS  127
#define FLEXRAY_MAX_PAYLOAD_BYTES  (FLEXRAY_MAX_PAYLOAD_WORDS * 2)

/* Заголовок кадру FlexRay */
typedef struct {
    bool     payload_preamble;
    bool     null_frame;
    bool     sync_frame;
    bool     startup_frame;
    uint16_t frame_id;       /* 1 .. 2047 */
    uint16_t payload_length; /* Довжина у 16-біт словах (0 .. 127) */
    uint16_t header_crc;     /* 11-бітний CRC */
    uint8_t  cycle_count;    /* 0 .. 63 */
} flexray_header_t;

/* Повний кадр FlexRay */
typedef struct {
    flexray_header_t header;
    uint8_t          payload[FLEXRAY_MAX_PAYLOAD_BYTES];
    uint32_t         frame_crc; /* 24-бітний CRC */
} flexray_frame_t;

/* Обчислення 11-бітного Header CRC (Поліном 0x385, init 0x01A) */
uint16_t flexray_compute_header_crc(const flexray_header_t* hdr) {
    uint32_t crc = 0x01A;
    uint32_t poly = 0x385;
    
    /* Формування 20-бітного вектора: [Sync(1) | Startup(1) | FrameID(11) | Length(7)] */
    uint32_t data_word = 0;
    data_word |= ((uint32_t)hdr->sync_frame & 0x01) << 19;
    data_word |= ((uint32_t)hdr->startup_frame & 0x01) << 18;
    data_word |= ((uint32_t)hdr->frame_id & 0x7FF) << 7;
    data_word |= ((uint32_t)hdr->payload_length & 0x7F);

    for (int i = 19; i >= 0; i--) {
        uint32_t bit = (data_word >> i) & 0x01;
        uint32_t crc_msb = (crc >> 10) & 0x01;
        crc = (crc << 1) & 0x7FF;
        if (bit ^ crc_msb) {
            crc ^= poly;
        }
    }
    return (uint16_t)(crc & 0x7FF);
}

/* Обчислення 24-бітного Frame CRC (Поліном 0x5B2EC7, init 0xFEDCBA) */
uint32_t flexray_compute_frame_crc(const flexray_frame_t* frame) {
    uint32_t crc = 0xFEDCBA;
    uint32_t poly = 0x5B2EC7;
    uint32_t payload_bytes = (uint32_t)frame->header.payload_length * 2;

    /* Упаковка байтів заголовка у формат передачі */
    uint8_t header_bytes[FLEXRAY_HEADER_SIZE];
    header_bytes[0] = (frame->header.payload_preamble << 6) |
                      (frame->header.null_frame << 5) |
                      (frame->header.sync_frame << 4) |
                      (frame->header.startup_frame << 3) |
                      ((frame->header.frame_id >> 8) & 0x07);
    header_bytes[1] = frame->header.frame_id & 0xFF;
    header_bytes[2] = ((frame->header.payload_length >> 4) & 0x0F) |
                      ((frame->header.header_crc >> 7) & 0xF0);
    header_bytes[3] = (frame->header.header_crc << 1) & 0xFE;
    header_bytes[4] = frame->header.cycle_count & 0x3F;

    /* Обробка байтів заголовка */
    for (int b = 0; b < FLEXRAY_HEADER_SIZE; b++) {
        for (int i = 7; i >= 0; i--) {
            uint32_t bit = (header_bytes[b] >> i) & 0x01;
            uint32_t crc_msb = (crc >> 23) & 0x01;
            crc = (crc << 1) & 0xFFFFFF;
            if (bit ^ crc_msb) {
                crc ^= poly;
            }
        }
    }

    /* Обробка байтів даних */
    for (uint32_t b = 0; b < payload_bytes; b++) {
        for (int i = 7; i >= 0; i--) {
            uint32_t bit = (frame->payload[b] >> i) & 0x01;
            uint32_t crc_msb = (crc >> 23) & 0x01;
            crc = (crc << 1) & 0xFFFFFF;
            if (bit ^ crc_msb) {
                crc ^= poly;
            }
        }
    }
    return crc & 0xFFFFFF;
}

/* Перевірка цілісності кадру */
bool flexray_verify_frame(const flexray_frame_t* frame) {
    uint16_t expected_header_crc = flexray_compute_header_crc(&frame->header);
    if (expected_header_crc != frame->header.header_crc) {
        printf("[ERROR] Header CRC Mismatch! Calc: 0x%03X, Recv: 0x%03X\n",
               expected_header_crc, frame->header.header_crc);
        return false;
    }

    uint32_t expected_frame_crc = flexray_compute_frame_crc(frame);
    if (expected_frame_crc != frame->frame_crc) {
        printf("[ERROR] Frame CRC Mismatch! Calc: 0x%06X, Recv: 0x%06X\n",
               expected_frame_crc, frame->frame_crc);
        return false;
    }

    return true;
}

int main(void) {
    flexray_frame_t frame;
    memset(&frame, 0, sizeof(frame));

    frame.header.payload_preamble = false;
    frame.header.null_frame = true;
    frame.header.sync_frame = true;
    frame.header.startup_frame = false;
    frame.header.frame_id = 12;      /* Статичний слот №12 */
    frame.header.payload_length = 4; /* 4 слова = 8 байтів */
    frame.header.cycle_count = 1;

    frame.header.header_crc = flexray_compute_header_crc(&frame.header);

    /* Копіювання сигнальних даних у байтовий масив */
    uint16_t test_data[4] = { 0x1234, 0x5678, 0x9ABC, 0xDEF0 };
    memcpy(frame.payload, test_data, sizeof(test_data));

    frame.frame_crc = flexray_compute_frame_crc(&frame);

    printf("FlexRay Frame Simulator (C99 Execution):\n");
    printf("----------------------------------------\n");
    printf("Frame ID:       %u (Static Slot)\n", frame.header.frame_id);
    printf("Payload Length: %u words (%u bytes)\n", frame.header.payload_length, frame.header.payload_length * 2);
    printf("Header CRC:     0x%03X\n", frame.header.header_crc);
    printf("Frame CRC:      0x%06X\n", frame.frame_crc);

    bool is_valid = flexray_verify_frame(&frame);
    printf("Verification:   %s\n", is_valid ? "PASSED (OK)" : "FAILED");

    return 0;
}
