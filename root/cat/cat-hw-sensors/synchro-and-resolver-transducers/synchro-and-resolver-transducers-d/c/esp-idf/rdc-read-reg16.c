#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "driver/spi_master.h"
#include "esp_err.h"

// Команди та регістри RDC (на прикладі типового перетворювача AD2S1210)
#define RDC_REG_POSITION_MSB  0x80
#define RDC_REG_VELOCITY_MSB  0x82
#define RDC_REG_FAULT_STATUS  0xFF

typedef struct {
    uint16_t raw_position; // 16-бітний код кута (0..65535)
    int16_t  raw_velocity; // 16-бітний код швидкості зі знаком
    uint8_t  fault_status; // Прапори помилок RDC
} rdc_data_t;

// Зчитування 16-бітного регістру RDC через SPI
static esp_err_t rdc_read_reg16(spi_device_handle_t spi, uint8_t reg_addr, uint16_t *out_val) {
    uint8_t tx_buf[3] = { reg_addr, 0x00, 0x00 };
    uint8_t rx_buf[3] = { 0 };
    
    spi_transaction_t t = {
        .length = 24,
        .tx_buffer = tx_buf,
        .rx_buffer = rx_buf
    };
    
    esp_err_t ret = spi_device_transmit(spi, &t);
    if (ret == ESP_OK && out_val) {
        *out_val = ((uint16_t)rx_buf[1] << 8) | rx_buf[2];
    }
    return ret;
}

// Повний цикл опитування RDC
esp_err_t rdc_read_telemetry(spi_device_handle_t spi, rdc_data_t *data) {
    uint16_t pos_val = 0;
    uint16_t vel_val = 0;
    uint16_t fault_val = 0;

    // Зчитування кута
    esp_err_t err = rdc_read_reg16(spi, RDC_REG_POSITION_MSB, &pos_val);
    if (err != ESP_OK) return err;

    // Зчитування швидкості
    err = rdc_read_reg16(spi, RDC_REG_VELOCITY_MSB, &vel_val);
    if (err != ESP_OK) return err;

    // Зчитування статусу помилок
    err = rdc_read_reg16(spi, RDC_REG_FAULT_STATUS, &fault_val);
    if (err != ESP_OK) return err;

    data->raw_position = pos_val;
    data->raw_velocity = (int16_t)vel_val;
    data->fault_status = (uint8_t)(fault_val & 0xFF);

    return ESP_OK;
}
