#pragma once

#include <string_view>
#include <string>
#include <array>
#include <span>
#include "UsbCdcStream.hpp"
#include "RmtLedController.hpp"
#include "WifiManager.hpp"
#include "esp_timer.h"

namespace esp32_zero {

// Головний клас-оркестратор пристрою у форматі USB-донгла
class UsbDongle {
public:
    UsbDongle() = default;
    ~UsbDongle() = default;

    // Заборона копіювання екземпляра пристрою
    UsbDongle(const UsbDongle&) = delete;
    UsbDongle& operator=(const UsbDongle&) = delete;

    // Ініціалізація всіх периферійних модулів пристрою
    bool begin(std::string_view wifi_ssid, std::string_view wifi_password) {
        // 1. Ініціалізація світлодіодної індикації станів на RMT
        if (!led_controller_.begin()) {
            return false;
        }
        led_controller_.setStatus(DongleStatus::Initializing);

        // 2. Ініціалізація потоку USB CDC через вбудований Type-C
        if (!usb_stream_.begin()) {
            led_controller_.setStatus(DongleStatus::Error);
            return false;
        }

        // 3. Запуск бездротового менеджера та з'єднання з Wi-Fi
        led_controller_.setStatus(DongleStatus::WifiConnecting);
        if (!wifi_manager_.begin(wifi_ssid, wifi_password)) {
            led_controller_.setStatus(DongleStatus::Error);
            return false;
        }

        usb_stream_.write("[USB-Dongle] Система ініціалізована. Підключення до Wi-Fi...\r\n");
        return true;
    }

    // Неблокувальне оновлення стану та обробка асинхронних подій
    void update() {
        const uint32_t now_ms = static_cast<uint32_t>(esp_timer_get_time() / 1000);

        // Оновлення статусу Wi-Fi з'єднання
        updateNetworkState();

        // Фонове оновлення асинхронного світлодіодного індикатора
        led_controller_.update(now_ms);

        // Прийом та обробка вхідних команд через USB CDC потік
        processUsbCommands(now_ms);
    }

private:
    void updateNetworkState() {
        WifiState wifi_state = wifi_manager_.getState();

        if (wifi_state == WifiState::Connected && !was_wifi_connected_) {
            was_wifi_connected_ = true;
            led_controller_.setStatus(DongleStatus::WifiConnected);

            std::string msg = "[USB-Dongle] З'єднання встановлено! IP: " + wifi_manager_.getIpAddress() + "\r\n";
            usb_stream_.write(msg);
        } else if (wifi_state == WifiState::Failed && was_wifi_connected_) {
            was_wifi_connected_ = false;
            led_controller_.setStatus(DongleStatus::Error);
            usb_stream_.write("[USB-Dongle] Помилка мережі: з'єднання втрачено.\r\n");
        }
    }

    void processUsbCommands(uint32_t now_ms) {
        std::array<uint8_t, 128> rx_buf{};
        size_t read_bytes = usb_stream_.read(std::span(rx_buf));

        if (read_bytes > 0) {
            // Індикація фонової активності передачі даних через USB
            led_controller_.setStatus(DongleStatus::DataTransferring);
            last_transfer_ms_ = now_ms;

            std::string_view command(reinterpret_cast<const char*>(rx_buf.data()), read_bytes);

            // Розбір простих текстових команд з USB CDC
            if (command.find("status") != std::string_view::npos) {
                std::string status_resp = "[STATUS] Wi-Fi IP: " + wifi_manager_.getIpAddress() + "\r\n";
                usb_stream_.write(status_resp);
            } else if (command.find("ping") != std::string_view::npos) {
                usb_stream_.write("[PONG] ESP32-S3-Zero активний\r\n");
            } else {
                // Ехо-відповідь для невизначених вхідних даних
                usb_stream_.write("[ECHO] ");
                usb_stream_.write(std::span<const uint8_t>(rx_buf.data(), read_bytes));
                usb_stream_.write("\r\n");
            }
        } else if (led_controller_.getStatus() == DongleStatus::DataTransferring) {
            // Повернення до індикації стану Wi-Fi після паузи обміну
            if (now_ms - last_transfer_ms_ > 500) {
                if (wifi_manager_.isConnected()) {
                    led_controller_.setStatus(DongleStatus::WifiConnected);
                } else {
                    led_controller_.setStatus(DongleStatus::WifiConnecting);
                }
            }
        }
    }

    UsbCdcStream usb_stream_{};
    RmtLedController led_controller_{GPIO_NUM_21};
    WifiManager wifi_manager_{};
    bool was_wifi_connected_{false};
    uint32_t last_transfer_ms_{0};
};

} // namespace esp32_zero
