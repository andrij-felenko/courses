#include "sensor_node.hpp"
#include "esp_log.h"
#include "esp_adc/adc_cali_scheme.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <cstring>
#include <cmath>

namespace iot {

static const char* TAG = "SensorNode";

SensorNode::SensorNode(gpio_num_t sda_pin, gpio_num_t scl_pin, adc_channel_t vbat_adc_channel)
    : sda_pin_(sda_pin), scl_pin_(scl_pin), vbat_channel_(vbat_adc_channel) {}

SensorNode::~SensorNode() {
    if (sensor_dev_handle_) {
        i2c_master_bus_rm_device(sensor_dev_handle_);
        sensor_dev_handle_ = nullptr;
    }
    if (i2c_bus_handle_) {
        i2c_del_master_bus(i2c_bus_handle_);
        i2c_bus_handle_ = nullptr;
    }
    if (adc_cali_handle_) {
#if ADC_CALI_SCHEME_CURVE_FITTING_SUPPORTED
        adc_cali_delete_scheme_curve_fitting(adc_cali_handle_);
#endif
        adc_cali_handle_ = nullptr;
    }
    if (adc_handle_) {
        adc_oneshot_del_unit(adc_handle_);
        adc_handle_ = nullptr;
    }
}

SensorNode::SensorNode(SensorNode&& other) noexcept
    : sda_pin_(other.sda_pin_),
      scl_pin_(other.scl_pin_),
      vbat_channel_(other.vbat_channel_),
      i2c_bus_handle_(other.i2c_bus_handle_),
      sensor_dev_handle_(other.sensor_dev_handle_),
      adc_handle_(other.adc_handle_),
      adc_cali_handle_(other.adc_cali_handle_),
      initialized_(other.initialized_) {
    other.i2c_bus_handle_ = nullptr;
    other.sensor_dev_handle_ = nullptr;
    other.adc_handle_ = nullptr;
    other.adc_cali_handle_ = nullptr;
    other.initialized_ = false;
}

SensorNode& SensorNode::operator=(SensorNode&& other) noexcept {
    if (this != &other) {
        if (sensor_dev_handle_) i2c_master_bus_rm_device(sensor_dev_handle_);
        if (i2c_bus_handle_) i2c_del_master_bus(i2c_bus_handle_);
        if (adc_handle_) adc_oneshot_del_unit(adc_handle_);

        sda_pin_ = other.sda_pin_;
        scl_pin_ = other.scl_pin_;
        vbat_channel_ = other.vbat_channel_;
        i2c_bus_handle_ = other.i2c_bus_handle_;
        sensor_dev_handle_ = other.sensor_dev_handle_;
        adc_handle_ = other.adc_handle_;
        adc_cali_handle_ = other.adc_cali_handle_;
        initialized_ = other.initialized_;

        other.i2c_bus_handle_ = nullptr;
        other.sensor_dev_handle_ = nullptr;
        other.adc_handle_ = nullptr;
        other.adc_cali_handle_ = nullptr;
        other.initialized_ = false;
    }
    return *this;
}

esp_err_t SensorNode::initialize() noexcept {
    ESP_LOGI(TAG, "Ініціалізація периферії I2C (SDA=%d, SCL=%d)...", sda_pin_, scl_pin_);

    i2c_master_bus_config_t bus_cfg = {};
    bus_cfg.clk_source = I2C_CLK_SRC_DEFAULT;
    bus_cfg.i2c_port = I2C_NUM_0;
    bus_cfg.scl_io_num = scl_pin_;
    bus_cfg.sda_io_num = sda_pin_;
    bus_cfg.glitch_ignore_cnt = 7;
    bus_cfg.flags.enable_internal_pullup = true;

    esp_err_t ret = i2c_new_master_bus(&bus_cfg, &i2c_bus_handle_);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати шину I2C: %s", esp_err_to_name(ret));
        return ret;
    }

    i2c_device_config_t dev_cfg = {};
    dev_cfg.dev_addr_length = I2C_ADDR_BIT_LEN_7;
    dev_cfg.device_address = 0x44;
    dev_cfg.scl_speed_hz = 100000;

    ret = i2c_master_bus_add_device(i2c_bus_handle_, &dev_cfg, &sensor_dev_handle_);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося додати пристрій сенсора I2C: %s", esp_err_to_name(ret));
        return ret;
    }

    adc_oneshot_unit_init_cfg_t init_config = {
        .unit_id = ADC_UNIT_1,
        .clk_src = ADC_RTC_CLK_SRC_DEFAULT,
        .ulp_mode = ADC_ULP_MODE_DISABLE
    };
    ret = adc_oneshot_new_unit(&init_config, &adc_handle_);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка створення блоку АЦП: %s", esp_err_to_name(ret));
        return ret;
    }

    adc_oneshot_chan_cfg_t chan_config = {
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_DEFAULT
    };
    ret = adc_oneshot_config_channel(adc_handle_, vbat_channel_, &chan_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка налаштування каналу АЦП: %s", esp_err_to_name(ret));
        return ret;
    }

    initialized_ = true;
    ESP_LOGI(TAG, "Периферію сенсорів успішно ініціалізовано");
    return ESP_OK;
}

esp_err_t SensorNode::read_i2c_sensor(float& out_temp, float& out_hum) noexcept {
    if (!sensor_dev_handle_) {
        return ESP_ERR_INVALID_STATE;
    }

    const uint8_t measure_cmd[2] = {0x24, 0x00};
    esp_err_t ret = i2c_master_transmit(sensor_dev_handle_, measure_cmd, sizeof(measure_cmd), 100);
    if (ret != ESP_OK) {
        ESP_LOGW(TAG, "Помилка відправки команди I2C: %s", esp_err_to_name(ret));
        return ret;
    }

    vTaskDelay(pdMS_TO_TICKS(15));

    uint8_t read_buf[6] = {0};
    ret = i2c_master_receive(sensor_dev_handle_, read_buf, sizeof(read_buf), 100);
    if (ret != ESP_OK) {
        ESP_LOGW(TAG, "Помилка зчитання даних з I2C: %s", esp_err_to_name(ret));
        return ret;
    }

    uint16_t raw_temp = static_cast<uint16_t>((read_buf[0] << 8) | read_buf[1]);
    uint16_t raw_hum = static_cast<uint16_t>((read_buf[3] << 8) | read_buf[4]);

    out_temp = -45.0f + (175.0f * (static_cast<float>(raw_temp) / 65535.0f));
    out_hum = 100.0f * (static_cast<float>(raw_hum) / 65535.0f);

    return ESP_OK;
}

esp_err_t SensorNode::read_battery_voltage(uint16_t& out_mv) noexcept {
    if (!adc_handle_) {
        return ESP_ERR_INVALID_STATE;
    }

    int raw_val = 0;
    esp_err_t ret = adc_oneshot_read(adc_handle_, vbat_channel_, &raw_val);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка зчитання АЦП: %s", esp_err_to_name(ret));
        return ret;
    }

    constexpr float ADC_MAX_MV = 3300.0f;
    constexpr float ADC_RESOLUTION = 4095.0f;
    constexpr float DIVIDER_RATIO = 2.0f;

    float voltage_mv = (static_cast<float>(raw_val) / ADC_RESOLUTION) * ADC_MAX_MV * DIVIDER_RATIO;
    out_mv = static_cast<uint16_t>(std::round(voltage_mv));

    return ESP_OK;
}

std::optional<SensorMeasurements> SensorNode::read_measurements(uint32_t sequence_counter) noexcept {
    if (!initialized_) {
        ESP_LOGE(TAG, "Неможливо виконати вимірювання до ініціалізації SensorNode");
        return std::nullopt;
    }

    SensorMeasurements measurements{};
    measurements.sample_sequence = sequence_counter;

    esp_err_t temp_ret = read_i2c_sensor(measurements.temperature_c, measurements.humidity_percent);
    if (temp_ret != ESP_OK) {
        ESP_LOGW(TAG, "Не вдалося зчитати сенсор I2C. Використовуються базові значення.");
        measurements.temperature_c = 22.5f;
        measurements.humidity_percent = 50.0f;
    }

    esp_err_t vbat_ret = read_battery_voltage(measurements.battery_mv);
    if (vbat_ret != ESP_OK) {
        measurements.battery_mv = 3300;
    }

    ESP_LOGI(TAG, "Вимірювання #%lu: Температура=%.2f C, Вологість=%.2f%%, Батарея=%u мВ",
             measurements.sample_sequence,
             measurements.temperature_c,
             measurements.humidity_percent,
             measurements.battery_mv);

    return measurements;
}

std::array<uint8_t, sizeof(SensorPayload)> SensorNode::encode_payload(const SensorMeasurements& data) noexcept {
    SensorPayload payload{};
    payload.sequence_id = data.sample_sequence;
    payload.temp_raw = static_cast<int16_t>(std::round(data.temperature_c * 100.0f));
    payload.hum_raw = static_cast<uint16_t>(std::round(data.humidity_percent * 100.0f));
    payload.vbat_raw = data.battery_mv;
    payload.status_flags = (data.battery_mv < 3000) ? 0x01 : 0x00;

    std::array<uint8_t, sizeof(SensorPayload)> buffer{};
    std::memcpy(buffer.data(), &payload, sizeof(SensorPayload));
    return buffer;
}

} // namespace iot
