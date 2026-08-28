#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PMS5003_FRAME_SIZE 32
#define PMS5003_HEADER_1   0x42
#define PMS5003_HEADER_2   0x4D

typedef struct {
    uint16_t pm1_0_std;   // PM1.0 стандартний аерозоль (мкг/м³)
    uint16_t pm2_5_std;   // PM2.5 стандартний аерозоль (мкг/м³)
    uint16_t pm10_std;    // PM10  стандартний аерозоль (мкг/м³)
    uint16_t pm1_0_atm;   // PM1.0 атмосферне повітря (мкг/м³)
    uint16_t pm2_5_atm;   // PM2.5 атмосферне повітря (мкг/м³)
    uint16_t pm10_atm;    // PM10  атмосферне повітря (мкг/м³)
    uint16_t count_0_3;   // Частинок >0.3 мкм в 0.1 л повітря
    uint16_t count_0_5;   // Частинок >0.5 мкм в 0.1 л повітря
    uint16_t count_1_0;   // Частинок >1.0 мкм в 0.1 л повітря
    uint16_t count_2_5;   // Частинок >2.5 мкм в 0.1 л повітря
    uint16_t count_5_0;   // Частинок >5.0 мкм в 0.1 л повітря
    uint16_t count_10;    // Частинок >10 мкм в 0.1 л повітря
} pms5003_data_t;

typedef enum {
    STATE_WAIT_H1 = 0,
    STATE_WAIT_H2,
    STATE_READ_PAYLOAD
} pms5003_state_t;

typedef struct {
    pms5003_state_t state;
    uint8_t buffer[PMS5003_FRAME_SIZE];
    uint8_t index;
} pms5003_parser_t;

void pms5003_parser_init(pms5003_parser_t *parser) {
    if (!parser) return;
    parser->state = STATE_WAIT_H1;
    parser->index = 0;
}

static uint16_t parse_be16(const uint8_t *p) {
    return (uint16_t)((p[0] << 8) | p[1]);
}

bool pms5003_parse_byte(pms5003_parser_t *parser, uint8_t byte, pms5003_data_t *out_data) {
    if (!parser || !out_data) return false;

    switch (parser->state) {
        case STATE_WAIT_H1:
            if (byte == PMS5003_HEADER_1) {
                parser->buffer[0] = byte;
                parser->index = 1;
                parser->state = STATE_WAIT_H2;
            }
            break;

        case STATE_WAIT_H2:
            if (byte == PMS5003_HEADER_2) {
                parser->buffer[1] = byte;
                parser->index = 2;
                parser->state = STATE_READ_PAYLOAD;
            } else if (byte == PMS5003_HEADER_1) {
                parser->index = 1; // повторний перший байт
            } else {
                parser->state = STATE_WAIT_H1;
            }
            break;

        case STATE_READ_PAYLOAD:
            parser->buffer[parser->index++] = byte;
            if (parser->index >= PMS5003_FRAME_SIZE) {
                parser->state = STATE_WAIT_H1;

                // Перевірка довжини корисного навантаження (байти 2..3 мають бути 0x001C)
                uint16_t frame_len = parse_be16(&parser->buffer[2]);
                if (frame_len != 28) {
                    return false;
                }

                // Перевірка 16-бітної контрольної суми (сума перших 30 байтів)
                uint16_t calc_sum = 0;
                for (size_t i = 0; i < 30; ++i) {
                    calc_sum += parser->buffer[i];
                }
                uint16_t rx_sum = parse_be16(&parser->buffer[30]);
                if (calc_sum != rx_sum) {
                    return false;
                }

                // Десеріалізація виміряних значень
                out_data->pm1_0_std = parse_be16(&parser->buffer[4]);
                out_data->pm2_5_std = parse_be16(&parser->buffer[6]);
                out_data->pm10_std  = parse_be16(&parser->buffer[8]);
                out_data->pm1_0_atm = parse_be16(&parser->buffer[10]);
                out_data->pm2_5_atm = parse_be16(&parser->buffer[12]);
                out_data->pm10_atm  = parse_be16(&parser->buffer[14]);
                out_data->count_0_3 = parse_be16(&parser->buffer[16]);
                out_data->count_0_5 = parse_be16(&parser->buffer[18]);
                out_data->count_1_0 = parse_be16(&parser->buffer[20]);
                out_data->count_2_5 = parse_be16(&parser->buffer[22]);
                out_data->count_5_0 = parse_be16(&parser->buffer[24]);
                out_data->count_10  = parse_be16(&parser->buffer[26]);

                return true;
            }
            break;
    }
    return false;
}
