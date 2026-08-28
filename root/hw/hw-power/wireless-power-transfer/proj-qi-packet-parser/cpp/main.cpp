#include <cstdint>
#include <functional>
#include <span>
#include <array>
#include <algorithm>

namespace qi {

constexpr uint32_t kBitHalfMinUs = 180;
constexpr uint32_t kBitHalfMaxUs = 320;
constexpr uint32_t kBitFullMinUs = 420;
constexpr uint32_t kBitFullMaxUs = 580;

constexpr size_t   kMaxPayloadLen   = 32;
constexpr uint8_t  kPreambleMinBits = 11;

enum class Header : uint8_t {
    SignalStrength = 0x01,
    EndTransfer    = 0x02,
    ControlError   = 0x03,
    ReceivedPower  = 0x04,
    Configuration  = 0x51,
    Identification = 0x71
};

struct Packet {
    Header header{Header::SignalStrength};
    std::array<uint8_t, kMaxPayloadLen> payload{};
    uint8_t payload_len{0};
    uint8_t checksum{0};
    bool valid{false};

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return std::span<const uint8_t>(payload.data(), payload_len);
    }
};

class Receiver {
public:
    using PacketCallback = std::function<void(const Packet&)>;

    explicit Receiver(PacketCallback callback = nullptr)
        : callback_(std::move(callback)) {}

    void on_edge(uint32_t current_time_us) {
        if (last_edge_time_us_ == 0) {
            last_edge_time_us_ = current_time_us;
            return;
        }

        const uint32_t dt = current_time_us - last_edge_time_us_;
        last_edge_time_us_ = current_time_us;

        if (dt < kBitHalfMinUs) {
            return;
        }

        switch (bmc_state_) {
            case BmcState::WaitSync:
                if (dt >= kBitHalfMinUs && dt <= kBitHalfMaxUs) {
                    bmc_state_ = BmcState::FirstHalf;
                } else if (dt >= kBitFullMinUs && dt <= kBitFullMaxUs) {
                    push_bit(0);
                }
                break;

            case BmcState::FirstHalf:
                if (dt >= kBitHalfMinUs && dt <= kBitHalfMaxUs) {
                    push_bit(1);
                    bmc_state_ = BmcState::WaitSync;
                } else {
                    bmc_state_ = BmcState::WaitSync;
                    preamble_count_ = 0;
                }
                break;
        }
    }

private:
    enum class BmcState { WaitSync, FirstHalf };
    enum class ParserState { Preamble, Header, Payload, Checksum };

    void push_bit(uint8_t bit) {
        if (parser_state_ == ParserState::Preamble) {
            if (bit == 1) {
                preamble_count_++;
            } else {
                if (preamble_count_ >= kPreambleMinBits) {
                    bit_index_ = 0;
                    rx_byte_ = 0;
                    parser_state_ = ParserState::Header;
                }
                preamble_count_ = 0;
            }
            return;
        }

        rx_byte_ = static_cast<uint8_t>((rx_byte_ << 1) | (bit & 0x01));
        bit_index_++;

        if (bit_index_ >= 8) {
            push_byte(rx_byte_);
            bit_index_ = 0;
            rx_byte_ = 0;
        }
    }

    void push_byte(uint8_t byte) {
        switch (parser_state_) {
            case ParserState::Preamble:
                break;

            case ParserState::Header:
                current_pkt_.header = static_cast<Header>(byte);
                current_pkt_.payload_len = get_payload_len(byte);
                calc_checksum_ = byte;
                payload_idx_ = 0;
                parser_state_ = (current_pkt_.payload_len > 0) ? ParserState::Payload : ParserState::Checksum;
                break;

            case ParserState::Payload:
                current_pkt_.payload[payload_idx_++] = byte;
                calc_checksum_ ^= byte;
                if (payload_idx_ >= current_pkt_.payload_len) {
                    parser_state_ = ParserState::Checksum;
                }
                break;

            case ParserState::Checksum:
                current_pkt_.checksum = byte;
                current_pkt_.valid = (calc_checksum_ == byte);
                if (current_pkt_.valid && callback_) {
                    callback_(current_pkt_);
                }
                parser_state_ = ParserState::Preamble;
                preamble_count_ = 0;
                break;
        }
    }

    static uint8_t get_payload_len(uint8_t hdr_raw) {
        switch (static_cast<Header>(hdr_raw)) {
            case Header::SignalStrength: return 1;
            case Header::EndTransfer:    return 1;
            case Header::ControlError:   return 1;
            case Header::ReceivedPower:  return 1;
            case Header::Configuration:  return 5;
            case Header::Identification: return 7;
            default: return static_cast<uint8_t>((hdr_raw >> 5) + 1);
        }
    }

    BmcState bmc_state_{BmcState::WaitSync};
    uint32_t last_edge_time_us_{0};
    uint8_t  preamble_count_{0};

    uint8_t  rx_byte_{0};
    uint8_t  bit_index_{0};

    ParserState parser_state_{ParserState::Preamble};
    Packet      current_pkt_{};
    uint8_t     payload_idx_{0};
    uint8_t     calc_checksum_{0};
    PacketCallback callback_;
};

class PowerController {
public:
    static constexpr float kFreqMinKhz = 110.0f;
    static constexpr float kFreqMaxKhz = 205.0f;
    static constexpr float kKp         = 0.25f;
    static constexpr float kKi         = 0.05f;

    explicit PowerController(float start_freq_khz = 145.0f)
        : current_freq_khz_(start_freq_khz) {}

    void process_cep(int8_t cep_value) {
        const float error = static_cast<float>(cep_value);
        integral_err_ += error;
        integral_err_ = std::clamp(integral_err_, -50.0f, 50.0f);

        const float delta_f = -(kKp * error + kKi * integral_err_);
        current_freq_khz_ = std::clamp(current_freq_khz_ + delta_f, kFreqMinKhz, kFreqMaxKhz);
    }

    [[nodiscard]] float frequency_khz() const noexcept {
        return current_freq_khz_;
    }

private:
    float current_freq_khz_{145.0f};
    float integral_err_{0.0f};
};

} // namespace qi
