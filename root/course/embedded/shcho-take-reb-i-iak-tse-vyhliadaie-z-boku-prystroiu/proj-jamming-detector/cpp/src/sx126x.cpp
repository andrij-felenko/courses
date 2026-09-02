#include "ew/sx126x.hpp"

#include <algorithm>
#include <array>

namespace ew {
namespace {

// Коди команд SX1261/1262/1268 (даташит, розділ 13).
constexpr std::uint8_t kCmdReadRegister = 0x1D;
constexpr std::uint8_t kCmdClearIrq = 0x02;
constexpr std::uint8_t kCmdGetIrqStatus = 0x12;
constexpr std::uint8_t kCmdGetPacketStatus = 0x14;
constexpr std::uint8_t kCmdGetRssiInst = 0x15;

// Регістр режиму вхідного підсилення: 0x94 — економний, 0x96 — boosted.
constexpr std::uint16_t kRegRxGain = 0x08AC;
constexpr std::uint8_t  kRxGainPowerSaving = 0x94;

constexpr std::uint16_t kIrqRxDone = 1u << 1;
constexpr std::uint16_t kIrqPreambleDetected = 1u << 2;
constexpr std::uint16_t kIrqSyncWordValid = 1u << 3;
constexpr std::uint16_t kIrqHeaderErr = 1u << 5;
constexpr std::uint16_t kIrqCrcErr = 1u << 6;
constexpr std::uint16_t kIrqAll = 0xFFFF;

constexpr auto kBusyTimeout = std::chrono::microseconds{1000};

// Демодулятор LoRa бере кадр аж до -20 дБ SNR. Якщо кадру не було зовсім,
// фактичне відношення сигнал/шум лежить нижче цієї межі — саме це число і
// чесно віддаємо класифікаторові замість нуля.
constexpr std::int8_t kSnrBelowFloorDb = -20;

constexpr std::byte b(std::uint8_t v) noexcept { return std::byte{v}; }
constexpr std::uint8_t u8(std::byte v) noexcept { return std::to_integer<std::uint8_t>(v); }

// SX126x не публікує крок AGC жодним регістром, тож відновлюємо його з робочої
// точки: чим сильніший вхід, тим нижче тракт мусив опустити підсилення.
// -120 дБм → 255 (максимум LNA), -20 дБм → 0 (вхід у насиченні).
constexpr std::uint8_t agcCode(std::int16_t rssi_dbm, std::uint8_t rx_gain_reg) noexcept
{
    std::int32_t code = 255 - (static_cast<std::int32_t>(rssi_dbm + 120) * 255) / 100;
    code = std::clamp<std::int32_t>(code, 0, 255);
    if (rx_gain_reg == kRxGainPowerSaving) {
        code = std::max<std::int32_t>(code - 20, 0); // тракт уже віддав частину підсилення
    }
    return static_cast<std::uint8_t>(code);
}

} // namespace

std::expected<void, RadioError> Sx126x::command(std::span<const std::byte> tx,
                                                std::span<std::byte> rx) noexcept
{
    if (!bsp::waitBusy(kBusyTimeout)) {
        return std::unexpected(RadioError::Busy);
    }
    if (!bsp::spiTransfer(tx, rx)) {
        return std::unexpected(RadioError::SpiFailure);
    }
    return {};
}

std::expected<std::uint16_t, RadioError> Sx126x::irqStatus() noexcept
{
    // [опкод][статус][IRQ старший][IRQ молодший]
    const std::array tx{b(kCmdGetIrqStatus), b(0), b(0), b(0)};
    std::array<std::byte, tx.size()> rx{};

    if (auto ok = command(tx, rx); !ok) {
        return std::unexpected(ok.error());
    }
    return static_cast<std::uint16_t>((u8(rx[2]) << 8) | u8(rx[3]));
}

std::expected<void, RadioError> Sx126x::clearIrq(std::uint16_t mask) noexcept
{
    const std::array tx{b(kCmdClearIrq), b(static_cast<std::uint8_t>(mask >> 8)),
                        b(static_cast<std::uint8_t>(mask))};
    std::array<std::byte, tx.size()> rx{};
    return command(tx, rx);
}

std::expected<std::int16_t, RadioError> Sx126x::instantRssi() noexcept
{
    const std::array tx{b(kCmdGetRssiInst), b(0), b(0)};
    std::array<std::byte, tx.size()> rx{};

    if (auto ok = command(tx, rx); !ok) {
        return std::unexpected(ok.error());
    }
    // RSSI_дБм = -rssi_raw / 2
    return static_cast<std::int16_t>(-static_cast<std::int16_t>(u8(rx[2])) / 2);
}

std::expected<Sx126x::PacketStatus, RadioError> Sx126x::packetStatus() noexcept
{
    // [опкод][статус][RssiPkt][SnrPkt][SignalRssiPkt]
    const std::array tx{b(kCmdGetPacketStatus), b(0), b(0), b(0), b(0)};
    std::array<std::byte, tx.size()> rx{};

    if (auto ok = command(tx, rx); !ok) {
        return std::unexpected(ok.error());
    }
    return PacketStatus{
        .rssi_pkt_dbm = static_cast<std::int16_t>(-static_cast<std::int16_t>(u8(rx[2])) / 2),
        // SnrPkt — знакове, у чвертях дБ.
        .snr_db = static_cast<std::int8_t>(static_cast<std::int8_t>(u8(rx[3])) / 4)};
}

std::expected<std::uint8_t, RadioError> Sx126x::readRegister(std::uint16_t addr) noexcept
{
    // [опкод][адреса старша][адреса молодша][NOP][дані]
    const std::array tx{b(kCmdReadRegister), b(static_cast<std::uint8_t>(addr >> 8)),
                        b(static_cast<std::uint8_t>(addr)), b(0), b(0)};
    std::array<std::byte, tx.size()> rx{};

    if (auto ok = command(tx, rx); !ok) {
        return std::unexpected(ok.error());
    }
    return u8(rx[4]);
}

std::expected<RfSample, RadioError> Sx126x::readSample() noexcept
{
    const auto irq = irqStatus();
    if (!irq) {
        return std::unexpected(irq.error());
    }

    // Беремо саме миттєвий RSSI, а не рівень пакета: він міряє ефір, зокрема
    // й тоді, коли пакетів немає взагалі — а це і є картина глушіння.
    const auto rssi = instantRssi();
    if (!rssi) {
        return std::unexpected(rssi.error());
    }

    RfSample sample{};
    sample.timestamp = bsp::now();
    sample.rssi_dbm = *rssi;
    sample.preamble = (*irq & (kIrqPreambleDetected | kIrqSyncWordValid)) != 0;
    sample.crc_error = (*irq & (kIrqCrcErr | kIrqHeaderErr)) != 0;

    if ((*irq & (kIrqRxDone | kIrqCrcErr | kIrqHeaderErr)) != 0) {
        const auto status = packetStatus();
        if (!status) {
            return std::unexpected(status.error());
        }
        sample.snr_db = status->snr_db;
    } else {
        sample.snr_db = kSnrBelowFloorDb;
    }

    const auto gain = readRegister(kRegRxGain);
    if (!gain) {
        return std::unexpected(gain.error());
    }
    sample.agc_gain = agcCode(sample.rssi_dbm, *gain);

    // Прапорці треба гасити самому: інакше один-єдиний CRC-збій висітиме в
    // регістрі вічно, і вікно назавжди лишиться «побитим».
    if (auto ok = clearIrq(kIrqAll); !ok) {
        return std::unexpected(ok.error());
    }
    return sample;
}

} // namespace ew
