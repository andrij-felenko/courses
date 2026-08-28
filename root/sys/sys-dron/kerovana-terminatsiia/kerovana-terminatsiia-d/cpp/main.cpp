#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>

namespace fts {

inline constexpr uint32_t MagicHeader    = 0x5AA5F751U;
inline constexpr uint32_t ArmWindowMs    = 2500U;
inline constexpr uint32_t MinArmTimeMs   = 100U;

enum class State : uint8_t {
    Safe = 0,
    Armed,
    Triggered,
    LatchedKill
};

enum class Command : uint8_t {
    None = 0x00,
    Arm  = 0xA5,
    Kill = 0x5A,
    Ping = 0x55
};

enum class ParseError {
    BufferTooSmall,
    InvalidMagic,
    ChecksumMismatch,
    SequenceReplay,
    AuthenticationFailed,
    WindowExpired
};

struct [[gnu::packed]] PacketHeader {
    uint32_t magic;
    uint32_t seq_num;
    uint32_t timestamp_ms;
    Command  command;
    uint8_t  reserved[3];
    uint32_t auth_token;
    uint32_t crc32;
};

class HardwareInterlock {
public:
    static void executeMotorKill() noexcept {
        /* Апаратне замикання ліній DShot на GND та відсікання eFuse */
    }

    static void firePyrotechnicSquib() noexcept {
        /* Двоконтурний імпульс активації парашута */
    }
};

class Controller {
public:
    explicit constexpr Controller(uint32_t secret_key) noexcept
        : secretKey_(secret_key) {}

    [[nodiscard]] std::expected<void, ParseError> processPacket(
        std::span<const uint8_t> buffer,
        uint32_t currentTimeMs) noexcept
    {
        if (buffer.size() < sizeof(PacketHeader)) {
            return std::unexpected(ParseError::BufferTooSmall);
        }

        const auto& pkt = *reinterpret_cast<const PacketHeader*>(buffer.data());

        if (pkt.magic != MagicHeader) {
            return std::unexpected(ParseError::InvalidMagic);
        }

        const uint32_t calcCrc = computeCrc32(buffer.first(sizeof(PacketHeader) - sizeof(uint32_t)));
        if (calcCrc != pkt.crc32) {
            return std::unexpected(ParseError::ChecksumMismatch);
        }

        if (pkt.seq_num <= lastSeq_) {
            return std::unexpected(ParseError::SequenceReplay);
        }

        if (computeToken(pkt, secretKey_) != pkt.auth_token) {
            return std::unexpected(ParseError::AuthenticationFailed);
        }

        lastSeq_ = pkt.seq_num;
        applyCommand(pkt.command, currentTimeMs);
        return {};
    }

    void updatePeriodic(uint32_t currentTimeMs) noexcept {
        if (state_ == State::Armed) {
            if (currentTimeMs - armTimestampMs_ > ArmWindowMs) {
                state_ = State::Safe;
            }
        }
    }

    [[nodiscard]] State getState() const noexcept { return state_; }
    [[nodiscard]] bool isLatched() const noexcept { return state_ == State::LatchedKill; }

private:
    void applyCommand(Command cmd, uint32_t currentTimeMs) noexcept {
        switch (state_) {
            case State::Safe:
                if (cmd == Command::Arm) {
                    state_ = State::Armed;
                    armTimestampMs_ = currentTimeMs;
                }
                break;

            case State::Armed:
                if (cmd == Command::Kill) {
                    const uint32_t delta = currentTimeMs - armTimestampMs_;
                    if (delta >= MinArmTimeMs && delta <= ArmWindowMs) {
                        state_ = State::Triggered;
                        HardwareInterlock::executeMotorKill();
                        HardwareInterlock::firePyrotechnicSquib();
                        state_ = State::LatchedKill;
                    } else {
                        state_ = State::Safe;
                    }
                } else if (cmd == Command::Arm) {
                    armTimestampMs_ = currentTimeMs;
                }
                break;

            case State::Triggered:
            case State::LatchedKill:
                HardwareInterlock::executeMotorKill();
                break;
        }
    }

    static uint32_t computeCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1U)));
            }
        }
        return ~crc;
    }

    static uint32_t computeToken(const PacketHeader& pkt, uint32_t key) noexcept {
        uint32_t hash = key ^ pkt.magic ^ pkt.seq_num ^ pkt.timestamp_ms ^ static_cast<uint32_t>(pkt.command);
        hash = ((hash << 13) | (hash >> 19)) * 0x5BD1E995U;
        return hash ^ (hash >> 15);
    }

    State    state_{State::Safe};
    uint32_t lastSeq_{0};
    uint32_t armTimestampMs_{0};
    uint32_t secretKey_{0};
};

} // namespace fts
