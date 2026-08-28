// Ідіоматична C++20 реалізація конвеєра міграцій
#include <cstdint>
#include <string_view>
#include <cstring>
#include <cstdio>
#include <span>
#include <expected>

struct [[gnu::packed]] SchemaV1 {
    char wifi_ssid[32];
    char wifi_pass[32];
    std::uint32_t server_ip_raw;
    std::uint32_t report_interval_s;
};

struct [[gnu::packed]] SchemaV2 {
    char wifi_ssid[32];
    char wifi_pass[32];
    std::uint32_t server_ip_raw;
    std::uint32_t report_interval_s;
    std::uint16_t mqtt_port;
    std::uint8_t  mqtt_qos;
    std::uint8_t  reserved;
};

struct [[gnu::packed]] SchemaV3 {
    char wifi_ssid[32];
    char wifi_pass[32];
    char server_host[64];
    std::uint32_t report_interval_s;
    std::uint16_t mqtt_port;
    std::uint8_t  mqtt_qos;
    std::uint8_t  tls_enable;
};

class SchemaMigrator {
public:
    static SchemaV2 v1_to_v2(const SchemaV1& v1) noexcept {
        SchemaV2 v2{};
        std::memcpy(v2.wifi_ssid, v1.wifi_ssid, sizeof(v2.wifi_ssid));
        std::memcpy(v2.wifi_pass, v1.wifi_pass, sizeof(v2.wifi_pass));
        v2.server_ip_raw = v1.server_ip_raw;
        v2.report_interval_s = v1.report_interval_s;
        v2.mqtt_port = 1883;
        v2.mqtt_qos = 1;
        return v2;
    }

    static SchemaV3 v2_to_v3(const SchemaV2& v2) noexcept {
        SchemaV3 v3{};
        std::memcpy(v3.wifi_ssid, v2.wifi_ssid, sizeof(v3.wifi_ssid));
        std::memcpy(v3.wifi_pass, v2.wifi_pass, sizeof(v3.wifi_pass));
        v3.report_interval_s = v2.report_interval_s;
        v3.mqtt_port = v2.mqtt_port;
        v3.mqtt_qos = v2.mqtt_qos;

        const auto* ip = reinterpret_cast<const std::uint8_t*>(&v2.server_ip_raw);
        std::snprintf(v3.server_host, sizeof(v3.server_host), "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);
        v3.tls_enable = 1;
        return v3;
    }
};
