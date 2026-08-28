#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <expected>
#include <array>
#include <numeric>
#include <chrono>
#include <format>
#include <charconv>

enum class IridiumError {
    Timeout,
    ChecksumMismatch,
    NoNetworkSignal,
    BufferOverflow,
    ProtocolError
};

struct SbdixResponse {
    uint16_t moStatus{0};
    uint16_t momsn{0};
    uint16_t mtStatus{0};
    uint16_t mtmsn{0};
    uint16_t mtLength{0};
    uint16_t mtQueued{0};

    [[nodiscard]] constexpr bool isSuccess() const noexcept {
        return moStatus <= 4;
    }
};

class IridiumHal {
public:
    virtual ~IridiumHal() = default;
    virtual void setPower(bool enable) = 0;
    virtual void sleep(std::chrono::milliseconds ms) = 0;
    virtual bool write(std::span<const uint8_t> data) = 0;
    virtual std::size_t readLine(std::span<char> buffer, std::chrono::milliseconds timeout) = 0;
    virtual std::size_t readBytes(std::span<uint8_t> buffer, std::chrono::milliseconds timeout) = 0;
};

class IridiumTransceiver {
public:
    static constexpr std::size_t MaxMoLength = 340;
    static constexpr std::size_t MaxMtLength = 270;

    explicit IridiumTransceiver(IridiumHal& hal) noexcept : hal_(hal) {}

    std::expected<void, IridiumError> powerOn() {
        hal_.setPower(true);
        hal_.sleep(std::chrono::milliseconds{2000});

        const std::string_view syncCmd = "AT\r";
        hal_.write(std::span{reinterpret_cast<const uint8_t*>(syncCmd.data()), syncCmd.size()});

        std::array<char, 32> lineBuf{};
        if (hal_.readLine(lineBuf, std::chrono::milliseconds{2000}) == 0) {
            return std::unexpected(IridiumError::Timeout);
        }
        return {};
    }

    void powerOff() noexcept {
        hal_.setPower(false);
    }

    std::expected<uint8_t, IridiumError> getSignalQuality() {
        const std::string_view cmd = "AT+CSQ\r";
        hal_.write(std::span{reinterpret_cast<const uint8_t*>(cmd.data()), cmd.size()});

        std::array<char, 32> lineBuf{};
        if (hal_.readLine(lineBuf, std::chrono::milliseconds{3000}) == 0) {
            return std::unexpected(IridiumError::Timeout);
        }

        std::string_view resp(lineBuf.data());
        auto pos = resp.find("+CSQ:");
        if (pos != std::string_view::npos && pos + 5 < resp.size()) {
            uint8_t csq = 0;
            auto [ptr, ec] = std::from_chars(resp.data() + pos + 5, resp.data() + resp.size(), csq);
            if (ec == std::errc{}) {
                return csq;
            }
        }
        return std::unexpected(IridiumError::ProtocolError);
    }

    std::expected<void, IridiumError> loadBinary(std::span<const uint8_t> payload) {
        if (payload.empty() || payload.size() > MaxMoLength) {
            return std::unexpected(IridiumError::BufferOverflow);
        }

        const auto cmd = std::format("AT+SBDWB={}\r", payload.size());
        hal_.write(std::span{reinterpret_cast<const uint8_t*>(cmd.data()), cmd.size()});

        std::array<char, 16> readyBuf{};
        if (hal_.readLine(readyBuf, std::chrono::milliseconds{2000}) == 0) {
            return std::unexpected(IridiumError::Timeout);
        }
        if (std::string_view(readyBuf.data()).find("READY") == std::string_view::npos) {
            return std::unexpected(IridiumError::ProtocolError);
        }

        /* Обчислення 16-бітної контрольної суми */
        uint16_t checksum = std::accumulate(payload.begin(), payload.end(), uint16_t{0});

        hal_.write(payload);
        const std::array<uint8_t, 2> csBytes{
            static_cast<uint8_t>((checksum >> 8) & 0xFF),
            static_cast<uint8_t>(checksum & 0xFF)
        };
        hal_.write(csBytes);

        std::array<char, 16> ackBuf{};
        if (hal_.readLine(ackBuf, std::chrono::milliseconds{5000}) == 0) {
            return std::unexpected(IridiumError::Timeout);
        }
        if (ackBuf[0] != '0') {
            return std::unexpected(IridiumError::ChecksumMismatch);
        }
        return {};
    }

    std::expected<SbdixResponse, IridiumError> executeSession() {
        const std::string_view cmd = "AT+SBDIX\r";
        hal_.write(std::span{reinterpret_cast<const uint8_t*>(cmd.data()), cmd.size()});

        std::array<char, 128> respBuf{};
        if (hal_.readLine(respBuf, std::chrono::seconds{60}) == 0) {
            return std::unexpected(IridiumError::Timeout);
        }

        SbdixResponse res{};
        std::string_view resp(respBuf.data());
        auto pos = resp.find("+SBDIX:");
        if (pos == std::string_view::npos) {
            return std::unexpected(IridiumError::ProtocolError);
        }

        /* Розбір 6 числових параметрів через кому */
        const char* ptr = resp.data() + pos + 7;
        const char* end = resp.data() + resp.size();
        uint16_t* fields[] = {&res.moStatus, &res.momsn, &res.mtStatus, &res.mtmsn, &res.mtLength, &res.mtQueued};

        for (int i = 0; i < 6; ++i) {
            while (ptr < end && (*ptr == ' ' || *ptr == ',')) ++ptr;
            if (ptr >= end) return std::unexpected(IridiumError::ProtocolError);
            auto [next_ptr, ec] = std::from_chars(ptr, end, *fields[i]);
            if (ec != std::errc{}) return std::unexpected(IridiumError::ProtocolError);
            ptr = next_ptr;
        }

        if (res.isSuccess()) {
            return res;
        } else if (res.moStatus == 32) {
            return std::unexpected(IridiumError::NoNetworkSignal);
        }
        return std::unexpected(IridiumError::ProtocolError);
    }

    std::expected<std::size_t, IridiumError> readBinary(std::span<uint8_t> outputBuffer) {
        const std::string_view cmd = "AT+SBDRB\r";
        hal_.write(std::span{reinterpret_cast<const uint8_t*>(cmd.data()), cmd.size()});

        std::array<uint8_t, 2> lenBytes{};
        if (hal_.readBytes(lenBytes, std::chrono::milliseconds{3000}) != 2) {
            return std::unexpected(IridiumError::Timeout);
        }

        const uint16_t payloadLen = static_cast<uint16_t>((lenBytes[0] << 8) | lenBytes[1]);
        if (payloadLen > outputBuffer.size() || payloadLen > MaxMtLength) {
            return std::unexpected(IridiumError::BufferOverflow);
        }

        if (hal_.readBytes(outputBuffer.subspan(0, payloadLen), std::chrono::milliseconds{5000}) != payloadLen) {
            return std::unexpected(IridiumError::Timeout);
        }

        std::array<uint8_t, 2> csBytes{};
        if (hal_.readBytes(csBytes, std::chrono::milliseconds{2000}) != 2) {
            return std::unexpected(IridiumError::Timeout);
        }

        const uint16_t receivedChecksum = static_cast<uint16_t>((csBytes[0] << 8) | csBytes[1]);
        const uint16_t computedChecksum = std::accumulate(outputBuffer.begin(), outputBuffer.begin() + payloadLen, uint16_t{0});

        if (receivedChecksum != computedChecksum) {
            return std::unexpected(IridiumError::ChecksumMismatch);
        }

        return payloadLen;
    }

private:
    IridiumHal& hal_;
};
