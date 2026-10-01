#pragma once

#include <string>
#include <string_view>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_log.h"

namespace esp32_zero {

// Стан підключення до Wi-Fi мережі
enum class WifiState : uint8_t {
    Disconnected,
    Connecting,
    Connected,
    Failed
};

// Менеджер бездротового підключення ESP32
class WifiManager {
public:
    WifiManager() = default;

    ~WifiManager() {
        deinit();
    }

    WifiManager(const WifiManager&) = delete;
    WifiManager& operator=(const WifiManager&) = delete;

    // Ініціалізація та конфігурація Wi-Fi у режимі станції (STA)
    bool begin(std::string_view ssid, std::string_view password) {
        if (initialized_) return true;

        esp_err_t ret = esp_netif_init();
        if (ret != ESP_OK && ret != ESP_ERR_INVALID_STATE) {
            return false;
        }

        ret = esp_event_loop_create_default();
        if (ret != ESP_OK && ret != ESP_ERR_INVALID_STATE) {
            return false;
        }

        netif_ = esp_netif_create_default_wifi_sta();
        if (!netif_) return false;

        wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
        if (esp_wifi_init(&cfg) != ESP_OK) return false;

        // Реєстрація обробника системних подій Wi-Fi та IP
        esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID,
                                            &WifiManager::eventHandler, this, &instance_any_id_);
        esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP,
                                            &WifiManager::eventHandler, this, &instance_got_ip_);

        wifi_config_t wifi_config = {};
        ::strncpy(reinterpret_cast<char*>(wifi_config.sta.ssid), ssid.data(), sizeof(wifi_config.sta.ssid) - 1);
        ::strncpy(reinterpret_cast<char*>(wifi_config.sta.password), password.data(), sizeof(wifi_config.sta.password) - 1);
        wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;

        if (esp_wifi_set_mode(WIFI_MODE_STA) != ESP_OK) return false;
        if (esp_wifi_set_config(WIFI_IF_STA, &wifi_config) != ESP_OK) return false;
        if (esp_wifi_start() != ESP_OK) return false;

        initialized_ = true;
        state_ = WifiState::Connecting;
        return true;
    }

    // Ручний виклик повторного підключення
    bool connect() {
        if (!initialized_) return false;
        retry_count_ = 0;
        state_ = WifiState::Connecting;
        return esp_wifi_connect() == ESP_OK;
    }

    // Відключення від бездротової мережі
    void disconnect() {
        if (initialized_) {
            esp_wifi_disconnect();
            state_ = WifiState::Disconnected;
        }
    }

    [[nodiscard]] WifiState getState() const noexcept { return state_; }
    [[nodiscard]] bool isConnected() const noexcept { return state_ == WifiState::Connected; }

    // Отримання призначеної IP-адреси у вигляді рядка
    [[nodiscard]] std::string getIpAddress() const {
        if (state_ != WifiState::Connected) return "0.0.0.0";
        char ip_str[16]{0};
        snprintf(ip_str, sizeof(ip_str), IPSTR, IP2STR(&ip_info_.ip));
        return std::string(ip_str);
    }

private:
    static void eventHandler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data) {
        auto* self = static_cast<WifiManager*>(arg);
        if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
            esp_wifi_connect();
        } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
            if (self->retry_count_ < max_retries_) {
                esp_wifi_connect();
                self->retry_count_++;
                self->state_ = WifiState::Connecting;
            } else {
                self->state_ = WifiState::Failed;
            }
        } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
            auto* event = static_cast<ip_event_got_ip_t*>(event_data);
            self->ip_info_ = event->ip_info;
            self->retry_count_ = 0;
            self->state_ = WifiState::Connected;
        }
    }

    void deinit() {
        if (initialized_) {
            esp_wifi_stop();
            esp_wifi_deinit();
            if (instance_any_id_) esp_event_handler_instance_unregister(WIFI_EVENT, ESP_EVENT_ANY_ID, instance_any_id_);
            if (instance_got_ip_) esp_event_handler_instance_unregister(IP_EVENT, IP_EVENT_STA_GOT_IP, instance_got_ip_);
            initialized_ = false;
            state_ = WifiState::Disconnected;
        }
    }

    esp_netif_t* netif_{nullptr};
    esp_event_handler_instance_t instance_any_id_{nullptr};
    esp_event_handler_instance_t instance_got_ip_{nullptr};
    esp_netif_ip_info_t ip_info_{};
    WifiState state_{WifiState::Disconnected};
    uint8_t retry_count_{0};
    static constexpr uint8_t max_retries_{5};
    bool initialized_{false};
};

} // namespace esp32_zero
