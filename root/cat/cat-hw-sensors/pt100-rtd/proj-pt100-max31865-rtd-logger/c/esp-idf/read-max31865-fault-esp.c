#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include "driver/spi_master.h"

typedef struct {
    uint32_t timestamp_ms;
    float    temperature;
    uint8_t  fault_code;
    bool     is_valid;
} telemetry_packet_t;

uint8_t read_max31865_fault_esp(spi_device_handle_t spi) {
    uint8_t tx_buf[2] = {0x07, 0x00};
    uint8_t rx_buf[2] = {0};
    spi_transaction_t t = {
        .length = 16,
        .tx_buffer = tx_buf,
        .rx_buffer = rx_buf,
    };
    spi_device_transmit(spi, &t);
    return rx_buf[1];
}

telemetry_packet_t process_logger_sample_esp(spi_device_handle_t spi, uint32_t now_ms, float raw_rtd) {
    telemetry_packet_t packet;
    packet.timestamp_ms = now_ms;
    packet.fault_code = read_max31865_fault_esp(spi);

    if (packet.fault_code != 0) {
        packet.is_valid = false;
        packet.temperature = NAN;
    } else {
        packet.temperature = rtd_to_temperature(raw_rtd);
        packet.is_valid = !isnan(packet.temperature);
    }
    return packet;
}
