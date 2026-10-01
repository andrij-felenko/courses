#pragma once

#include <cstdint>
#include <optional>
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "esp_sleep.h"
#include "esp_log.h"

struct ClimateReading {
    float humidity;
    float temperature;
};

class ClimateNode {
public:
    ClimateNode(gpio_num_t powerPin, i2c_port_t i2cPort, uint8_t sensorAddr = 0x38)
        : m_powerPin(powerPin), m_i2cPort(i2cPort), m_sensorAddr(sensorAddr) {}

    ~ClimateNode() {
        powerOff();
    }

    void powerOn() {
        gpio_config_t pwr_cfg = {
            .pin_bit_mask = (1ULL << m_powerPin),
            .mode = GPIO_MODE_OUTPUT,
            .pull_up_en = GPIO_PULLUP_DISABLE,
            .pull_down_en = GPIO_PULLDOWN_DISABLE,
            .intr_type = GPIO_INTR_DISABLE
        };
        gpio_config(&pwr_cfg);
        gpio_set_level(m_powerPin, 1);
    }

    void powerOff() {
        gpio_set_level(m_powerPin, 0);
    }

    bool initI2C(int sdaPin = 21, int sclPin = 22, uint32_t clkHz = 100000) {
        i2c_config_t conf = {};
        conf.mode = I2C_MODE_MASTER;
        conf.sda_io_num = static_cast<gpio_num_t>(sdaPin);
        conf.sda_pullup_en = GPIO_PULLUP_ENABLE;
        conf.scl_io_num = static_cast<gpio_num_t>(sclPin);
        conf.scl_pullup_en = GPIO_PULLUP_ENABLE;
        conf.master.clk_speed = clkHz;

        if (i2c_param_config(m_i2cPort, &conf) != ESP_OK) return false;
        return (i2c_driver_install(m_i2cPort, conf.mode, 0, 0, 0) == ESP_OK);
    }

    std::optional<ClimateReading> readSensor() {
        uint8_t initCmd[3] = {0xBE, 0x08, 0x00};
        i2c_master_write_to_device(m_i2cPort, m_sensorAddr, initCmd, sizeof(initCmd), pdMS_TO_TICKS(100));
        vTaskDelay(pdMS_TO_TICKS(10));

        uint8_t triggerCmd[3] = {0xAC, 0x33, 0x00};
        if (i2c_master_write_to_device(m_i2cPort, m_sensorAddr, triggerCmd, sizeof(triggerCmd), pdMS_TO_TICKS(100)) != ESP_OK) {
            return std::nullopt;
        }

        vTaskDelay(pdMS_TO_TICKS(80));

        uint8_t rxBuf[7] = {0};
        if (i2c_master_read_from_device(m_i2cPort, m_sensorAddr, rxBuf, sizeof(rxBuf), pdMS_TO_TICKS(100)) != ESP_OK) {
            return std::nullopt;
        }

        if (rxBuf[0] & 0x80) return std::nullopt;

        if (calculateCRC8(rxBuf, 6) != rxBuf[6]) return std::nullopt;

        uint32_t rawHum = ((uint32_t)rxBuf[1] << 12) | ((uint32_t)rxBuf[2] << 4) | ((uint32_t)rxBuf[3] >> 4);
        uint32_t rawTemp = (((uint32_t)rxBuf[3] & 0x0F) << 16) | ((uint32_t)rxBuf[4] << 8) | (uint32_t)rxBuf[5];

        ClimateReading reading;
        reading.humidity = (static_cast<float>(rawHum) / 1048576.0f) * 100.0f;
        reading.temperature = (static_cast<float>(rawTemp) / 1048576.0f) * 200.0f - 50.0f;
        return reading;
    }

    void enterDeepSleep(uint32_t seconds) {
        powerOff();
        i2c_driver_delete(m_i2cPort);
        esp_sleep_enable_timer_wakeup(static_cast<uint64_t>(seconds) * 1000000ULL);
        esp_deep_sleep_start();
    }

private:
    gpio_num_t m_powerPin;
    i2c_port_t m_i2cPort;
    uint8_t m_sensorAddr;

    static uint8_t calculateCRC8(const uint8_t* data, size_t len) {
        uint8_t crc = 0xFF;
        for (size_t i = 0; i < len; ++i) {
            crc ^= data[i];
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x80) {
                    crc = (crc << 1) ^ 0x31;
                } else {
                    crc <<= 1;
                }
            }
        }
        return crc;
    }
};
