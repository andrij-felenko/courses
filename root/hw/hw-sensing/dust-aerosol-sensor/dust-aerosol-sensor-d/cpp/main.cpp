#include <cstdint>
#include <array>
#include <span>
#include <optional>

struct Pms5003Data {
    uint16_t pm1_0_std{};
    uint16_t pm2_5_std{};
    uint16_t pm10_std{};
    uint16_t pm1_0_atm{};
    uint16_t pm2_5_atm{};
    uint16_t pm10_atm{};
    uint16_t count_0_3{};
    uint16_t count_0_5{};
    uint16_t count_1_0{};
    uint16_t count_2_5{};
    uint16_t count_5_0{};
    uint16_t count_10{};
};

class Pms5003Parser {
public:
    static constexpr size_t FrameSize = 32;
    static constexpr uint8_t Header1 = 0x42;
    static constexpr uint8_t Header2 = 0x4D;

    constexpr Pms5003Parser() = default;

    std::optional<Pms5003Data> parseByte(uint8_t byte) noexcept {
        switch (state_) {
            case State::WaitH1:
                if (byte == Header1) {
                    buffer_[0] = byte;
                    index_ = 1;
                    state_ = State::WaitH2;
                }
                break;

            case State::WaitH2:
                if (byte == Header2) {
                    buffer_[1] = byte;
                    index_ = 2;
                    state_ = State::ReadPayload;
                } else if (byte == Header1) {
                    index_ = 1;
                } else {
                    state_ = State::WaitH1;
                }
                break;

            case State::ReadPayload:
                buffer_[index_++] = byte;
                if (index_ >= FrameSize) {
                    state_ = State::WaitH1;
                    return validateAndExtract();
                }
                break;
        }
        return std::nullopt;
    }

    void reset() noexcept {
        state_ = State::WaitH1;
        index_ = 0;
    }

private:
    enum class State : uint8_t {
        WaitH1,
        WaitH2,
        ReadPayload
    };

    static constexpr uint16_t readBe16(const uint8_t* ptr) noexcept {
        return static_cast<uint16_t>((ptr[0] << 8) | ptr[1]);
    }

    std::optional<Pms5003Data> validateAndExtract() const noexcept {
        if (readBe16(&buffer_[2]) != 28) {
            return std::nullopt;
        }

        uint16_t calculatedSum = 0;
        for (size_t i = 0; i < 30; ++i) {
            calculatedSum += buffer_[i];
        }

        if (calculatedSum != readBe16(&buffer_[30])) {
            return std::nullopt;
        }

        Pms5003Data data;
        data.pm1_0_std = readBe16(&buffer_[4]);
        data.pm2_5_std = readBe16(&buffer_[6]);
        data.pm10_std  = readBe16(&buffer_[8]);
        data.pm1_0_atm = readBe16(&buffer_[10]);
        data.pm2_5_atm = readBe16(&buffer_[12]);
        data.pm10_atm  = readBe16(&buffer_[14]);
        data.count_0_3 = readBe16(&buffer_[16]);
        data.count_0_5 = readBe16(&buffer_[18]);
        data.count_1_0 = readBe16(&buffer_[20]);
        data.count_2_5 = readBe16(&buffer_[22]);
        data.count_5_0 = readBe16(&buffer_[24]);
        data.count_10  = readBe16(&buffer_[26]);
        return data;
    }

    State state_{State::WaitH1};
    std::array<uint8_t, FrameSize> buffer_{};
    size_t index_{0};
};
