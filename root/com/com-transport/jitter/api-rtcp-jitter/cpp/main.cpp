#include <cstdint>
#include <span>
#include <optional>
#include <bit>

struct RtcpHeaderView {
    uint8_t  version;
    bool     has_padding;
    uint8_t  report_count;
    uint8_t  packet_type;
    uint16_t length_words;
    uint32_t ssrc;

    static std::optional<RtcpHeaderView> parse(std::span<const uint8_t> data) noexcept {
        if (data.size() < 8) return std::nullopt;

        uint8_t b0 = data[0];
        uint16_t raw_len = (static_cast<uint16_t>(data[2]) << 8) | data[3];
        uint32_t raw_ssrc = (static_cast<uint32_t>(data[4]) << 24) |
                            (static_cast<uint32_t>(data[5]) << 16) |
                            (static_cast<uint32_t>(data[6]) << 8)  |
                            data[7];

        return RtcpHeaderView{
            .version = static_cast<uint8_t>((b0 >> 6) & 0x03),
            .has_padding = static_cast<bool>((b0 >> 5) & 0x01),
            .report_count = static_cast<uint8_t>(b0 & 0x1F),
            .packet_type = data[1],
            .length_words = raw_len,
            .ssrc = raw_ssrc
        };
    }
};

struct RtcpReportBlockView {
    uint32_t ssrc;
    float    fraction_lost;
    int32_t  cumulative_lost;
    uint32_t highest_seq_extended;
    uint32_t jitter_samples;
    uint32_t last_sr_ntp;
    uint32_t delay_since_last_sr;

    static std::optional<RtcpReportBlockView> parse(std::span<const uint8_t> data) noexcept {
        if (data.size() < 24) return std::nullopt;

        auto read32 = [](const uint8_t* p) -> uint32_t {
            return (static_cast<uint32_t>(p[0]) << 24) |
                   (static_cast<uint32_t>(p[1]) << 16) |
                   (static_cast<uint32_t>(p[2]) << 8)  |
                   p[3];
        };

        int32_t cum_lost = (data[5] << 16) | (data[6] << 8) | data[7];
        if (cum_lost & 0x00800000) cum_lost |= 0xFF000000;

        return RtcpReportBlockView{
            .ssrc = read32(&data[0]),
            .fraction_lost = static_cast<float>(data[4]) / 256.0f,
            .cumulative_lost = cum_lost,
            .highest_seq_extended = read32(&data[8]),
            .jitter_samples = read32(&data[12]),
            .last_sr_ntp = read32(&data[16]),
            .delay_since_last_sr = read32(&data[20])
        };
    }
};
