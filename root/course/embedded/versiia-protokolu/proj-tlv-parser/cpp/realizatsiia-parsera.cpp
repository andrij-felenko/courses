#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <string_view>
#include <optional>
#include <expected>
#include <array>
#include <string>

enum class TlvTag : uint8_t {
    VoltageMv     = 0x01,
    CurrentMa     = 0x02,
    Temperature   = 0x03,
    DeviceName    = 0x04,
    NetworkConfig = 0x05
};

enum class TlvSubTag : uint8_t {
    IpAddress = 0x10,
    Port      = 0x11
};

enum class TlvError {
    BufferOverrun,
    InvalidLength,
    TruncatedPayload,
    NestedInvalid
};

struct NetworkConfig {
    std::optional<uint32_t> ip_address;
    std::optional<uint16_t> port;
};

struct TelemetryData {
    std::optional<uint16_t> voltage_mv;
    std::optional<int32_t>  current_ma;
    std::optional<int16_t>  temperature_c_x100;
    std::string             device_name;
    NetworkConfig           net_cfg;
    uint16_t                unknown_tags_count{0};
};

class TlvStreamParser {
private:
    static std::expected<NetworkConfig, TlvError> 
    parse_nested_net_cfg(std::span<const uint8_t> payload) {
        NetworkConfig net;
        size_t cursor = 0;

        while (cursor < payload.size()) {
            if (cursor + 2 > payload.size()) {
                return std::unexpected(TlvError::TruncatedPayload);
            }

            const uint8_t tag = payload[cursor];
            const uint8_t len = payload[cursor + 1];
            cursor += 2;

            if (len > payload.size() - cursor) {
                return std::unexpected(TlvError::InvalidLength);
            }

            auto val_span = payload.subspan(cursor, len);
            cursor += len;

            switch (static_cast<TlvSubTag>(tag)) {
                case TlvSubTag::IpAddress:
                    if (val_span.size() == sizeof(uint32_t)) {
                        uint32_t ip = static_cast<uint32_t>(val_span[0]) |
                                      (static_cast<uint32_t>(val_span[1]) << 8) |
                                      (static_cast<uint32_t>(val_span[2]) << 16) |
                                      (static_cast<uint32_t>(val_span[3]) << 24);
                        net.ip_address = ip;
                    }
                    break;

                case TlvSubTag::Port:
                    if (val_span.size() == sizeof(uint16_t)) {
                        net.port = static_cast<uint16_t>(val_span[0] | (val_span[1] << 8));
                    }
                    break;

                default:
                    // Пропуск невідомого підтегу
                    break;
            }
        }

        return net;
    }

public:
    static std::expected<TelemetryData, TlvError> parse(std::span<const uint8_t> payload) {
        TelemetryData result;
        size_t cursor = 0;

        while (cursor < payload.size()) {
            if (cursor + 2 > payload.size()) {
                return std::unexpected(TlvError::TruncatedPayload);
            }

            const uint8_t tag = payload[cursor];
            const uint8_t len = payload[cursor + 1];
            cursor += 2;

            if (len > payload.size() - cursor) {
                return std::unexpected(TlvError::InvalidLength);
            }

            auto val_span = payload.subspan(cursor, len);
            cursor += len;

            switch (static_cast<TlvTag>(tag)) {
                case TlvTag::VoltageMv:
                    if (val_span.size() == sizeof(uint16_t)) {
                        result.voltage_mv = static_cast<uint16_t>(val_span[0] | (val_span[1] << 8));
                    }
                    break;

                case TlvTag::CurrentMa:
                    if (val_span.size() == sizeof(int32_t)) {
                        uint32_t raw = static_cast<uint32_t>(val_span[0]) |
                                       (static_cast<uint32_t>(val_span[1]) << 8) |
                                       (static_cast<uint32_t>(val_span[2]) << 16) |
                                       (static_cast<uint32_t>(val_span[3]) << 24);
                        result.current_ma = static_cast<int32_t>(raw);
                    }
                    break;

                case TlvTag::Temperature:
                    if (val_span.size() == sizeof(int16_t)) {
                        uint16_t raw = static_cast<uint16_t>(val_span[0] | (val_span[1] << 8));
                        result.temperature_c_x100 = static_cast<int16_t>(raw);
                    }
                    break;

                case TlvTag::DeviceName:
                    if (!val_span.empty() && val_span.size() <= 32) {
                        result.device_name = std::string(
                            reinterpret_cast<const char*>(val_span.data()), 
                            val_span.size()
                        );
                    }
                    break;

                case TlvTag::NetworkConfig:
                    if (auto net_res = parse_nested_net_cfg(val_span); net_res.has_value()) {
                        result.net_cfg = *net_res;
                    }
                    break;

                default:
                    result.unknown_tags_count++;
                    break;
            }
        }

        return result;
    }
};
