#include <cstdint>
#include <cstring>
#include <array>
#include <span>
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_sleep.h"
#include "esp_netif.h"
#include "nvs_flash.h"
#include "lwip/sockets.h"

namespace field {

constexpr char SSID[] = "Farm_Field_Mesh";
constexpr char PASSWORD[] = "FieldSecureKey2026";
constexpr uint64_t SLEEP_INTERVAL_US = 300ULL * 1000ULL * 1000ULL; /* 5 хв */

struct RtcWifiContext {
    uint32_t crc32{0};
    std::array<uint8_t, 6> bssid{};
    uint8_t channel{0};
    bool valid{false};
    esp_netif_ip_info_t ip_info{};

    [[nodiscard]] uint32_t compute_crc() const noexcept {
        const auto* data = reinterpret_cast<const uint8_t*>(&bssid);
        const size_t len = sizeof(RtcWifiContext) - offsetof(RtcWifiContext, bssid);
        uint32_t crc = 0xFFFFFFFF;
        for (size_t i = 0; i < len; ++i) {
            crc ^= data[i];
            for (int j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
            }
        }
        return ~crc;
    }
};

RTC_DATA_ATTR static RtcWifiContext s_rtc_context;

class FastConnectManager {
public:
    FastConnectManager() noexcept = default;

    ~FastConnectManager() noexcept {
        esp_wifi_stop();
        esp_wifi_deinit();
    }

    bool initialize_and_connect() noexcept {
        esp_err_t ret = nvs_flash_init();
        if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
            nvs_flash_erase();
            nvs_flash_init();
        }

        esp_netif_init();
        esp_event_loop_create_default();
        sta_netif_ = esp_netif_create_default_wifi_sta();

        wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
        if (esp_wifi_init(&cfg) != ESP_OK) return false;
        esp_wifi_set_storage(WIFI_STORAGE_RAM);
        esp_wifi_set_mode(WIFI_MODE_STA);

        wifi_config_t wifi_cfg{};
        std::strncpy(reinterpret_cast<char*>(wifi_cfg.sta.ssid), SSID, sizeof(wifi_cfg.sta.ssid));
        std::strncpy(reinterpret_cast<char*>(wifi_cfg.sta.password), PASSWORD, sizeof(wifi_cfg.sta.password));

        if (esp_reset_reason() == ESP_RST_DEEPSLEEP && s_rtc_context.valid) {
            if (s_rtc_context.compute_crc() == s_rtc_context.crc32) {
                wifi_cfg.sta.channel = s_rtc_context.channel;
                std::memcpy(wifi_cfg.sta.bssid, s_rtc_context.bssid.data(), 6);
                wifi_cfg.sta.bssid_set = 1;

                esp_netif_dhcpc_stop(sta_netif_);
                esp_netif_set_ip_info(sta_netif_, &s_rtc_context.ip_info);
                is_fast_connect_ = true;
            }
        }

        esp_wifi_set_config(WIFI_IF_STA, &wifi_cfg);
        esp_wifi_start();
        esp_wifi_connect();

        return wait_connection();
    }

    bool send_udp_telemetry(const char* dest_ip, uint16_t port, std::string_view payload) noexcept {
        int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
        if (sock < 0) return false;

        sockaddr_in dest_addr{};
        dest_addr.sin_addr.s_addr = inet_addr(dest_ip);
        dest_addr.sin_family = AF_INET;
        dest_addr.sin_port = htons(port);

        ssize_t sent = sendto(sock, payload.data(), payload.size(), 0,
                              reinterpret_cast<sockaddr*>(&dest_addr), sizeof(dest_addr));
        close(sock);
        return sent == static_cast<ssize_t>(payload.size());
    }

private:
    bool wait_connection() noexcept {
        wifi_ap_record_t ap_info{};
        int wait_cycles = is_fast_connect_ ? 10 : 40;

        while (wait_cycles-- > 0) {
            if (esp_wifi_sta_get_ap_info(&ap_info) == ESP_OK) {
                if (!is_fast_connect_) {
                    s_rtc_context.channel = ap_info.primary;
                    std::memcpy(s_rtc_context.bssid.data(), ap_info.bssid, 6);
                    esp_netif_get_ip_info(sta_netif_, &s_rtc_context.ip_info);
                    s_rtc_context.valid = true;
                    s_rtc_context.crc32 = s_rtc_context.compute_crc();
                }
                return true;
            }
            vTaskDelay(pdMS_TO_TICKS(10));
        }
        return false;
    }

    esp_netif_t* sta_netif_{nullptr};
    bool is_fast_connect_{false};
};

} // namespace field

extern "C" void app_main() {
    {
        field::FastConnectManager manager;
        if (manager.initialize_and_connect()) {
            manager.send_udp_telemetry("192.168.1.1", 5005, "{\"node\":104,\"v_bat\":3.28,\"temp\":23.5}");
        }
    }

    esp_sleep_enable_timer_wakeup(field::SLEEP_INTERVAL_US);
    esp_deep_sleep_start();
}
