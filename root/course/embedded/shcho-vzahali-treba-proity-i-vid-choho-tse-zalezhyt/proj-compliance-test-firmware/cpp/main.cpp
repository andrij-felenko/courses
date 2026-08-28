#include <cstdint>
#include <string_view>
#include <span>
#include <charconv>
#include <array>

namespace compliance {

enum class RfMode : uint8_t {
    Idle = 0,
    TxContinuousWave,
    TxModulatedPrbs9,
    RxContinuous
};

struct RadioConfig {
    static constexpr uint8_t MinChannel = 0;
    static constexpr uint8_t MaxChannel = 39;
    static constexpr int8_t MinPowerDbm = -20;
    static constexpr int8_t MaxPowerDbm = 8;
};

class RfComplianceController {
public:
    constexpr RfComplianceController() noexcept = default;

    void init() noexcept {
        stopHardware();
        currentMode_ = RfMode::Idle;
    }

    bool handleCommand(std::string_view cmdLine, std::span<char> responseOut) noexcept {
        auto tokens = tokenize(cmdLine);
        if (tokens.empty()) {
            writeResponse(responseOut, "ERR: EMPTY_CMD\r\n");
            return false;
        }

        const auto verb = tokens[0];
        if (verb == "STOP") {
            stopHardware();
            currentMode_ = RfMode::Idle;
            writeResponse(responseOut, "OK: RADIO_STOPPED\r\n");
            return true;
        }

        if (tokens.size() < 2) {
            writeResponse(responseOut, "ERR: MISSING_ARGS\r\n");
            return false;
        }

        int channel = 0;
        if (!parseNumber(tokens[1], channel) || 
            channel < RadioConfig::MinChannel || channel > RadioConfig::MaxChannel) {
            writeResponse(responseOut, "ERR: INVALID_CHANNEL (0..39)\r\n");
            return false;
        }

        if (verb == "RX") {
            stopHardware();
            channel_ = static_cast<uint8_t>(channel);
            currentMode_ = RfMode::RxContinuous;
            startHardwareRx(channel_);
            writeResponse(responseOut, "OK: RX_STANDBY\r\n");
            return true;
        }

        if (tokens.size() < 3) {
            writeResponse(responseOut, "ERR: MISSING_POWER\r\n");
            return false;
        }

        int power = 0;
        if (!parseNumber(tokens[2], power) || 
            power < RadioConfig::MinPowerDbm || power > RadioConfig::MaxPowerDbm) {
            writeResponse(responseOut, "ERR: INVALID_POWER (-20..+8 dBm)\r\n");
            return false;
        }

        channel_ = static_cast<uint8_t>(channel);
        powerDbm_ = static_cast<int8_t>(power);

        if (verb == "TX_CW") {
            stopHardware();
            currentMode_ = RfMode::TxContinuousWave;
            startHardwareCw(channel_, powerDbm_);
            writeResponse(responseOut, "OK: TX_CW_ACTIVE\r\n");
            return true;
        }

        if (verb == "TX_MOD") {
            stopHardware();
            currentMode_ = RfMode::TxModulatedPrbs9;
            startHardwareModulated(channel_, powerDbm_);
            writeResponse(responseOut, "OK: TX_MOD_PRBS9_ACTIVE\r\n");
            return true;
        }

        writeResponse(responseOut, "ERR: UNKNOWN_COMMAND\r\n");
        return false;
    }

    [[nodiscard]] RfMode mode() const noexcept { return currentMode_; }
    [[nodiscard]] uint8_t channel() const noexcept { return channel_; }
    [[nodiscard]] int8_t power() const noexcept { return powerDbm_; }

private:
    RfMode currentMode_{RfMode::Idle};
    uint8_t channel_{0};
    int8_t powerDbm_{0};

    static void stopHardware() noexcept {
        /* Апаратне вимкнення генератора та підсилювачів */
    }

    static void startHardwareCw(uint8_t ch, int8_t pwr) noexcept {
        /* Налаштування регістрів на генерацію немодульованого тону */
    }

    static void startHardwareModulated(uint8_t ch, int8_t pwr) noexcept {
        /* Запуск генератора PRBS9 з модуляцією GFSK */
    }

    static void startHardwareRx(uint8_t ch) noexcept {
        /* Переведення ВЧ-тракту в режим постійного прийому */
    }

    static bool parseNumber(std::string_view sv, int &val) noexcept {
        const auto res = std::from_chars(sv.data(), sv.data() + sv.size(), val);
        return res.ec == std::errc{};
    }

    static void writeResponse(std::span<char> dst, std::string_view src) noexcept {
        const auto len = std::min(dst.size() - 1, src.size());
        std::copy_n(src.data(), len, dst.data());
        dst[len] = '\0';
    }

    static auto tokenize(std::string_view s) noexcept {
        std::array<std::string_view, 4> tokens{};
        size_t count = 0;
        size_t start = 0;

        while (start < s.size() && count < tokens.size()) {
            while (start < s.size() && (s[start] == ' ' || s[start] == '\r' || s[start] == '\n')) {
                ++start;
            }
            if (start >= s.size()) break;

            size_t end = start;
            while (end < s.size() && s[end] != ' ' && s[end] != '\r' && s[end] != '\n') {
                ++end;
            }
            tokens[count++] = s.substr(start, end - start);
            start = end;
        }
        return std::span<const std::string_view>(tokens.data(), count);
    }
};

} // namespace compliance
