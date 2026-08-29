#include "bootloader.hpp"

#include <array>

namespace {

using namespace std::chrono_literals;

constexpr std::uint8_t kAck = 0x79;
constexpr std::uint8_t kNack = 0x1F;

constexpr std::uint8_t kCmdSync = 0x7F;
constexpr std::uint8_t kCmdGetVersion = 0x01;
constexpr std::uint8_t kCmdGetId = 0x02;
constexpr std::uint8_t kCmdRead = 0x11;
constexpr std::uint8_t kCmdGo = 0x21;
constexpr std::uint8_t kCmdWrite = 0x31;
constexpr std::uint8_t kCmdEraseExt = 0x44;
constexpr std::uint8_t kCmdUnprotect = 0x92;

constexpr auto kAckTimeout = 1000ms;
constexpr auto kSyncTimeout = 2000ms;
constexpr auto kWriteTimeout = 3000ms;
constexpr auto kEraseTimeout = 30000ms; // високовольтне стирання всієї матриці

} // namespace

std::string_view describe(BootError error)
{
    switch (error) {
    case BootError::Io:       return "збій запису або читання порту";
    case BootError::Timeout:  return "завантажувач не відповів";
    case BootError::Nack:     return "чип відповів NACK";
    case BootError::Protocol: return "неочікуваний байт у відповіді";
    case BootError::Argument: return "хибний аргумент";
    }
    return "невідома помилка";
}

Result<void> Bootloader::waitAck(std::chrono::milliseconds timeout)
{
    std::uint8_t byte = 0;
    if (!port_.read(std::span{&byte, 1}, timeout)) {
        return std::unexpected{BootError::Timeout};
    }
    if (byte == kAck) {
        return {};
    }
    if (byte == kNack) {
        return std::unexpected{BootError::Nack};
    }
    return std::unexpected{BootError::Protocol};
}

// Кожна команда — байт коду і його побітова інверсія.
Result<void> Bootloader::command(std::uint8_t code, std::chrono::milliseconds ackTimeout)
{
    const std::array<std::uint8_t, 2> frame{code, static_cast<std::uint8_t>(~code)};
    if (!port_.write(frame)) {
        return std::unexpected{BootError::Io};
    }
    return waitAck(ackTimeout);
}

// Адреса — 4 байти зі старшого, п'ятий байт: XOR попередніх чотирьох.
Result<void> Bootloader::address(std::uint32_t value)
{
    const std::array<std::uint8_t, 5> frame{
        static_cast<std::uint8_t>(value >> 24),
        static_cast<std::uint8_t>(value >> 16),
        static_cast<std::uint8_t>(value >> 8),
        static_cast<std::uint8_t>(value),
        static_cast<std::uint8_t>((value >> 24) ^ (value >> 16) ^ (value >> 8) ^ value),
    };
    if (!port_.write(frame)) {
        return std::unexpected{BootError::Io};
    }
    return waitAck(kAckTimeout);
}

Result<void> Bootloader::sync()
{
    // Під час скидання ніжки в Hi-Z, і RX міг зловити фальшивий стартовий біт.
    port_.flush();

    const std::uint8_t byte = kCmdSync;
    if (!port_.write(std::span{&byte, 1})) {
        return std::unexpected{BootError::Io};
    }
    return waitAck(kSyncTimeout);
}

Result<Version> Bootloader::version()
{
    if (auto ok = command(kCmdGetVersion, kAckTimeout); !ok) {
        return std::unexpected{ok.error()};
    }

    std::array<std::uint8_t, 3> reply{};
    if (!port_.read(reply, kAckTimeout)) {
        return std::unexpected{BootError::Timeout};
    }
    if (auto ok = waitAck(kAckTimeout); !ok) {
        return std::unexpected{ok.error()};
    }
    return Version{reply[0], reply[1], reply[2]};
}

Result<std::uint16_t> Bootloader::chipId()
{
    if (auto ok = command(kCmdGetId, kAckTimeout); !ok) {
        return std::unexpected{ok.error()};
    }

    std::uint8_t count = 0;
    if (!port_.read(std::span{&count, 1}, kAckTimeout)) {
        return std::unexpected{BootError::Timeout};
    }
    if (count != 1) {
        return std::unexpected{BootError::Protocol}; // очікуємо два байти PID, тобто N = 1
    }

    std::array<std::uint8_t, 2> id{};
    if (!port_.read(id, kAckTimeout)) {
        return std::unexpected{BootError::Timeout};
    }
    if (auto ok = waitAck(kAckTimeout); !ok) {
        return std::unexpected{ok.error()};
    }
    return static_cast<std::uint16_t>((static_cast<std::uint16_t>(id[0]) << 8) | id[1]);
}

Result<void> Bootloader::readoutUnprotect()
{
    if (auto ok = command(kCmdUnprotect, kAckTimeout); !ok) {
        return ok;
    }
    // Другий ACK приходить після того, як чип сам стер Flash; далі він
    // перезавантажується, тож викликач мусить наново зайти в завантажувач.
    return waitAck(kEraseTimeout);
}

Result<void> Bootloader::massErase()
{
    if (auto ok = command(kCmdEraseExt, kAckTimeout); !ok) {
        return ok;
    }
    // Спецкод 0xFFFF — «стерти все», контрольна сума 0xFF ^ 0xFF = 0x00.
    const std::array<std::uint8_t, 3> params{0xFF, 0xFF, 0x00};
    if (!port_.write(params)) {
        return std::unexpected{BootError::Io};
    }
    return waitAck(kEraseTimeout);
}

Result<void> Bootloader::writeBlock(std::uint32_t addr, std::span<const std::uint8_t> data)
{
    if (data.empty() || data.size() > kMaxBlock) {
        return std::unexpected{BootError::Argument};
    }
    if (auto ok = command(kCmdWrite, kAckTimeout); !ok) {
        return ok;
    }
    if (auto ok = address(addr); !ok) {
        return ok;
    }

    // N = len - 1, далі тіло, останній байт — XOR від N і всіх байтів даних.
    std::vector<std::uint8_t> packet;
    packet.reserve(data.size() + 2);

    const auto n = static_cast<std::uint8_t>(data.size() - 1);
    packet.push_back(n);

    std::uint8_t checksum = n;
    for (std::uint8_t byte : data) {
        packet.push_back(byte);
        checksum ^= byte;
    }
    packet.push_back(checksum);

    if (!port_.write(packet)) {
        return std::unexpected{BootError::Io};
    }
    return waitAck(kWriteTimeout);
}

Result<std::vector<std::uint8_t>> Bootloader::readBlock(std::uint32_t addr, std::size_t length)
{
    if (length == 0 || length > kMaxBlock) {
        return std::unexpected{BootError::Argument};
    }
    if (auto ok = command(kCmdRead, kAckTimeout); !ok) {
        return std::unexpected{ok.error()}; // NACK тут — найчастіше RDP level 1
    }
    if (auto ok = address(addr); !ok) {
        return std::unexpected{ok.error()};
    }

    // Кількість байтів і її інверсія як контрольна сума.
    const auto n = static_cast<std::uint8_t>(length - 1);
    const std::array<std::uint8_t, 2> frame{n, static_cast<std::uint8_t>(~n)};
    if (!port_.write(frame)) {
        return std::unexpected{BootError::Io};
    }
    if (auto ok = waitAck(kAckTimeout); !ok) {
        return std::unexpected{ok.error()};
    }

    std::vector<std::uint8_t> data(length);
    if (!port_.read(data, kWriteTimeout)) {
        return std::unexpected{BootError::Timeout};
    }
    return data;
}

Result<void> Bootloader::go(std::uint32_t addr)
{
    if (auto ok = command(kCmdGo, kAckTimeout); !ok) {
        return ok;
    }
    return address(addr);
}
