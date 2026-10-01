#include "ClimateNode.hpp"

uint16_t ClimatePacket::calculateCRC() const {
    const uint8_t* bytes = reinterpret_cast<const uint8_t*>(this);
    std::size_t length = sizeof(ClimatePacket) - sizeof(uint16_t);
    uint16_t crc = 0xFFFF;

    for (std::size_t i = 0; i < length; ++i) {
        crc ^= (static_cast<uint16_t>(bytes[i]) << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

ClimateNode::ClimateNode(II2CBus& i2c_bus, PollingConfig config)
    : i2c_(i2c_bus), config_(config) {}

bool ClimateNode::begin() {
    bool aht_ok = initAHT20();
    bool bmp_ok = initBMP280();
    return aht_ok || bmp_ok;
}

bool ClimateNode::initAHT20() {
    uint8_t status = 0;
    if (!i2c_.readBytes(AHT20_I2C_ADDR, &status, 1)) {
        return false;
    }
    // Бит 3 вказує на відкаліброваність сенсора
    if ((status & 0x08) == 0) {
        uint8_t init_cmd[3] = {0xBE, 0x08, 0x00};
        if (!i2c_.writeBytes(AHT20_I2C_ADDR, init_cmd, 3)) {
            return false;
        }
    }
    return true;
}

bool ClimateNode::triggerAHT20Measurement() {
    uint8_t trigger_cmd[3] = {0xAC, 0x33, 0x00};
    return i2c_.writeBytes(AHT20_I2C_ADDR, trigger_cmd, 3);
}

bool ClimateNode::readAHT20Data(float& temperature, float& humidity) {
    uint8_t data[7] = {0};
    if (!i2c_.readBytes(AHT20_I2C_ADDR, data, 7)) {
        return false;
    }

    // Бит 7 у байті стану означає процес перетворення (Busy)
    if ((data[0] & 0x80) != 0) {
        return false;
    }

    uint32_t raw_hum = ((static_cast<uint32_t>(data[1]) << 12) |
                        (static_cast<uint32_t>(data[2]) << 4)  |
                        (static_cast<uint32_t>(data[3]) >> 4));

    uint32_t raw_temp = (((static_cast<uint32_t>(data[3]) & 0x0F) << 16) |
                         (static_cast<uint32_t>(data[4]) << 8)         |
                         static_cast<uint32_t>(data[5]));

    humidity = (static_cast<float>(raw_hum) / 1048576.0f) * 100.0f;
    temperature = (static_cast<float>(raw_temp) / 1048576.0f) * 200.0f - 50.0f;

    // Перевірка діапазонів фізичної коректності
    if (humidity < 0.0f || humidity > 100.0f || temperature < -40.0f || temperature > 85.0f) {
        return false;
    }

    return true;
}

bool ClimateNode::initBMP280() {
    uint8_t chip_id = 0;
    if (!i2c_.readRegisters(BMP280_I2C_ADDR, 0xD0, &chip_id, 1)) {
        return false;
    }
    if (chip_id != 0x58) { // Фіксований Chip ID для BMP280
        return false;
    }
    return readBMP280Calibration();
}

bool ClimateNode::readBMP280Calibration() {
    uint8_t calib_buf[24] = {0};
    if (!i2c_.readRegisters(BMP280_I2C_ADDR, 0x88, calib_buf, 24)) {
        return false;
    }

    bmp280_calib_.dig_T1 = static_cast<uint16_t>(calib_buf[0]  | (calib_buf[1] << 8));
    bmp280_calib_.dig_T2 = static_cast<int16_t>(calib_buf[2]   | (calib_buf[3] << 8));
    bmp280_calib_.dig_T3 = static_cast<int16_t>(calib_buf[4]   | (calib_buf[5] << 8));
    bmp280_calib_.dig_P1 = static_cast<uint16_t>(calib_buf[6]  | (calib_buf[7] << 8));
    bmp280_calib_.dig_P2 = static_cast<int16_t>(calib_buf[8]   | (calib_buf[9] << 8));
    bmp280_calib_.dig_P3 = static_cast<int16_t>(calib_buf[10]  | (calib_buf[11] << 8));
    bmp280_calib_.dig_P4 = static_cast<int16_t>(calib_buf[12]  | (calib_buf[13] << 8));
    bmp280_calib_.dig_P5 = static_cast<int16_t>(calib_buf[14]  | (calib_buf[15] << 8));
    bmp280_calib_.dig_P6 = static_cast<int16_t>(calib_buf[16]  | (calib_buf[17] << 8));
    bmp280_calib_.dig_P7 = static_cast<int16_t>(calib_buf[18]  | (calib_buf[19] << 8));
    bmp280_calib_.dig_P8 = static_cast<int16_t>(calib_buf[20]  | (calib_buf[21] << 8));
    bmp280_calib_.dig_P9 = static_cast<int16_t>(calib_buf[22]  | (calib_buf[23] << 8));

    return true;
}

bool ClimateNode::triggerBMP280Measurement() {
    // ctrl_meas (0xF4): osrs_t x2 (010b), osrs_p x16 (101b), mode Forced (01b) -> 0x55
    uint8_t ctrl_meas = (2 << 5) | (5 << 2) | 1;
    return i2c_.writeRegisters(BMP280_I2C_ADDR, 0xF4, &ctrl_meas, 1);
}

bool ClimateNode::readBMP280Data(float& temperature, float& pressure_pa) {
    uint8_t data[6] = {0};
    if (!i2c_.readRegisters(BMP280_I2C_ADDR, 0xF7, data, 6)) {
        return false;
    }

    int32_t adc_P = (static_cast<int32_t>(data[0]) << 12) |
                    (static_cast<int32_t>(data[1]) << 4)  |
                    (static_cast<int32_t>(data[2]) >> 4);

    int32_t adc_T = (static_cast<int32_t>(data[3]) << 12) |
                    (static_cast<int32_t>(data[4]) << 4)  |
                    (static_cast<int32_t>(data[5]) >> 4);

    int32_t temp_raw = compensateTemperatureBMP280(adc_T);
    temperature = static_cast<float>(temp_raw) / 100.0f;

    uint32_t press_raw = compensatePressureBMP280(adc_P);
    pressure_pa = static_cast<float>(press_raw);

    return (temperature >= -40.0f && temperature <= 85.0f && pressure_pa > 30000.0f && pressure_pa < 110000.0f);
}

int32_t ClimateNode::compensateTemperatureBMP280(int32_t adc_T) {
    int32_t var1 = ((((adc_T >> 3) - (static_cast<int32_t>(bmp280_calib_.dig_T1) << 1))) *
                    (static_cast<int32_t>(bmp280_calib_.dig_T2))) >> 11;
    int32_t var2 = (((((adc_T >> 4) - static_cast<int32_t>(bmp280_calib_.dig_T1)) *
                      ((adc_T >> 4) - static_cast<int32_t>(bmp280_calib_.dig_T1))) >> 12) *
                    static_cast<int32_t>(bmp280_calib_.dig_T3)) >> 14;
    bmp280_calib_.t_fine = var1 + var2;
    return (bmp280_calib_.t_fine * 5 + 128) >> 8;
}

uint32_t ClimateNode::compensatePressureBMP280(int32_t adc_P) {
    int64_t var1 = static_cast<int64_t>(bmp280_calib_.t_fine) - 128000;
    int64_t var2 = var1 * var1 * static_cast<int64_t>(bmp280_calib_.dig_P6);
    var2 = var2 + ((var1 * static_cast<int64_t>(bmp280_calib_.dig_P5)) << 17);
    var2 = var2 + (static_cast<int64_t>(bmp280_calib_.dig_P4) << 35);
    var1 = ((var1 * var1 * static_cast<int64_t>(bmp280_calib_.dig_P3)) >> 8) +
           ((var1 * static_cast<int64_t>(bmp280_calib_.dig_P2)) << 12);
    var1 = (((static_cast<int64_t>(1) << 47) + var1)) * static_cast<int64_t>(bmp280_calib_.dig_P1) >> 33;

    if (var1 == 0) {
        return 0;
    }
    int64_t p = 1048576 - adc_P;
    p = (((p << 31) - var2) * 3125) / var1;
    var1 = (static_cast<int64_t>(bmp280_calib_.dig_P9) * (p >> 13) * (p >> 13)) >> 25;
    var2 = (static_cast<int64_t>(bmp280_calib_.dig_P8) * p) >> 19;
    p = ((p + var1 + var2) >> 8) + (static_cast<int64_t>(bmp280_calib_.dig_P7) << 4);
    return static_cast<uint32_t>(p / 256);
}

void ClimateNode::update(uint32_t current_time_ms) {
    switch (state_) {
        case NodeState::IDLE: {
            if ((current_time_ms - last_poll_start_ms_) >= config_.poll_interval_ms) {
                last_poll_start_ms_ = current_time_ms;
                state_ = NodeState::TRIGGER_AHT20;
            }
            break;
        }

        case NodeState::TRIGGER_AHT20: {
            if (triggerAHT20Measurement()) {
                state_timer_ms_ = current_time_ms;
                state_ = NodeState::WAIT_AHT20;
            } else {
                raw_data_.aht20_valid = false;
                state_ = NodeState::TRIGGER_BMP280;
            }
            break;
        }

        case NodeState::WAIT_AHT20: {
            if ((current_time_ms - state_timer_ms_) >= config_.aht20_delay_ms) {
                state_ = NodeState::READ_AHT20;
            }
            break;
        }

        case NodeState::READ_AHT20: {
            raw_data_.aht20_valid = readAHT20Data(raw_data_.temperature_aht20, raw_data_.humidity_aht20);
            state_ = NodeState::TRIGGER_BMP280;
            break;
        }

        case NodeState::TRIGGER_BMP280: {
            if (triggerBMP280Measurement()) {
                state_timer_ms_ = current_time_ms;
                state_ = NodeState::WAIT_BMP280;
            } else {
                raw_data_.bmp280_valid = false;
                state_ = NodeState::PROCESS_AND_PACK;
            }
            break;
        }

        case NodeState::WAIT_BMP280: {
            if ((current_time_ms - state_timer_ms_) >= config_.bmp280_delay_ms) {
                state_ = NodeState::READ_BMP280;
            }
            break;
        }

        case NodeState::READ_BMP280: {
            raw_data_.bmp280_valid = readBMP280Data(raw_data_.temperature_bmp280, raw_data_.pressure_bmp280);
            state_ = NodeState::PROCESS_AND_PACK;
            break;
        }

        case NodeState::PROCESS_AND_PACK: {
            // Комплексна обробка вимірів температури від двох сенсорів
            if (raw_data_.aht20_valid && raw_data_.bmp280_valid) {
                float avg_temp = (raw_data_.temperature_aht20 + raw_data_.temperature_bmp280) / 2.0f;
                temp_filter_.addSample(avg_temp);
            } else if (raw_data_.aht20_valid) {
                temp_filter_.addSample(raw_data_.temperature_aht20);
            } else if (raw_data_.bmp280_valid) {
                temp_filter_.addSample(raw_data_.temperature_bmp280);
            }

            if (raw_data_.aht20_valid) {
                humidity_filter_.addSample(raw_data_.humidity_aht20);
            }

            if (raw_data_.bmp280_valid) {
                float pressure_hpa = raw_data_.pressure_bmp280 / 100.0f;
                pressure_filter_.addSample(pressure_hpa);
            }

            // Оновлення згладжених даних
            processed_data_.temperature  = temp_filter_.getAverage();
            processed_data_.humidity     = humidity_filter_.getAverage();
            processed_data_.pressure_hpa = pressure_filter_.getAverage();
            processed_data_.data_valid   = (raw_data_.aht20_valid || raw_data_.bmp280_valid);

            // Упаковка телеметричного пакета
            latest_packet_.timestamp_ms = current_time_ms;
            latest_packet_.temperature  = processed_data_.temperature;
            latest_packet_.humidity     = processed_data_.humidity;
            latest_packet_.pressure_hpa = processed_data_.pressure_hpa;

            latest_packet_.status_flags = 0;
            if (raw_data_.aht20_valid)  latest_packet_.status_flags |= (1 << 0);
            if (raw_data_.bmp280_valid) latest_packet_.status_flags |= (1 << 1);
            if (temp_filter_.isFull() && humidity_filter_.isFull() && pressure_filter_.isFull()) {
                latest_packet_.status_flags |= (1 << 2);
            }

            latest_packet_.checksum = latest_packet_.calculateCRC();
            new_packet_available_ = true;

            state_ = NodeState::IDLE;
            break;
        }
    }
}

std::optional<ClimatePacket> ClimateNode::getLatestPacket() {
    if (!new_packet_available_) {
        return std::nullopt;
    }
    new_packet_available_ = false;
    return latest_packet_;
}
