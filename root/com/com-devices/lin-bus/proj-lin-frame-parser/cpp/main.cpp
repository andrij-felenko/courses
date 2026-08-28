#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

enum class LinChecksumType {
    Classic,
    Enhanced
};

enum class LinState {
    WaitBreak,
    WaitSync,
    WaitPid,
    WaitData,
    WaitChecksum
};

struct LinFrame {
    uint8_t id{0};
    uint8_t pid{0};
    std::array<uint8_t, 8> data{};
    uint8_t data_len{0};
    uint8_t checksum{0};
    bool valid{false};

    [[nodiscard]] constexpr std::span<const uint8_t> payload() const noexcept {
        return std::span<const uint8_t>{data.data(), data_len};
    }
};

class LinFrameParser {
public:
    explicit constexpr LinFrameParser(LinChecksumType default_checksum = LinChecksumType::Enhanced) noexcept
        : default_checksum_{default_checksum} {}

    static constexpr uint8_t calculate_pid(uint8_t id) noexcept {
        const uint8_t id_clean = id & 0x3F;
        const uint8_t p0 = ((id_clean >> 0) ^ (id_clean >> 1) ^ (id_clean >> 2) ^ (id_clean >> 4)) & 0x01;
        const uint8_t p1 = ~((id_clean >> 1) ^ (id_clean >> 3) ^ (id_clean >> 4) ^ (id_clean >> 5)) & 0x01;
        return id_clean | static_cast<uint8_t>(p0 << 6) | static_cast<uint8_t>(p1 << 7);
    }

    static constexpr bool verify_pid(uint8_t pid) noexcept {
        return calculate_pid(pid & 0x3F) == pid;
    }

    static constexpr uint8_t calculate_checksum(uint8_t pid, std::span<const uint8_t> data, LinChecksumType type) noexcept {
        uint16_t sum = 0;
        if (type == LinChecksumType::Enhanced) {
            sum += pid;
        }
        for (const uint8_t b : data) {
            sum += b;
            if (sum > 0xFF) {
                sum = (sum & 0xFF) + 1;
            }
        }
        return static_cast<uint8_t>(~sum & 0xFF);
    }

    constexpr void reset() noexcept {
        state_ = LinState::WaitBreak;
        data_index_ = 0;
        current_frame_ = LinFrame{};
    }

    constexpr void on_break_detected() noexcept {
        state_ = LinState::WaitSync;
        data_index_ = 0;
        current_frame_ = LinFrame{};
    }

    constexpr std::optional<LinFrame> process_byte(uint8_t byte, uint8_t expected_len) noexcept {
        switch (state_) {
            case LinState::WaitBreak:
                break;

            case LinState::WaitSync:
                if (byte == 0x55) {
                    state_ = LinState::WaitPid;
                } else {
                    reset();
                }
                break;

            case LinState::WaitPid:
                if (verify_pid(byte)) {
                    current_frame_.pid = byte;
                    current_frame_.id = byte & 0x3F;
                    current_frame_.data_len = (expected_len > 8) ? 8 : expected_len;
                    data_index_ = 0;
                    state_ = LinState::WaitData;
                } else {
                    reset();
                }
                break;

            case LinState::WaitData:
                current_frame_.data[data_index_++] = byte;
                if (data_index_ >= current_frame_.data_len) {
                    state_ = LinState::WaitChecksum;
                }
                break;

            case LinState::WaitChecksum: {
                current_frame_.checksum = byte;
                LinChecksumType active_type = default_checksum_;
                if (current_frame_.id == 0x3C || current_frame_.id == 0x3D) {
                    active_type = LinChecksumType::Classic;
                }

                const uint8_t calculated = calculate_checksum(
                    current_frame_.pid,
                    current_frame_.payload(),
                    active_type
                );

                current_frame_.valid = (calculated == byte);
                LinFrame result = current_frame_;
                reset();
                
                if (result.valid) {
                    return result;
                }
                break;
            }
        }
        return std::nullopt;
    }

private:
    LinChecksumType default_checksum_;
    LinState state_{LinState::WaitBreak};
    uint8_t data_index_{0};
    LinFrame current_frame_{};
};
