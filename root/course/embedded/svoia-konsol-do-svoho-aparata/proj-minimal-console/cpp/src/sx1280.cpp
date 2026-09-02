#include "sx1280.hpp"

#include <algorithm>
#include <utility>

namespace console {
namespace {

constexpr auto kBusyTimeout = std::chrono::microseconds{2000};
constexpr std::uint32_t kRfHz = 2440000000u;
constexpr std::uint32_t kXtalHz = 52000000u;

// Синхрослово FLRC займає старші чотири байти поля SyncAddress1.
constexpr std::uint16_t kRegFlrcSyncWord1 = 0x09CF;

constexpr std::uint8_t kStandbyRc = 0x00;
constexpr std::uint8_t kPacketTypeFlrc = 0x03;
constexpr std::uint8_t kBr1300Bw1200 = 0x45;
constexpr std::uint8_t kCodingRate34 = 0x02;
constexpr std::uint8_t kGaussian05 = 0x20;
constexpr std::uint8_t kPreamble32Bits = 0x70;
constexpr std::uint8_t kSyncLen4Bytes = 0x04;
constexpr std::uint8_t kMatchSync1 = 0x10;
constexpr std::uint8_t kFixedLength = 0x00;
constexpr std::uint8_t kCrcOff = 0x00;
constexpr std::uint8_t kWhiteningOff = 0x08;
constexpr std::uint8_t kRamp20us = 0xE0;
constexpr std::uint8_t kPeriodBase15us = 0x00;
constexpr std::uint8_t kPeriodBase1ms = 0x02;

constexpr std::uint32_t toPllSteps(std::uint32_t hz) noexcept
{
    // Крок сітки — XTAL/2^18 ≈ 198.36 Гц; ділимо в 64 бітах.
    return static_cast<std::uint32_t>((static_cast<std::uint64_t>(hz) << 18) / kXtalHz);
}

}   // namespace

void Sx1280::reset() noexcept
{
    hal::write(hal::Pin::RadioNss, true);
    hal::write(hal::Pin::RadioReset, false);
    hal::delay(std::chrono::microseconds{200});
    hal::write(hal::Pin::RadioReset, true);
    hal::delay(std::chrono::milliseconds{3});   // чипу треба ~2.5 мс на старт
}

std::expected<void, RadioError> Sx1280::exchange(std::size_t length, bool needRx) noexcept
{
    if (length > tx_.size()) {
        return std::unexpected{RadioError::BadLength};
    }
    if (!SpiBus::waitIdle(hal::Pin::RadioBusy, kBusyTimeout)) {
        return std::unexpected{RadioError::Busy};
    }

    const ChipSelect cs{hal::Pin::RadioNss};
    if (needRx) {
        bus_.transfer(std::span{tx_}.first(length), std::span{rx_}.first(length));
    } else {
        bus_.write(std::span{tx_}.first(length));
    }
    return {};
}

std::expected<void, RadioError> Sx1280::command(Opcode op,
                                                std::span<const std::uint8_t> params) noexcept
{
    if (params.size() + 1 > tx_.size()) {
        return std::unexpected{RadioError::BadLength};
    }
    tx_[0] = static_cast<std::byte>(std::to_underlying(op));
    std::ranges::transform(params, tx_.begin() + 1,
                           [](std::uint8_t v) { return static_cast<std::byte>(v); });
    return exchange(params.size() + 1, false);
}

std::expected<void, RadioError> Sx1280::query(Opcode op, std::span<std::uint8_t> out) noexcept
{
    const std::size_t total = out.size() + 2;   // опкод, NOP зі статусом, дані
    if (total > tx_.size()) {
        return std::unexpected{RadioError::BadLength};
    }
    tx_.fill(std::byte{0});
    tx_[0] = static_cast<std::byte>(std::to_underlying(op));

    if (auto r = exchange(total, true); !r) {
        return r;
    }
    std::transform(rx_.begin() + 2, rx_.begin() + static_cast<std::ptrdiff_t>(total), out.begin(),
                   [](std::byte b) { return static_cast<std::uint8_t>(b); });
    return {};
}

std::expected<void, RadioError> Sx1280::writeRegister(std::uint16_t address,
                                                      std::span<const std::uint8_t> data) noexcept
{
    if (data.size() + 3 > tx_.size()) {
        return std::unexpected{RadioError::BadLength};
    }
    tx_[0] = static_cast<std::byte>(std::to_underlying(Opcode::WriteRegister));
    tx_[1] = static_cast<std::byte>(address >> 8);
    tx_[2] = static_cast<std::byte>(address & 0xFF);
    std::ranges::transform(data, tx_.begin() + 3,
                           [](std::uint8_t v) { return static_cast<std::byte>(v); });
    return exchange(data.size() + 3, false);
}

std::expected<void, RadioError> Sx1280::begin() noexcept
{
    reset();

    // GetStatus віддає відповідь уже другим байтом, без NOP-затримки.
    tx_.fill(std::byte{0});
    tx_[0] = static_cast<std::byte>(std::to_underlying(Opcode::GetStatus));
    if (auto r = exchange(2, true); !r) {
        return r;
    }
    const auto mode = static_cast<std::uint8_t>((std::to_integer<std::uint8_t>(rx_[1]) >> 5) & 0x07);
    if (mode == 0x00 || mode == 0x07) {
        return std::unexpected{RadioError::NotResponding};
    }

    const std::uint32_t pll = toPllSteps(kRfHz);
    const std::array<std::uint8_t, 3> freq{static_cast<std::uint8_t>(pll >> 16),
                                           static_cast<std::uint8_t>(pll >> 8),
                                           static_cast<std::uint8_t>(pll)};
    const std::array<std::uint8_t, 3> modulation{kBr1300Bw1200, kCodingRate34, kGaussian05};
    const std::array<std::uint8_t, 7> packet{kPreamble32Bits, kSyncLen4Bytes, kMatchSync1,
                                             kFixedLength,    payloadLength_, kCrcOff,
                                             kWhiteningOff};
    // +13 dBm на виході чипа, далі зовнішній PA дотягує до +20 dBm.
    const std::array<std::uint8_t, 2> power{0x1F, kRamp20us};
    const std::array<std::uint8_t, 4> syncWord{0x54, 0x69, 0x96, 0x1E};

    constexpr std::uint16_t mask = irq::TxDone | irq::RxDone | irq::CrcError | irq::RxTxTimeout;
    const std::array<std::uint8_t, 8> dio{
        static_cast<std::uint8_t>(mask >> 8), static_cast<std::uint8_t>(mask),   // загальна маска
        static_cast<std::uint8_t>(mask >> 8), static_cast<std::uint8_t>(mask),   // те саме на DIO1
        0, 0, 0, 0};

    const std::array<std::uint8_t, 1> standby{kStandbyRc};
    const std::array<std::uint8_t, 1> regulator{0x01};   // DC-DC: на платі є дросель
    const std::array<std::uint8_t, 1> type{kPacketTypeFlrc};
    const std::array<std::uint8_t, 2> base{0x00, 0x00};

    if (auto r = command(Opcode::SetStandby, standby); !r) return r;
    if (auto r = command(Opcode::SetRegulatorMode, regulator); !r) return r;
    if (auto r = command(Opcode::SetPacketType, type); !r) return r;
    if (auto r = command(Opcode::SetRfFrequency, freq); !r) return r;
    if (auto r = command(Opcode::SetBufferBase, base); !r) return r;
    if (auto r = command(Opcode::SetModulationParams, modulation); !r) return r;
    if (auto r = writeRegister(kRegFlrcSyncWord1, syncWord); !r) return r;
    if (auto r = command(Opcode::SetPacketParams, packet); !r) return r;
    if (auto r = command(Opcode::SetTxParams, power); !r) return r;
    if (auto r = command(Opcode::SetDioIrqParams, dio); !r) return r;

    return clearIrq(irq::All);
}

std::expected<void, RadioError> Sx1280::transmit(std::span<const std::byte> payload) noexcept
{
    if (payload.size() + 2 > tx_.size()) {
        return std::unexpected{RadioError::BadLength};
    }
    if (auto r = clearIrq(irq::All); !r) {
        return r;
    }

    tx_[0] = static_cast<std::byte>(std::to_underlying(Opcode::WriteBuffer));
    tx_[1] = std::byte{0x00};
    std::ranges::copy(payload, tx_.begin() + 2);
    if (auto r = exchange(payload.size() + 2, false); !r) {
        return r;
    }

    // Апаратний таймаут 3 мс: якщо передача зірветься, чип сам вийде в STDBY
    // і не залишить підсилювач ввімкненим.
    const std::array<std::uint8_t, 3> params{kPeriodBase1ms, 0x00, 0x03};
    return command(Opcode::SetTx, params);
}

std::expected<void, RadioError> Sx1280::listen(std::chrono::microseconds window) noexcept
{
    if (auto r = clearIrq(irq::All); !r) {
        return r;
    }
    const auto ticks = std::min<std::uint32_t>(
        static_cast<std::uint32_t>(window.count() * 64 / 1000), 0xFFFFu);   // крок 15.625 мкс
    const std::array<std::uint8_t, 3> params{kPeriodBase15us,
                                             static_cast<std::uint8_t>(ticks >> 8),
                                             static_cast<std::uint8_t>(ticks)};
    return command(Opcode::SetRx, params);
}

std::expected<std::uint16_t, RadioError> Sx1280::irqStatus() noexcept
{
    std::array<std::uint8_t, 2> raw{};
    if (auto r = query(Opcode::GetIrqStatus, raw); !r) {
        return std::unexpected{r.error()};
    }
    return static_cast<std::uint16_t>((static_cast<std::uint16_t>(raw[0]) << 8) | raw[1]);
}

std::expected<void, RadioError> Sx1280::clearIrq(std::uint16_t mask) noexcept
{
    const std::array<std::uint8_t, 2> params{static_cast<std::uint8_t>(mask >> 8),
                                             static_cast<std::uint8_t>(mask)};
    return command(Opcode::ClearIrqStatus, params);
}

std::expected<std::uint16_t, RadioError> Sx1280::waitIrq(std::uint16_t mask,
                                                         std::chrono::microseconds limit) noexcept
{
    const auto start = hal::now();
    for (;;) {
        // Спершу дивимося на DIO1: читати регістр щоразу означало б тримати
        // шину зайнятою й красти в дисплея його вікно.
        if (hal::read(hal::Pin::RadioDio1)) {
            const auto status = irqStatus();
            if (!status) {
                return status;
            }
            if (*status & mask) {
                if (auto r = clearIrq(*status); !r) {
                    return std::unexpected{r.error()};
                }
                return *status;
            }
        }
        if (hal::now() - start > limit) {
            return std::unexpected{RadioError::Timeout};
        }
    }
}

std::expected<Reception, RadioError> Sx1280::read() noexcept
{
    std::array<std::uint8_t, 2> status{};
    if (auto r = query(Opcode::GetRxBufferStatus, status); !r) {
        return std::unexpected{r.error()};
    }
    const std::size_t length = status[0];
    if (length == 0 || length + 3 > tx_.size()) {
        return std::unexpected{RadioError::BadLength};
    }

    tx_.fill(std::byte{0});
    tx_[0] = static_cast<std::byte>(std::to_underlying(Opcode::ReadBuffer));
    tx_[1] = static_cast<std::byte>(status[1]);
    // Третій такт — NOP: дані з буфера чипа йдуть починаючи з нього.
    if (auto r = exchange(length + 3, true); !r) {
        return std::unexpected{r.error()};
    }

    std::array<std::uint8_t, 5> packetStatus{};
    if (query(Opcode::GetPacketStatus, packetStatus)) {
        lastRssi_ = -static_cast<int>(packetStatus[0]) / 2;
    }
    return Reception{std::span<const std::byte>{rx_.data() + 3, length}, lastRssi_};
}

std::expected<void, RadioError> Sx1280::standby() noexcept
{
    const std::array<std::uint8_t, 1> params{kStandbyRc};
    return command(Opcode::SetStandby, params);
}

}   // namespace console
