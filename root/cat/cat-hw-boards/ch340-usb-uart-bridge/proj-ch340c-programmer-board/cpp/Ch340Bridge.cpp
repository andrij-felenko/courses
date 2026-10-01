#include "Ch340Bridge.hpp"

#if defined(ESP_PLATFORM)
#include "driver/uart.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"
static const char* TAG = "CH340_BRIDGE";
#elif defined(ARDUINO)
#include <Arduino.h>
#else
#include <chrono>
#include <algorithm>
#endif

namespace ch340 {

Ch340Bridge::Ch340Bridge(const UartConfig& uart_cfg, const IndicatorConfig& ind_cfg)
    : uart_cfg_(uart_cfg), ind_cfg_(ind_cfg) {}

Ch340Bridge::~Ch340Bridge() {
    if (!initialized_) return;

#if defined(ESP_PLATFORM)
    uart_driver_delete(static_cast<uart_port_t>(uart_cfg_.uart_port));
#elif defined(ARDUINO)
    // Arduino HardwareSerial не потребує явного видалення
#endif
}

Ch340Bridge::Ch340Bridge(Ch340Bridge&& other) noexcept
    : uart_cfg_(other.uart_cfg_),
      ind_cfg_(other.ind_cfg_),
      state_(other.state_),
      last_activity_timestamp_(other.last_activity_timestamp_),
      total_bytes_processed_(other.total_bytes_processed_),
      initialized_(other.initialized_) {
    other.initialized_ = false;
    other.state_ = ConnectionState::IDLE;
}

Ch340Bridge& Ch340Bridge::operator=(Ch340Bridge&& other) noexcept {
    if (this != &other) {
        if (initialized_) {
#if defined(ESP_PLATFORM)
            uart_driver_delete(static_cast<uart_port_t>(uart_cfg_.uart_port));
#endif
        }
        uart_cfg_ = other.uart_cfg_;
        ind_cfg_ = other.ind_cfg_;
        state_ = other.state_;
        last_activity_timestamp_ = other.last_activity_timestamp_;
        total_bytes_processed_ = other.total_bytes_processed_;
        initialized_ = other.initialized_;

        other.initialized_ = false;
        other.state_ = ConnectionState::IDLE;
    }
    return *this;
}

uint32_t Ch340Bridge::getCurrentMillis() const noexcept {
#if defined(ESP_PLATFORM)
    return static_cast<uint32_t>(esp_timer_get_time() / 1000ULL);
#elif defined(ARDUINO)
    return millis();
#else
    using namespace std::chrono;
    return static_cast<uint32_t>(duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count());
#endif
}

void Ch340Bridge::setLedState(bool turn_on) {
    bool physical_level = ind_cfg_.active_high ? turn_on : !turn_on;

#if defined(ESP_PLATFORM)
    gpio_set_level(static_cast<gpio_num_t>(ind_cfg_.led_pin), physical_level ? 1 : 0);
#elif defined(ARDUINO)
    digitalWrite(ind_cfg_.led_pin, physical_level ? HIGH : LOW);
#else
    (void)physical_level;
#endif
}

bool Ch340Bridge::begin() {
    // 1. Налаштування GPIO для світлодіода індикатора
#if defined(ESP_PLATFORM)
    gpio_config_t io_conf{};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pin_bit_mask = (1ULL << ind_cfg_.led_pin);
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    if (gpio_config(&io_conf) != ESP_OK) {
        state_ = ConnectionState::ERROR;
        return false;
    }
#elif defined(ARDUINO)
    pinMode(ind_cfg_.led_pin, OUTPUT);
#endif

    setLedState(false);

    // 2. Ініціалізація периферії UART під конкретну платформу
#if defined(ESP_PLATFORM)
    uart_config_t u_config{};
    u_config.baud_rate = static_cast<int>(uart_cfg_.baud_rate);
    u_config.data_bits = UART_DATA_8_BITS;
    u_config.parity    = UART_PARITY_DISABLE;
    u_config.stop_bits   = UART_STOP_BITS_1;
    u_config.flow_ctrl  = UART_HW_FLOWCTRL_DISABLE;
    u_config.source_clk = UART_SCLK_DEFAULT;

    auto port = static_cast<uart_port_t>(uart_cfg_.uart_port);
    if (uart_param_config(port, &u_config) != ESP_OK) {
        state_ = ConnectionState::ERROR;
        return false;
    }

    if (uart_set_pin(port, uart_cfg_.tx_pin, uart_cfg_.rx_pin, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE) != ESP_OK) {
        state_ = ConnectionState::ERROR;
        return false;
    }

    if (uart_driver_install(port, uart_cfg_.rx_buffer_size, uart_cfg_.tx_buffer_size, 0, nullptr, 0) != ESP_OK) {
        state_ = ConnectionState::ERROR;
        return false;
    }
#elif defined(ARDUINO)
    if (uart_cfg_.uart_port == 0) {
        Serial.begin(uart_cfg_.baud_rate);
    } else {
#if defined(ESP32)
        Serial1.begin(uart_cfg_.baud_rate, SERIAL_8N1, uart_cfg_.rx_pin, uart_cfg_.tx_pin);
#else
        Serial.begin(uart_cfg_.baud_rate);
#endif
    }
#endif

    initialized_ = true;
    state_ = ConnectionState::IDLE;
    return true;
}

std::size_t Ch340Bridge::processEcho() {
    if (!initialized_) {
        state_ = ConnectionState::ERROR;
        return 0;
    }

    std::size_t bytes_read = 0;

#if defined(ESP_PLATFORM)
    auto port = static_cast<uart_port_t>(uart_cfg_.uart_port);
    int read_res = uart_read_bytes(port, rx_chunk_buffer_.data(), rx_chunk_buffer_.size(), 0);
    if (read_res > 0) {
        bytes_read = static_cast<std::size_t>(read_res);
        uart_write_bytes(port, reinterpret_cast<const char*>(rx_chunk_buffer_.data()), bytes_read);
    }
#elif defined(ARDUINO)
    Stream* serial_ptr = &Serial;
    if (uart_cfg_.uart_port != 0) {
#if defined(ESP32)
        serial_ptr = &Serial1;
#endif
    }

    int available = serial_ptr->available();
    if (available > 0) {
        std::size_t to_read = std::min(static_cast<std::size_t>(available), rx_chunk_buffer_.size());
        bytes_read = serial_ptr->readBytes(reinterpret_cast<char*>(rx_chunk_buffer_.data()), to_read);
        if (bytes_read > 0) {
            serial_ptr->write(rx_chunk_buffer_.data(), bytes_read);
        }
    }
#else
    // Заглушка імітації для настільного тестування (без апаратури CH340)
    bytes_read = 0;
#endif

    if (bytes_read > 0) {
        total_bytes_processed_ += bytes_read;
        last_activity_timestamp_ = getCurrentMillis();
        state_ = ConnectionState::ACTIVE;
        setLedState(true);
    }

    return bytes_read;
}

void Ch340Bridge::update() {
    if (!initialized_) return;

    // Виконуємо прийом та автоматичне повернення ехо-байтів
    std::size_t echoed = processEcho();
    (void)echoed;

    // Оновлення індикатора стану згасання після простою
    uint32_t now = getCurrentMillis();
    if (state_ == ConnectionState::ACTIVE) {
        if (now - last_activity_timestamp_ >= ind_cfg_.activity_timeout_ms) {
            state_ = ConnectionState::IDLE;
            setLedState(false);
        }
    }
}

} // namespace ch340
