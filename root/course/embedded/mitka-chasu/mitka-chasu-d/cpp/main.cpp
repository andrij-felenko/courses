#include <cstdint>
#include <span>
#include <vector>
#include <optional>
#include <chrono>
#include <cstring>
#include <algorithm>

namespace telemetry {

enum class Mode : uint8_t {
    Absolute     = 0x00,
    ForwardDelta = 0x01,
    ReverseDelta = 0x02
};

enum class RtcStatus : uint8_t {
    Unsynchronized = 0x00,
    Estimated      = 0x04,
    Synchronized   = 0x08
};

struct SensorSample {
    std::chrono::milliseconds local_time;
    int16_t raw_value;
};

struct ReconstructedPoint {
    std::chrono::system_clock::time_point timestamp;
    int16_t raw_value;
};

#pragma pack(push, 1)
struct Header {
    uint8_t  magic{0x7E};
    uint8_t  version{0x01};
    uint16_t flags{0};
    uint8_t  sample_count{0};
    uint8_t  sample_type{0};
    uint32_t anchor_sec{0};
};
#pragma pack(pop)

class PacketCodec {
public:
    // Пакування серії замірів у бінарний вектор
    static std::optional<std::vector<uint8_t>> pack_reverse(
        RtcStatus status,
        uint8_t sample_type,
        std::span<const SensorSample> samples,
        std::chrono::milliseconds tx_moment
    ) {
        if (samples.empty() || samples.size() > 255) {
            return std::nullopt;
        }

        const size_t total_size = sizeof(Header) + 
                                  samples.size() * (sizeof(uint16_t) + sizeof(int16_t));
        std::vector<uint8_t> buffer(total_size);

        Header hdr{};
        hdr.flags = static_cast<uint16_t>(Mode::ReverseDelta) | static_cast<uint16_t>(status);
        hdr.sample_count = static_cast<uint8_t>(samples.size());
        hdr.sample_type = sample_type;

        std::memcpy(buffer.data(), &hdr, sizeof(hdr));
        auto* delta_ptr = reinterpret_cast<uint16_t*>(buffer.data() + sizeof(Header));
        auto* val_ptr = reinterpret_cast<int16_t*>(buffer.data() + sizeof(Header) + 
                                                   samples.size() * sizeof(uint16_t));

        for (size_t i = 0; i < samples.size(); ++i) {
            auto diff = std::chrono::duration_cast<std::chrono::milliseconds>(
                tx_moment - samples[i].local_time
            ).count();
            delta_ptr[i] = static_cast<uint16_t>(std::clamp<int64_t>(diff, 0, 65535));
            val_ptr[i] = samples[i].raw_value;
        }

        return buffer;
    }

    // Реконструкція точок на сервері
    static std::optional<std::vector<ReconstructedPoint>> unpack_reconstruct(
        std::span<const uint8_t> packet,
        std::chrono::system_clock::time_point server_rx_time,
        std::chrono::milliseconds propagation_delay
    ) {
        if (packet.size() < sizeof(Header)) {
            return std::nullopt;
        }

        Header hdr{};
        std::memcpy(&hdr, packet.data(), sizeof(Header));
        if (hdr.magic != 0x7E || hdr.version != 0x01) {
            return std::nullopt;
        }

        const size_t expected_size = sizeof(Header) + 
                                     hdr.sample_count * (sizeof(uint16_t) + sizeof(int16_t));
        if (packet.size() < expected_size) {
            return std::nullopt;
        }

        const auto mode = static_cast<Mode>(hdr.flags & 0x03);
        if (mode != Mode::ReverseDelta) {
            return std::nullopt;
        }

        const auto* delta_ptr = reinterpret_cast<const uint16_t*>(packet.data() + sizeof(Header));
        const auto* val_ptr = reinterpret_cast<const int16_t*>(
            packet.data() + sizeof(Header) + hdr.sample_count * sizeof(uint16_t)
        );

        const auto anchor_utc = server_rx_time - propagation_delay;
        std::vector<ReconstructedPoint> result;
        result.reserve(hdr.sample_count);

        for (size_t i = 0; i < hdr.sample_count; ++i) {
            auto delta = std::chrono::milliseconds(delta_ptr[i]);
            result.push_back(ReconstructedPoint{
                .timestamp = anchor_utc - delta,
                .raw_value = val_ptr[i]
            });
        }

        return result;
    }
};

} // namespace telemetry
