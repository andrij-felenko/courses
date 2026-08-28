// minimal_remote_firmware.c — Повний відкритий модуль прошивки пульта
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CHANNELS_TOTAL       4
#define FRAME_SYNC_BYTE      0x5A
#define SX1280_CMD_SET_TX    0x83
#define SX1280_CMD_SET_RX    0x82
#define SX1280_CMD_WRITE_BUF 0x18
#define SX1280_CMD_READ_BUF  0x19

// Структура калібрування стіка
typedef struct {
    uint16_t min_raw;
    uint16_t center_raw;
    uint16_t max_raw;
    uint16_t deadband;
} StickCalibration;

// Структура вихідного радіокадру керування
typedef struct {
    uint8_t  sync;
    uint8_t  sequence;
    uint8_t  packed_channels[6];
    uint8_t  switches;
    uint8_t  flags;
    uint16_t crc;
} __attribute__((packed)) UplinkPacket;

// Структура вхідного кадру бортової телеметрії
typedef struct {
    uint8_t  sync;
    uint8_t  sequence;
    uint16_t vbat_mv;       // Напруга батареї дрона (мВ)
    uint8_t  current_a_x10; // Струм дрона (А * 10)
    uint8_t  rssi_dbm;      // Рівень сигналу (-dBm)
    uint8_t  link_quality;  // Якість лінка (0..100%)
    uint8_t  flight_mode;   // Польотний режим
} __attribute__((packed)) DownlinkTelemetry;

static StickCalibration g_calib[CHANNELS_TOTAL] = {
    { .min_raw = 320, .center_raw = 2048, .max_raw = 3780, .deadband = 25 },
    { .min_raw = 330, .center_raw = 2050, .max_raw = 3770, .deadband = 25 },
    { .min_raw = 310, .center_raw = 2048, .max_raw = 3790, .deadband = 10 },
    { .min_raw = 325, .center_raw = 2045, .max_raw = 3775, .deadband = 25 }
};

static uint16_t g_adc_history[CHANNELS_TOTAL] = {2048, 2048, 0, 2048};
static uint8_t  g_packet_counter = 0;

// Апаратна абстракція SPI DMA
extern void spi_dma_transmit_receive(const uint8_t *tx, uint8_t *rx, size_t len);
extern void hardware_watchdog_reset(void);
extern void set_haptic_vibration(uint8_t intensity_pwm);

static uint16_t compute_crc16(const uint8_t *buf, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)buf[i] << 8;
        for (uint8_t b = 0; b < 8; b++) {
            crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
        }
    }
    return crc;
}

// Обробка, фільтрація та лінеаризація каналу
uint16_t filter_and_scale_axis(uint8_t ch, uint16_t raw_adc) {
    // Цифровий фільтр: експоненційне згладжування
    g_adc_history[ch] = (uint16_t)((raw_adc * 5 + g_adc_history[ch] * 5) / 10);
    uint16_t val = g_adc_history[ch];
    const StickCalibration *c = &g_calib[ch];

    if (val < c->min_raw) val = c->min_raw;
    if (val > c->max_raw) val = c->max_raw;

    // Спеціальний режим для Throttle (без центральної мертвої зони)
    if (ch == 2) {
        uint32_t span = c->max_raw - c->min_raw;
        return span ? (uint16_t)((uint32_t)(val - c->min_raw) * 2047 / span) : 0;
    }

    int32_t diff = (int32_t)val - (int32_t)c->center_raw;
    if (diff > -c->deadband && diff < c->deadband) {
        return 1024; // Нейтральний центр
    }

    if (diff > 0) {
        uint32_t span = c->max_raw - c->center_raw;
        uint32_t res = 1024 + ((uint32_t)diff * 1023 / span);
        return (res > 2047) ? 2047 : (uint16_t)res;
    } else {
        uint32_t span = c->center_raw - c->min_raw;
        int32_t res = 1024 - ((uint32_t)(-diff) * 1024 / span);
        return (res < 0) ? 0 : (uint16_t)res;
    }
}

// Головний обробник 1 кГц радіоциклу
void process_1khz_control_tick(const uint16_t raw_gimbals[CHANNELS_TOTAL], 
                              uint8_t switch_state, DownlinkTelemetry *out_telemetry) {
    uint16_t scaled_axes[CHANNELS_TOTAL];
    for (uint8_t i = 0; i < CHANNELS_TOTAL; i++) {
        scaled_axes[i] = filter_and_scale_axis(i, raw_gimbals[i]);
    }

    // Пакування бінарного кадру
    UplinkPacket packet;
    packet.sync = FRAME_SYNC_BYTE;
    packet.sequence = g_packet_counter++;
    packet.switches = switch_state;
    packet.flags = 0x00;

    // Пакування 4x 11-бітних осей у 6 байтів
    packet.packed_channels[0] = (uint8_t)(scaled_axes[0] & 0xFF);
    packet.packed_channels[1] = (uint8_t)(((scaled_axes[0] >> 8) & 0x07) | ((scaled_axes[1] & 0x1F) << 3));
    packet.packed_channels[2] = (uint8_t)(((scaled_axes[1] >> 5) & 0x3F) | ((scaled_axes[2] & 0x03) << 6));
    packet.packed_channels[3] = (uint8_t)((scaled_axes[2] >> 2) & 0xFF);
    packet.packed_channels[4] = (uint8_t)(((scaled_axes[2] >> 10) & 0x01) | ((scaled_axes[3] & 0x7F) << 1));
    packet.packed_channels[5] = (uint8_t)((scaled_axes[3] >> 7) & 0x0F);

    packet.crc = compute_crc16((const uint8_t*)&packet, sizeof(UplinkPacket) - sizeof(uint16_t));

    // Відправка кадру в трансивер SX1280 через SPI DMA
    uint8_t tx_cmd[sizeof(UplinkPacket) + 2];
    tx_cmd[0] = SX1280_CMD_WRITE_BUF;
    tx_cmd[1] = 0x00; // Зсув буфера
    memcpy(&tx_cmd[2], &packet, sizeof(UplinkPacket));
    spi_dma_transmit_receive(tx_cmd, NULL, sizeof(tx_cmd));

    // Запуск радіопередачі
    uint8_t set_tx_cmd[4] = {SX1280_CMD_SET_TX, 0x00, 0x00, 0x00};
    spi_dma_transmit_receive(set_tx_cmd, NULL, sizeof(set_tx_cmd));

    // Скидання сторожового таймера
    hardware_watchdog_reset();
}
