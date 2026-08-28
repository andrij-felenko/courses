#include <cstdint>
#include <cstring>
#include <span>
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_sleep.h"
#include "esp_now.h"
#include "nvs_flash.h"

namespace field {

constexpr uint8_t WIFI_CHANNEL = 6;
constexpr uint64_t SLEEP_INTERVAL_US = 600ULL * 1000ULL * 1000ULL; /* 10 хв */

struct [[gnu::packed]] TelemetryPayload {
    uint32_t node_id;
    uint32_t message_seq;
    int16_t  temperature_q4;
    uint16_t soil_moisture_raw;
    uint16_t battery_mv;
};

class EspNowSender {
public:
    explicit EspNowSender(std::span<const uint8_t, ESP_NOW_ETH_ALEN> target_mac) noexcept {
        std::memcpy(gateway_mac_, target_mac.data(), ESP_NOW_ETH_ALEN);
    }

    ~EspNowSender() noexcept {
        esp_now_unregister_send_cb();
        esp_now_deinit();
        esp_wifi_stop();
        esp_wifi_deinit();
    }

    bool init() noexcept {
        esp_err_t ret = nvs_flash_init();
        if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
            nvs_flash_erase();
            nvs_flash_init();
        }

        wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
        if (esp_wifi_init(&cfg) != ESP_OK) return false;
        esp_wifi_set_storage(WIFI_STORAGE_RAM);
        esp_wifi_set_mode(WIFI_MODE_STA);
        if (esp_wifi_start() != ESP_OK) return false;

        esp_wifi_set_channel(WIFI_CHANNEL, WIFI_SECOND_CHAN_NONE);
        esp_wifi_set_protocol(WIFI_IF_STA, WIFI_PROTOCOL_11B | WIFI_PROTOCOL_LR);

        if (esp_now_init() != ESP_OK) return false;
        esp_now_register_send_cb(&EspNowSender::on_sent);

        esp_now_peer_info_t peer{};
        std::memcpy(peer.peer_addr, gateway_mac_, ESP_NOW_ETH_ALEN);
        peer.channel = WIFI_CHANNEL;
        peer.ifidx = WIFI_IF_STA;
        peer.encrypt = false;

        return esp_now_add_peer(&peer) == ESP_OK;
    }

    bool send(const TelemetryPayload& payload) noexcept {
        send_completed_ = false;
        send_success_ = false;

        const auto* data_ptr = reinterpret_cast<const uint8_t*>(&payload);
        esp_err_t res = esp_now_send(gateway_mac_, data_ptr, sizeof(TelemetryPayload));
        if (res != ESP_OK) return false;

        int timeout_ms = 15;
        while (!send_completed_ && timeout_ms-- > 0) {
            esp_rom_delay_us(1000);
        }
        return send_success_;
    }

private:
    static void on_sent(const uint8_t*, esp_now_send_status_t status) noexcept {
        send_success_ = (status == ESP_NOW_SEND_SUCCESS);
        send_completed_ = true;
    }

    uint8_t gateway_mac_[ESP_NOW_ETH_ALEN]{};
    static inline volatile bool send_completed_{false};
    static inline volatile bool send_success_{false};
};

} // namespace field

extern "C" void app_main() {
    constexpr uint8_t GATEWAY_MAC[ESP_NOW_ETH_ALEN] = {0x24, 0x6F, 0x28, 0xAA, 0xBB, 0xCC};

    {
        field::EspNowSender sender(GATEWAY_MAC);
        if (sender.init()) {
            const field::TelemetryPayload data{
                .node_id = 0x00010042,
                .message_seq = 104,
                .temperature_q4 = 376,
                .soil_moisture_raw = 1840,
                .battery_mv = 3280
            };
            sender.send(data);
        }
    }

    esp_sleep_enable_timer_wakeup(field::SLEEP_INTERVAL_US);
    esp_deep_sleep_start();
}
