#include "crash_report.hpp"

#include "platform.hpp"

#include <cstring>

namespace diag {
namespace {

// Секція .noinit НЕ обнуляється стартовим кодом: після теплого рестарту
// (сторож, HardFault, програмний reset) вміст цих байтів лишається тим
// самим, бо живлення ядра не зникало. Скрипт компонування мусить
// розмістити секцію в SRAM і не включати її ні в .bss, ні в таблицю
// копіювання .data.
[[gnu::section(".noinit"), gnu::used]] CrashReport g_report;

// CRC-16/CCITT-FALSE. Журнал живе в пам'яті, яку могло зачепити
// просідання живлення. Без контрольної суми ми показали б сервісному
// інженеру телеметрію з випадкового сміття — це гірше за чесне
// «журнал утрачено».
[[nodiscard]] std::uint16_t crc16(std::span<const std::byte> data) noexcept
{
    std::uint16_t crc = 0xFFFFU;
    for (const std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(std::to_integer<std::uint8_t>(b)) << 8;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000U) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021U)
                                  : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

void seal() noexcept
{
    g_report.crc = g_report.checksum();
}

void wipe() noexcept
{
    std::memset(&g_report, 0, sizeof(g_report));
    g_report.magic = CrashReport::magic_value;
    g_report.cause = ResetCause::unknown;
    g_report.panic = PanicReason::none;
}

// Порядок перевірки не довільний: прапорці накопичуються, і після подачі
// живлення разом із por_rst апаратно виставляється й pin_rst. Тому спершу
// дивимося на «неприємні» причини — сторож і просідання, — і лише потім
// на нормальні.
[[nodiscard]] ResetCause decode(std::uint32_t flags) noexcept
{
    using namespace stm32::rcc;

    if ((flags & iwdg_rst) != 0U) {
        return ResetCause::independent_watchdog;
    }
    if ((flags & wwdg_rst) != 0U) {
        return ResetCause::window_watchdog;
    }
    if ((flags & bor_rst) != 0U && (flags & por_rst) == 0U) {
        return ResetCause::brown_out;
    }
    if ((flags & soft_rst) != 0U) {
        return ResetCause::software;
    }
    if ((flags & low_power_rst) != 0U) {
        return ResetCause::low_power;
    }
    if ((flags & por_rst) != 0U) {
        return ResetCause::power_on;
    }
    if ((flags & pin_rst) != 0U) {
        return ResetCause::pin;
    }
    return ResetCause::unknown;
}

[[nodiscard]] bool is_fault_cause(ResetCause cause) noexcept
{
    return cause == ResetCause::independent_watchdog ||
           cause == ResetCause::window_watchdog ||
           cause == ResetCause::brown_out;
}

} // namespace

std::span<const std::byte> CrashReport::payload() const noexcept
{
    return {reinterpret_cast<const std::byte*>(this), offsetof(CrashReport, crc)};
}

std::uint16_t CrashReport::checksum() const noexcept
{
    return crc16(payload());
}

bool CrashReport::intact() const noexcept
{
    return magic == magic_value && crc == checksum();
}

ResetCause Journal::begin_boot() noexcept
{
    const std::uint32_t flags = stm32::rcc::csr::read();
    // Прапорці треба зняти тут-таки, інакше наступний старт побачить
    // суміш причин і звинуватить сторожа в чужому гріху.
    stm32::rcc::csr::set(stm32::rcc::rmvf);

    const ResetCause cause = decode(flags);
    const bool cold = cause == ResetCause::power_on || cause == ResetCause::unknown;

    if (cold || !g_report.intact()) {
        wipe();
    }

    ++g_report.boot_count;
    g_report.cause = cause;
    g_report.raw_reset_flags = flags;
    g_report.uptime_ms = 0U;

    if (is_fault_cause(cause)) {
        ++g_report.fault_count;
        // Сторож і просідання не лишають ані PC, ані CFSR: ядро просто
        // зникло. Причину ставимо лише тоді, коли її ще не записав
        // обробник збою перед рестартом.
        if (g_report.panic == PanicReason::none) {
            g_report.panic = (cause == ResetCause::brown_out) ? PanicReason::brown_out
                                                              : PanicReason::assertion;
        }
    }

    seal();
    return cause;
}

void Journal::record(PanicReason reason, const FaultContext& context) noexcept
{
    if (!g_report.intact()) {
        wipe();
    }
    g_report.panic = reason;
    g_report.fault = context;
    seal();
}

void Journal::note_safe_state() noexcept
{
    if (!g_report.intact()) {
        wipe();
    }
    ++g_report.safe_state_entries;
    seal();
}

void Journal::note_uptime(std::uint32_t ms) noexcept
{
    if (!g_report.intact()) {
        return;
    }
    g_report.uptime_ms = ms;
    seal();
}

std::expected<CrashReport, JournalError> Journal::load() noexcept
{
    if (g_report.magic != CrashReport::magic_value) {
        return std::unexpected{JournalError::uninitialised};
    }
    if (g_report.crc != g_report.checksum()) {
        return std::unexpected{JournalError::checksum_mismatch};
    }
    return g_report;
}

std::string_view to_string(ResetCause cause) noexcept
{
    using enum ResetCause;
    switch (cause) {
    case power_on:             return "POWER_ON";
    case pin:                  return "PIN";
    case brown_out:            return "BROWN_OUT";
    case software:             return "SOFTWARE";
    case independent_watchdog: return "IWDG";
    case window_watchdog:      return "WWDG";
    case low_power:            return "LOW_POWER";
    case unknown:              break;
    }
    return "UNKNOWN";
}

std::string_view to_string(PanicReason reason) noexcept
{
    using enum PanicReason;
    switch (reason) {
    case hard_fault:     return "HARDFAULT";
    case assertion:      return "ASSERTION";
    case sensor_timeout: return "SENSOR_TIMEOUT";
    case bus_stuck:      return "BUS_STUCK";
    case loop_too_fast:  return "LOOP_TOO_FAST";
    case brown_out:      return "BROWN_OUT";
    case none:           break;
    }
    return "NONE";
}

std::string_view to_string(JournalError error) noexcept
{
    switch (error) {
    case JournalError::uninitialised:     return "ЖУРНАЛ ПОРОЖНІЙ";
    case JournalError::checksum_mismatch: return "ЖУРНАЛ ПОШКОДЖЕНО";
    }
    return "?";
}

} // namespace diag
