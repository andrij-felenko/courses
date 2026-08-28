#include <cstdint>
#include <cstddef>
#include <array>
#include <vector>
#include <optional>
#include <span>
#include <string_view>

namespace usbpd {

constexpr uint32_t FreqHz         = 300'000;
constexpr float    TBitUs         = 3.333333f;
constexpr float    THalfUs        = 1.666667f;

constexpr float    TNoiseMinUs    = 0.833f;
constexpr float    TSplitUs       = 2.500f;
constexpr float    TTimeoutMaxUs  = 4.167f;

// 5-бітні K-символи керування
enum class KCode : uint8_t {
    Sync1 = 0x18, // 11000b
    Sync2 = 0x12, // 10010b
    Sync3 = 0x06, // 00110b
    Rst1  = 0x07, // 00111b
    Rst2  = 0x19, // 11001b
    Eop   = 0x0D  // 01101b
};

enum class SopType {
    Unknown = 0,
    Sop,        // Sync1 + Sync1 + Sync1 + Sync2
    SopPrime,   // Sync1 + Sync1 + Sync3 + Sync3
    SopDPrime,  // Sync1 + Sync3 + Sync1 + Sync3
    HardReset,  // Rst1 + Rst1 + Rst1 + Rst2
    CableReset  // Rst1 + Sync1 + Rst1 + Sync1
};

// Константні таблиці 4b/5b
constexpr std::array<uint8_t, 16> Table4b5b = {
    0x1E, 0x09, 0x14, 0x15, 0x0A, 0x0B, 0x0E, 0x0F,
    0x12, 0x13, 0x16, 0x17, 0x1A, 0x1B, 0x1C, 0x1D
};

constexpr std::array<uint8_t, 32> Table5b4b = {
    0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
    0xFF, 0x01, 0x04, 0x05, 0xFF, 0xFF, 0x06, 0x07,
    0xFF, 0xFF, 0x08, 0x09, 0x02, 0x03, 0x0A, 0x0B,
    0xFF, 0xFF, 0x0C, 0x0D, 0x0E, 0x0F, 0x00, 0xFF
};

// Обчислення CRC-32 для USB Power Delivery
constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFUL;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320UL;
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

// Клас BMC кодера
class BmcEncoder {
public:
    BmcEncoder() = default;

    [[nodiscard]] std::vector<float> encode_packet(std::span<const uint8_t> payload, SopType sop) {
        std::vector<float> intervals;
        intervals.reserve(128 + payload.size() * 20);

        // 1. 64 біти преамбули
        for (int i = 0; i < 64; ++i) {
            encode_bit(intervals, false);
        }

        // 2. Стартовий маркер SOP
        switch (sop) {
            case SopType::Sop:
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync2));
                break;
            case SopType::SopPrime:
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync3));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync3));
                break;
            case SopType::SopDPrime:
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync3));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync3));
                break;
            case SopType::HardReset:
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst2));
                return intervals;
            case SopType::CableReset:
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Rst1));
                encode_5b(intervals, static_cast<uint8_t>(KCode::Sync1));
                return intervals;
            default:
                return {};
        }

        // 3. Корисне навантаження
        for (uint8_t byte : payload) {
            encode_5b(intervals, Table4b5b[byte & 0x0F]);
            encode_5b(intervals, Table4b5b[(byte >> 4) & 0x0F]);
        }

        // 4. CRC-32
        uint32_t crc = calculate_crc32(payload);
        for (int i = 0; i < 4; ++i) {
            uint8_t byte = (crc >> (i * 8)) & 0xFF;
            encode_5b(intervals, Table4b5b[byte & 0x0F]);
            encode_5b(intervals, Table4b5b[(byte >> 4) & 0x0F]);
        }

        // 5. Завершення пакета EOP
        encode_5b(intervals, static_cast<uint8_t>(KCode::Eop));

        return intervals;
    }

private:
    static void encode_bit(std::vector<float>& out, bool bit) {
        if (bit) {
            out.push_back(THalfUs);
            out.push_back(THalfUs);
        } else {
            out.push_back(TBitUs);
        }
    }

    static void encode_5b(std::vector<float>& out, uint8_t sym5b) {
        for (int i = 0; i < 5; ++i) {
            encode_bit(out, (sym5b >> i) & 1);
        }
    }
};

// Результат декодування пакета
struct DecodedPacket {
    SopType sop = SopType::Unknown;
    std::vector<uint8_t> payload;
    uint32_t received_crc = 0;
    bool crc_valid = false;
};

// Клас BMC декодера
class BmcDecoder {
public:
    enum class State {
        WaitPreamble,
        WaitSop,
        ReceivePayload,
        PacketDone,
        Error
    };

    BmcDecoder() { reset(); }

    void reset() noexcept {
        state_ = State::WaitPreamble;
        half_bit_pending_ = false;
        shift_reg_ = 0;
        sym_shift_reg_ = 0;
        sym_bit_count_ = 0;
        nibble_buffer_ = 0;
        high_nibble_expected_ = false;
        current_packet_ = {};
    }

    // Обробка чергового виміряного інтервалу
    std::optional<DecodedPacket> feed_interval(float dt_us) {
        if (dt_us < TNoiseMinUs) {
            return std::nullopt; // Шумовий викид
        }

        if (dt_us > TTimeoutMaxUs) {
            half_bit_pending_ = false;
            if (state_ == State::ReceivePayload && current_packet_.payload.size() >= 4) {
                return finalize_packet();
            }
            state_ = State::WaitPreamble;
            return std::nullopt;
        }

        int bit_val = -1;
        if (dt_us < TSplitUs) {
            if (half_bit_pending_) {
                bit_val = 1;
                half_bit_pending_ = false;
            } else {
                half_bit_pending_ = true;
                return std::nullopt;
            }
        } else {
            if (half_bit_pending_) {
                half_bit_pending_ = false;
                state_ = State::Error;
                return std::nullopt;
            }
            bit_val = 0;
        }

        shift_reg_ = ((shift_reg_ >> 1) | (static_cast<uint32_t>(bit_val) << 19)) & 0xFFFFF;

        if (state_ == State::WaitPreamble || state_ == State::WaitSop) {
            constexpr uint32_t SopPattern = 
                static_cast<uint32_t>(KCode::Sync1) |
                (static_cast<uint32_t>(KCode::Sync1) << 5) |
                (static_cast<uint32_t>(KCode::Sync1) << 10) |
                (static_cast<uint32_t>(KCode::Sync2) << 15);

            constexpr uint32_t SopPPattern = 
                static_cast<uint32_t>(KCode::Sync1) |
                (static_cast<uint32_t>(KCode::Sync1) << 5) |
                (static_cast<uint32_t>(KCode::Sync3) << 10) |
                (static_cast<uint32_t>(KCode::Sync3) << 15);

            constexpr uint32_t HardRstPattern = 
                static_cast<uint32_t>(KCode::Rst1) |
                (static_cast<uint32_t>(KCode::Rst1) << 5) |
                (static_cast<uint32_t>(KCode::Rst1) << 10) |
                (static_cast<uint32_t>(KCode::Rst2) << 15);

            if (shift_reg_ == SopPattern) {
                current_packet_.sop = SopType::Sop;
                state_ = State::ReceivePayload;
                sym_bit_count_ = 0;
                sym_shift_reg_ = 0;
                high_nibble_expected_ = false;
                current_packet_.payload.clear();
            } else if (shift_reg_ == SopPPattern) {
                current_packet_.sop = SopType::SopPrime;
                state_ = State::ReceivePayload;
                sym_bit_count_ = 0;
                sym_shift_reg_ = 0;
                high_nibble_expected_ = false;
                current_packet_.payload.clear();
            } else if (shift_reg_ == HardRstPattern) {
                current_packet_.sop = SopType::HardReset;
                state_ = State::PacketDone;
                DecodedPacket res = std::move(current_packet_);
                reset();
                return res;
            }
            return std::nullopt;
        }

        if (state_ == State::ReceivePayload) {
            sym_shift_reg_ |= (static_cast<uint8_t>(bit_val) << sym_bit_count_);
            sym_bit_count_++;

            if (sym_bit_count_ == 5) {
                uint8_t symbol = sym_shift_reg_;
                sym_bit_count_ = 0;
                sym_shift_reg_ = 0;

                if (symbol == static_cast<uint8_t>(KCode::Eop)) {
                    return finalize_packet();
                }

                uint8_t nibble = Table5b4b[symbol & 0x1F];
                if (nibble == 0xFF) {
                    state_ = State::Error;
                    return std::nullopt;
                }

                if (!high_nibble_expected_) {
                    nibble_buffer_ = nibble;
                    high_nibble_expected_ = true;
                } else {
                    uint8_t full_byte = nibble_buffer_ | (nibble << 4);
                    high_nibble_expected_ = false;
                    current_packet_.payload.push_back(full_byte);
                }
            }
        }

        return std::nullopt;
    }

private:
    std::optional<DecodedPacket> finalize_packet() {
        if (current_packet_.payload.size() < 4) {
            reset();
            return std::nullopt;
        }

        // Останні 4 байти — це контрольна сума CRC-32
        size_t data_len = current_packet_.payload.size() - 4;
        uint32_t rx_crc = static_cast<uint32_t>(current_packet_.payload[data_len]) |
                         (static_cast<uint32_t>(current_packet_.payload[data_len + 1]) << 8) |
                         (static_cast<uint32_t>(current_packet_.payload[data_len + 2]) << 16) |
                         (static_cast<uint32_t>(current_packet_.payload[data_len + 3]) << 24);

        std::span<const uint8_t> data_span(current_packet_.payload.data(), data_len);
        uint32_t calc_crc = calculate_crc32(data_span);

        current_packet_.received_crc = rx_crc;
        current_packet_.crc_valid = (rx_crc == calc_crc);
        current_packet_.payload.resize(data_len);

        DecodedPacket res = std::move(current_packet_);
        reset();
        return res;
    }

    State state_ = State::WaitPreamble;
    bool half_bit_pending_ = false;
    uint32_t shift_reg_ = 0;
    uint8_t sym_shift_reg_ = 0;
    uint8_t sym_bit_count_ = 0;
    uint8_t nibble_buffer_ = 0;
    bool high_nibble_expected_ = false;
    DecodedPacket current_packet_;
};

} // namespace usbpd
