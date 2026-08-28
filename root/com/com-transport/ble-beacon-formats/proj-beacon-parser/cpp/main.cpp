// beacon_parser.hpp / main.cpp — Стандарт C++20
#include <iostream>
#include <iomanip>
#include <vector>
#include <span>
#include <string_view>
#include <string>
#include <array>
#include <variant>
#include <optional>
#include <cmath>
#include <cstdint>
#include <bit>

namespace ble {

struct IBeaconData {
    std::array<uint8_t, 16> uuid;
    uint16_t major;
    uint16_t minor;
};

struct EddystoneUidData {
    std::array<uint8_t, 10> namespace_id;
    std::array<uint8_t, 6>  instance_id;
};

struct EddystoneUrlData {
    std::string url;
};

struct EddystoneTlmData {
    uint16_t battery_mv;
    float    temperature_c;
    uint32_t adv_count;
    uint32_t uptime_sec;
};

struct AltBeaconData {
    uint16_t manufacturer_id;
    std::array<uint8_t, 20> beacon_id;
};

using BeaconPayload = std::variant<
    std::monostate,
    IBeaconData,
    EddystoneUidData,
    EddystoneUrlData,
    EddystoneTlmData,
    AltBeaconData
>;

struct BeaconFrame {
    int8_t calibrated_power_1m{ -59 };
    BeaconPayload payload{};

    [[nodiscard]] bool isValid() const noexcept {
        return !std::holds_alternative<std::monostate>(payload);
    }
};

class KalmanRssiFilter {
public:
    constexpr explicit KalmanRssiFilter(float process_noise = 0.05f, float measurement_noise = 4.0f) noexcept
        : q_{ process_noise }, r_{ measurement_noise } {}

    [[nodiscard]] float update(float measurement) noexcept {
        if (!initialized_) {
            x_ = measurement;
            p_ = 5.0f;
            initialized_ = true;
            return x_;
        }
        // Прогноз
        const float p_pred = p_ + q_;
        // Оновлення
        const float k = p_pred / (p_pred + r_);
        x_ += k * (measurement - x_);
        p_ = (1.0f - k) * p_pred;
        return x_;
    }

    [[nodiscard]] float state() const noexcept { return x_; }
    [[nodiscard]] bool isInitialized() const noexcept { return initialized_; }

private:
    float x_{ 0.0f };
    float p_{ 5.0f };
    float q_{ 0.05f };
    float r_{ 4.0f };
    bool  initialized_{ false };
};

[[nodiscard]] inline float calculateDistance(int8_t tx_power_1m, float rssi, float n = 2.0f) noexcept {
    if (n <= 0.0f) n = 2.0f;
    return std::pow(10.0f, (static_cast<float>(tx_power_1m) - rssi) / (10.0f * n));
}

namespace detail {
    [[nodiscard]] inline uint16_t readBe16(std::span<const uint8_t, 2> s) noexcept {
        return static_cast<uint16_t>((s[0] << 8) | s[1]);
    }

    [[nodiscard]] inline uint32_t readBe32(std::span<const uint8_t, 4> s) noexcept {
        return (static_cast<uint32_t>(s[0]) << 24) |
               (static_cast<uint32_t>(s[1]) << 16) |
               (static_cast<uint32_t>(s[2]) << 8)  |
                static_cast<uint32_t>(s[3]);
    }

    inline std::string decodeEddystoneUrl(std::span<const uint8_t> payload) {
        if (payload.empty()) return {};

        static constexpr std::string_view prefixes[] = {
            "http://www.", "https://www.", "http://", "https://"
        };
        static constexpr std::string_view suffixes[] = {
            ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",
            ".com",  ".org",  ".edu",  ".net",  ".info",  ".biz",  ".gov"
        };

        std::string result;
        const uint8_t scheme = payload[0];
        if (scheme < std::size(prefixes)) {
            result += prefixes[scheme];
        }

        for (size_t i = 1; i < payload.size(); ++i) {
            const uint8_t b = payload[i];
            if (b < std::size(suffixes)) {
                result += suffixes[b];
            } else if (b >= 32 && b <= 126) {
                result.push_back(static_cast<char>(b));
            }
        }
        return result;
    }
} // namespace detail

class BeaconParser {
public:
    [[nodiscard]] static std::optional<BeaconFrame> parse(std::span<const uint8_t> packet) {
        size_t offset = 0;
        while (offset < packet.size()) {
            const uint8_t ad_len = packet[offset];
            if (ad_len == 0 || offset + 1 + ad_len > packet.size()) break;

            const uint8_t ad_type = packet[offset + 1];
            const auto ad_data = packet.subspan(offset + 2, ad_len - 1);

            // Manufacturer Specific Data (0xFF)
            if (ad_type == 0xFF && ad_data.size() >= 25) {
                const uint16_t company = static_cast<uint16_t>(ad_data[0] | (ad_data[1] << 8));

                // Apple iBeacon (Company = 0x004C, Type = 0x02, Subtype Len = 0x15)
                if (company == 0x004C && ad_data[2] == 0x02 && ad_data[3] == 0x15 && ad_data.size() >= 25) {
                    BeaconFrame frame{};
                    IBeaconData ib{};
                    std::copy_n(ad_data.subspan(4, 16).begin(), 16, ib.uuid.begin());
                    ib.major = detail::readBe16(ad_data.subspan<20, 2>());
                    ib.minor = detail::readBe16(ad_data.subspan<22, 2>());
                    frame.calibrated_power_1m = static_cast<int8_t>(ad_data[24]);
                    frame.payload = ib;
                    return frame;
                }

                // AltBeacon (Beacon Code = 0xBEAC)
                if (ad_data.size() >= 26 && ad_data[2] == 0xBE && ad_data[3] == 0xAC) {
                    BeaconFrame frame{};
                    AltBeaconData ab{};
                    ab.manufacturer_id = company;
                    std::copy_n(ad_data.subspan(4, 20).begin(), 20, ab.beacon_id.begin());
                    frame.calibrated_power_1m = static_cast<int8_t>(ad_data[24]);
                    frame.payload = ab;
                    return frame;
                }
            }

            // Service Data (0x16) для Google Eddystone (0xFEAA)
            if (ad_type == 0x16 && ad_data.size() >= 3) {
                const uint16_t uuid = static_cast<uint16_t>(ad_data[0] | (ad_data[1] << 8));
                if (uuid == 0xFEAA) {
                    const uint8_t frame_type = ad_data[2];
                    if (frame_type == 0x00 && ad_data.size() >= 18) { // UID
                        BeaconFrame frame{};
                        EddystoneUidData uid{};
                        frame.calibrated_power_1m = static_cast<int8_t>(static_cast<int8_t>(ad_data[3]) - 41);
                        std::copy_n(ad_data.subspan(4, 10).begin(), 10, uid.namespace_id.begin());
                        std::copy_n(ad_data.subspan(14, 6).begin(), 6, uid.instance_id.begin());
                        frame.payload = uid;
                        return frame;
                    }
                    if (frame_type == 0x10 && ad_data.size() >= 4) { // URL
                        BeaconFrame frame{};
                        frame.calibrated_power_1m = static_cast<int8_t>(static_cast<int8_t>(ad_data[3]) - 41);
                        frame.payload = EddystoneUrlData{ detail::decodeEddystoneUrl(ad_data.subspan(4)) };
                        return frame;
                    }
                    if (frame_type == 0x20 && ad_data.size() >= 14) { // TLM
                        BeaconFrame frame{};
                        frame.calibrated_power_1m = -59;
                        const auto raw_temp = static_cast<int16_t>(detail::readBe16(ad_data.subspan<5, 2>()));
                        frame.payload = EddystoneTlmData{
                            .battery_mv = detail::readBe16(ad_data.subspan<3, 2>()),
                            .temperature_c = static_cast<float>(raw_temp) / 256.0f,
                            .adv_count = detail::readBe32(ad_data.subspan<7, 4>()),
                            .uptime_sec = detail::readBe32(ad_data.subspan<11, 4>()) / 10
                        };
                        return frame;
                    }
                }
            }

            offset += 1 + ad_len;
        }

        return std::nullopt;
    }
};

} // namespace ble

int main() {
    // Тестовий пакет Google Eddystone-URL
    const std::vector<uint8_t> raw_eddystone_url = {
        0x02, 0x01, 0x06,                         // Flags
        0x03, 0x03, 0xAA, 0xFE,                   // Complete 16-bit Service UUID
        0x0E, 0x16, 0xAA, 0xFE,                   // Service Data Header
        0x10, 0xEE,                               // Frame: URL, TxPower@0m = -18 dBm
        0x01,                                     // Scheme: https://www.
        'e', 'x', 'a', 'm', 'p', 'l', 'e', 0x00   // "example" + ".com/"
    };

    if (auto frame = ble::BeaconParser::parse(raw_eddystone_url)) {
        if (const auto* url_data = std::get_if<ble::EddystoneUrlData>(&frame->payload)) {
            std::cout << "Розпізнано Eddystone-URL!\n";
            std::cout << "Адреса: " << url_data->url << "\n";
            std::cout << "Опорна потужність @1m: " << static_cast<int>(frame->calibrated_power_1m) << " дБм\n";
        }
    }

    ble::KalmanRssiFilter filter(0.05f, 4.0f);
    const std::vector<float> measurements = { -68.0f, -72.0f, -69.0f, -85.0f, -70.0f, -71.0f };

    std::cout << "\nФільтрація сигналу Калманом у C++20:\n";
    for (size_t i = 0; i < measurements.size(); ++i) {
        const float raw = measurements[i];
        const float smoothed = filter.update(raw);
        const float dist_raw = ble::calculateDistance(-59, raw, 2.0f);
        const float dist_smooth = ble::calculateDistance(-59, smoothed, 2.0f);

        std::cout << "[" << i + 1 << "] Raw: " << std::setw(5) << raw << " dBm ("
                  << dist_raw << " м) -> Kalman: " << std::setw(5) << smoothed
                  << " dBm (" << dist_smooth << " м)\n";
    }

    return 0;
}
