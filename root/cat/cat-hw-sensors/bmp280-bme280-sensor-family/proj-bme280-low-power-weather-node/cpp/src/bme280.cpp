#include "bme280.hpp"
#include <iostream>
#include <thread>
#include <chrono>

BME280::BME280(I2CBus& bus, uint8_t address)
    : bus_(bus), address_(address) {}

bool BME280::init() {
    if (!bus_.set_slave_address(address_)) {
        std::cerr << "[BME280] Не вдалося встановити I2C адресу 0x"
                  << std::hex << static_cast<int>(address_) << std::dec << std::endl;
        return false;
    }

    // Перевірка Chip ID (повинен бути 0x60 для BME280)
    uint8_t chip_id = 0;
    if (!bus_.read_register(REG_CHIP_ID, chip_id)) {
        std::cerr << "[BME280] Не вдалося прочитати Chip ID" << std::endl;
        return false;
    }

    if (chip_id != CHIP_ID_EXPECTED) {
        std::cerr << "[BME280] Невідповідність Chip ID! Очікувалось: 0x60, отримано: 0x"
                  << std::hex << static_cast<int>(chip_id) << std::dec << std::endl;
        return false;
    }

    // Програмне скидання давача (Soft Reset: 0xB6 у регістр 0xE0)
    if (!bus_.write_register(REG_SOFT_RESET, 0xB6)) {
        std::cerr << "[BME280] Помилка виконання Soft Reset" << std::endl;
        return false;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(10));

    // Зчитування калібрувальних коефіцієнтів із NVRAM
    if (!read_calibration_data()) {
        std::cerr << "[BME280] Не вдалося зчитати калібрувальні коефіцієнти NVRAM" << std::endl;
        return false;
    }

    return true;
}

bool BME280::read_calibration_data() {
    uint8_t calib1[26] = {0};
    if (!bus_.read_bytes(REG_DIG_T1, calib1, 26)) {
        return false;
    }

    // Распаковка першого блоку калібрувальних даних (0x88..0xA1)
    calib_.dig_T1 = static_cast<uint16_t>(calib1[0] | (calib1[1] << 8));
    calib_.dig_T2 = static_cast<int16_t>(calib1[2] | (calib1[3] << 8));
    calib_.dig_T3 = static_cast<int16_t>(calib1[4] | (calib1[5] << 8));

    calib_.dig_P1 = static_cast<uint16_t>(calib1[6] | (calib1[7] << 8));
    calib_.dig_P2 = static_cast<int16_t>(calib1[8] | (calib1[9] << 8));
    calib_.dig_P3 = static_cast<int16_t>(calib1[10] | (calib1[11] << 8));
    calib_.dig_P4 = static_cast<int16_t>(calib1[12] | (calib1[13] << 8));
    calib_.dig_P5 = static_cast<int16_t>(calib1[14] | (calib1[15] << 8));
    calib_.dig_P6 = static_cast<int16_t>(calib1[16] | (calib1[17] << 8));
    calib_.dig_P7 = static_cast<int16_t>(calib1[18] | (calib1[19] << 8));
    calib_.dig_P8 = static_cast<int16_t>(calib1[20] | (calib1[21] << 8));
    calib_.dig_P9 = static_cast<int16_t>(calib1[22] | (calib1[23] << 8));

    calib_.dig_H1 = calib1[25]; // 0xA1

    // Распаковка другого блоку калібрувальних даних (0xE1..0xE7)
    uint8_t calib2[7] = {0};
    if (!bus_.read_bytes(REG_DIG_H2, calib2, 7)) {
        return false;
    }

    calib_.dig_H2 = static_cast<int16_t>(calib2[0] | (calib2[1] << 8));
    calib_.dig_H3 = calib2[2];

    // dig_H4: 12-бітне signed значення із 0xE4 (біти 11..4) та 0xE5 (біти 3..0)
    int16_t h4_raw = static_cast<int16_t>((static_cast<uint16_t>(calib2[3]) << 4) | (calib2[4] & 0x0F));
    if (h4_raw & 0x0800) {
        h4_raw |= static_cast<int16_t>(0xF000);
    }
    calib_.dig_H4 = h4_raw;

    // dig_H5: 12-бітне signed значення із 0xE6 (біти 11..4) та 0xE5 (біти 7..4)
    int16_t h5_raw = static_cast<int16_t>((static_cast<uint16_t>(calib2[5]) << 4) | (calib2[4] >> 4));
    if (h5_raw & 0x0800) {
        h5_raw |= static_cast<int16_t>(0xF000);
    }
    calib_.dig_H5 = h5_raw;

    calib_.dig_H6 = static_cast<int8_t>(calib2[6]);

    return true;
}

bool BME280::trigger_forced_measurement(Oversampling os_temp, Oversampling os_press, Oversampling os_hum) {
    if (!bus_.set_slave_address(address_)) {
        return false;
    }

    // УВАГА: Налаштування ctrl_hum (0xF2) набуває чинності лише після запису в ctrl_meas (0xF4)
    uint8_t hum_reg = static_cast<uint8_t>(os_hum) & 0x07;
    if (!bus_.write_register(REG_CTRL_HUM, hum_reg)) {
        return false;
    }

    // Формування бітів ctrl_meas: [7..5: osrs_t] [4..2: osrs_p] [1..0: mode]
    // Mode = 0x01 (Forced Mode)
    uint8_t meas_reg = ((static_cast<uint8_t>(os_temp) & 0x07) << 5) |
                       ((static_cast<uint8_t>(os_press) & 0x07) << 2) |
                       0x01; // Forced mode

    return bus_.write_register(REG_CTRL_MEAS, meas_reg);
}

bool BME280::is_measuring(bool& measuring) {
    if (!bus_.set_slave_address(address_)) {
        return false;
    }
    uint8_t status = 0;
    if (!bus_.read_register(REG_STATUS, status)) {
        return false;
    }
    // Біт 3 у регістрі STATUS (0xF3) — measuring flag
    measuring = (status & 0x08) != 0;
    return true;
}

bool BME280::wait_until_ready(uint32_t timeout_ms) {
    auto start = std::chrono::steady_clock::now();
    while (true) {
        bool measuring = true;
        if (!is_measuring(measuring)) {
            return false;
        }
        if (!measuring) {
            return true;
        }
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - start
        ).count();
        if (elapsed >= timeout_ms) {
            std::cerr << "[BME280] Таймаут очікування готовності даних вимірювання" << std::endl;
            return false;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    }
}

bool BME280::read_sensor_data(Bme280Data& data) {
    if (!bus_.set_slave_address(address_)) {
        return false;
    }

    // Зчитування 8 байтів починаючи з REG_DATA_START (0xF7)
    // 0xF7..0xF9: Pressure MSB, LSB, XLSB
    // 0xFA..0xFC: Temperature MSB, LSB, XLSB
    // 0xFD..0xFE: Humidity MSB, LSB
    uint8_t raw[8] = {0};
    if (!bus_.read_bytes(REG_DATA_START, raw, 8)) {
        return false;
    }

    int32_t adc_P = static_cast<int32_t>((static_cast<uint32_t>(raw[0]) << 12) |
                                         (static_cast<uint32_t>(raw[1]) << 4)  |
                                         (static_cast<uint32_t>(raw[2]) >> 4));

    int32_t adc_T = static_cast<int32_t>((static_cast<uint32_t>(raw[3]) << 12) |
                                         (static_cast<uint32_t>(raw[4]) << 4)  |
                                         (static_cast<uint32_t>(raw[5]) >> 4));

    int32_t adc_H = static_cast<int32_t>((static_cast<uint32_t>(raw[6]) << 8) |
                                         static_cast<uint32_t>(raw[7]));

    int32_t t_fine = 0;
    data.temperature_c = compensate_temperature(adc_T, t_fine);
    data.pressure_pa    = compensate_pressure(adc_P, t_fine);
    data.humidity_pct   = compensate_humidity(adc_H, t_fine);

    return true;
}

bool BME280::perform_single_measurement(Bme280Data& data, Oversampling os_temp, Oversampling os_press, Oversampling os_hum) {
    if (!trigger_forced_measurement(os_temp, os_press, os_hum)) {
        return false;
    }
    if (!wait_until_ready(100)) {
        return false;
    }
    return read_sensor_data(data);
}

double BME280::compensate_temperature(int32_t adc_T, int32_t& t_fine) {
    double var1 = (static_cast<double>(adc_T) / 16384.0 - static_cast<double>(calib_.dig_T1) / 1024.0) *
                  static_cast<double>(calib_.dig_T2);
    double var2 = ((static_cast<double>(adc_T) / 131072.0 - static_cast<double>(calib_.dig_T1) / 8192.0) *
                   (static_cast<double>(adc_T) / 131072.0 - static_cast<double>(calib_.dig_T1) / 8192.0)) *
                  static_cast<double>(calib_.dig_T3);

    t_fine = static_cast<int32_t>(var1 + var2);
    return (var1 + var2) / 5120.0;
}

double BME280::compensate_pressure(int32_t adc_P, int32_t t_fine) {
    double var1 = (static_cast<double>(t_fine) / 2.0) - 64000.0;
    double var2 = var1 * var1 * static_cast<double>(calib_.dig_P6) / 32768.0;
    var2 = var2 + var1 * static_cast<double>(calib_.dig_P5) * 2.0;
    var2 = (var2 / 4.0) + (static_cast<double>(calib_.dig_P4) * 65536.0);

    var1 = (static_cast<double>(calib_.dig_P3) * var1 * var1 / 524288.0 + static_cast<double>(calib_.dig_P2) * var1) / 524288.0;
    var1 = (1.0 + var1 / 32768.0) * static_cast<double>(calib_.dig_P1);

    if (var1 == 0.0) {
        return 0.0; // Запобігання діленню на нуль
    }

    double p = 1048576.0 - static_cast<double>(adc_P);
    p = (p - (var2 / 4096.0)) * 6250.0 / var1;
    var1 = static_cast<double>(calib_.dig_P9) * p * p / 2147483648.0;
    var2 = p * static_cast<double>(calib_.dig_P8) / 32768.0;
    double pressure = p + (var1 + var2 + static_cast<double>(calib_.dig_P7)) / 16.0;

    return pressure;
}

double BME280::compensate_humidity(int32_t adc_H, int32_t t_fine) {
    double var_H = static_cast<double>(t_fine) - 76800.0;
    var_H = (static_cast<double>(adc_H) - (static_cast<double>(calib_.dig_H4) * 64.0 + static_cast<double>(calib_.dig_H5) / 16384.0 * var_H)) *
            (static_cast<double>(calib_.dig_H2) / 65536.0 * (1.0 + static_cast<double>(calib_.dig_H6) / 67108864.0 * var_H *
            (1.0 + static_cast<double>(calib_.dig_H3) / 67108864.0 * var_H)));
    var_H = var_H * (1.0 - static_cast<double>(calib_.dig_H1) * var_H / 524288.0);

    if (var_H > 100.0) {
        var_H = 100.0;
    } else if (var_H < 0.0) {
        var_H = 0.0;
    }

    return var_H;
}
