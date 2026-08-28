// console_controller.c — Модуль опитування стіків та пакування радіокадру
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CHANNELS_COUNT      4
#define ADC_MAX_VAL         4095
#define CHANNEL_MAX_11BIT   2047
#define DEAD_BAND_THRESHOLD 30

typedef struct {
    uint16_t min;
    uint16_t center;
    uint16_t max;
    uint16_t deadband;
} GimbalCalib;

typedef struct {
    uint8_t  sync_byte;      // 0x5A
    uint8_t  sequence_id;    // 0..255
    uint8_t  packed_axes[6]; // 4 канали по 11 біт (44 біти)
    uint8_t  switches_mask;  // Бітова маска тумблерів
    uint8_t  command_flags;  // Прапорці запитів
    uint16_t crc16;          // Контрольна сума CRC-16-CCITT
} __attribute__((packed)) RadioControlFrame;

static GimbalCalib g_calib[CHANNELS_COUNT] = {
    { .min = 350,  .center = 2048, .max = 3750, .deadband = DEAD_BAND_THRESHOLD }, // Roll
    { .min = 360,  .center = 2050, .max = 3740, .deadband = DEAD_BAND_THRESHOLD }, // Pitch
    { .min = 340,  .center = 2040, .max = 3760, .deadband = 10 },                  // Throttle
    { .min = 355,  .center = 2045, .max = 3745, .deadband = DEAD_BAND_THRESHOLD }  // Yaw
};

static uint16_t g_filtered_adc[CHANNELS_COUNT] = {2048, 2048, 0, 2048};
static uint8_t  g_frame_seq = 0;

// Обчислення CRC-16-CCITT (поліном 0x1021)
static uint16_t crc16_ccitt(const uint8_t *data, size_t length) {
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

// Нормалізація та фільтрація відліків АЦП
uint16_t process_gimbal_axis(uint8_t ch, uint16_t raw_adc) {
    // IIR фільтрація 1-го порядку: y[k] = 0.5 * raw + 0.5 * y[k-1]
    g_filtered_adc[ch] = (uint16_t)((raw_adc + g_filtered_adc[ch]) >> 1);
    uint16_t val = g_filtered_adc[ch];
    const GimbalCalib *c = &g_calib[ch];

    if (val < c->min) val = c->min;
    if (val > c->max) val = c->max;

    // Спеціальна обробка для газу (від 0 до MAX без центру)
    if (ch == 2) {
        uint32_t norm = (uint32_t)(val - c->min) * CHANNEL_MAX_11BIT / (c->max - c->min);
        return (uint16_t)norm;
    }

    // Обробка осей із центром (Roll, Pitch, Yaw)
    int32_t delta = (int32_t)val - (int32_t)c->center;
    if (delta > -c->deadband && delta < c->deadband) {
        return CHANNEL_MAX_11BIT / 2; // Рівно центр (1024)
    }

    if (delta > 0) {
        uint32_t span = c->max - c->center;
        uint32_t out = (CHANNEL_MAX_11BIT / 2) + 
                       ((uint32_t)delta * (CHANNEL_MAX_11BIT / 2) / span);
        return (out > CHANNEL_MAX_11BIT) ? CHANNEL_MAX_11BIT : (uint16_t)out;
    } else {
        uint32_t span = c->center - c->min;
        int32_t out = (CHANNEL_MAX_11BIT / 2) - 
                      ((uint32_t)(-delta) * (CHANNEL_MAX_11BIT / 2) / span);
        return (out < 0) ? 0 : (uint16_t)out;
    }
}

// Формування кадру керування
void build_radio_packet(const uint16_t raw_dma_adc[CHANNELS_COUNT], 
                        uint8_t switches, RadioControlFrame *out_frame) {
    uint16_t norm_channels[CHANNELS_COUNT];
    for (uint8_t i = 0; i < CHANNELS_COUNT; i++) {
        norm_channels[i] = process_gimbal_axis(i, raw_dma_adc[i]);
    }

    out_frame->sync_byte = 0x5A;
    out_frame->sequence_id = g_frame_seq++;
    out_frame->switches_mask = switches;
    out_frame->command_flags = 0x00;

    // Щільне бітове пакування чотирьох 11-бітних осей у 6 байтів
    out_frame->packed_axes[0] = (uint8_t)(norm_channels[0] & 0xFF);
    out_frame->packed_axes[1] = (uint8_t)(((norm_channels[0] >> 8) & 0x07) | 
                                         ((norm_channels[1] & 0x1F) << 3));
    out_frame->packed_axes[2] = (uint8_t)(((norm_channels[1] >> 5) & 0x3F) | 
                                         ((norm_channels[2] & 0x03) << 6));
    out_frame->packed_axes[3] = (uint8_t)((norm_channels[2] >> 2) & 0xFF);
    out_frame->packed_axes[4] = (uint8_t)(((norm_channels[2] >> 10) & 0x01) | 
                                         ((norm_channels[3] & 0x7F) << 1));
    out_frame->packed_axes[5] = (uint8_t)((norm_channels[3] >> 7) & 0x0F);

    // Розрахунок контрольної суми без поля CRC
    out_frame->crc16 = crc16_ccitt((const uint8_t*)out_frame, 
                                   sizeof(RadioControlFrame) - sizeof(uint16_t));
}
