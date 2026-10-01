#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include "freertos/FreeRTOS.h"
#include "driver/usb_serial_jtag.h"
#include "esp_err.h"

namespace esp32_zero {

// C++ RAII-обгортка для асинхронного потокового обміну даними через USB CDC / Serial JTAG
class UsbCdcStream {
public:
    explicit UsbCdcStream(size_t rx_buffer_size = 1024, size_t tx_buffer_size = 1024) noexcept
        : rx_buf_size_(rx_buffer_size), tx_buf_size_(tx_buffer_size) {}

    ~UsbCdcStream() {
        deinit();
    }

    // Семантика переміщення для передачі володіння периферією
    UsbCdcStream(const UsbCdcStream&) = delete;
    UsbCdcStream& operator=(const UsbCdcStream&) = delete;

    UsbCdcStream(UsbCdcStream&& other) noexcept
        : rx_buf_size_(other.rx_buf_size_),
          tx_buf_size_(other.tx_buf_size_),
          initialized_(other.initialized_) {
        other.initialized_ = false;
    }

    UsbCdcStream& operator=(UsbCdcStream&& other) noexcept {
        if (this != &other) {
            deinit();
            rx_buf_size_ = other.rx_buf_size_;
            tx_buf_size_ = other.tx_buf_size_;
            initialized_ = other.initialized_;
            other.initialized_ = false;
        }
        return *this;
    }

    // Ініціалізація драйвера USB Serial JTAG
    bool begin() {
        if (initialized_) return true;

        usb_serial_jtag_driver_config_t config = {
            .rx_buffer_size = rx_buf_size_,
            .tx_buffer_size = tx_buf_size_
        };

        esp_err_t err = usb_serial_jtag_driver_install(&config);
        if (err == ESP_OK) {
            initialized_ = true;
            return true;
        }
        return false;
    }

    // Неблокувальне читання даних у наданий span буфера
    size_t read(std::span<uint8_t> buffer, uint32_t timeout_ticks = 0) {
        if (!initialized_ || buffer.empty()) return 0;

        int bytes_read = usb_serial_jtag_read_bytes(buffer.data(), buffer.size(), timeout_ticks);
        return (bytes_read > 0) ? static_cast<size_t>(bytes_read) : 0;
    }

    // Запис бінарних даних із span
    size_t write(std::span<const uint8_t> data, uint32_t timeout_ticks = pdMS_TO_TICKS(50)) {
        if (!initialized_ || data.empty()) return 0;

        int bytes_sent = usb_serial_jtag_write_bytes(data.data(), data.size(), timeout_ticks);
        return (bytes_sent > 0) ? static_cast<size_t>(bytes_sent) : 0;
    }

    // Запис текстового рядка через string_view
    size_t write(std::string_view text, uint32_t timeout_ticks = pdMS_TO_TICKS(50)) {
        auto bytes_span = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(text.data()), text.size());
        return write(bytes_span, timeout_ticks);
    }

    // Очікування завершення передачі вихідних даних
    bool flush(uint32_t timeout_ticks = pdMS_TO_TICKS(100)) {
        if (!initialized_) return false;
        return usb_serial_jtag_wait_tx_done(timeout_ticks) == ESP_OK;
    }

    // Перевірка активного підключення хоста USB
    [[nodiscard]] bool isConnected() const noexcept {
        return initialized_ && usb_serial_jtag_is_connected();
    }

private:
    void deinit() {
        if (initialized_) {
            usb_serial_jtag_driver_uninstall();
            initialized_ = false;
        }
    }

    size_t rx_buf_size_{1024};
    size_t tx_buf_size_{1024};
    bool initialized_{false};
};

} // namespace esp32_zero
