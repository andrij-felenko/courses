/* flight_recorder.cpp - C++20 реалізація методів реєстратора */
#include "flight_recorder.hpp"
#include <cstring>

namespace notary::diagnostics {

uint32_t FlightRecorder::calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (uint8_t byte : data) {
        crc ^= static_cast<uint32_t>(byte);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 1U) {
                crc = (crc >> 1U) ^ 0xEDB88320U;
            } else {
                crc = (crc >> 1U);
            }
        }
    }
    return ~crc;
}

void FlightRecorder::initialize(uint32_t raw_reset_status, uint32_t boot_counter) noexcept {
    if (storage_.size() < sizeof(CrashDump)) return;

    auto* dump = reinterpret_cast<CrashDump*>(storage_.data());
    uint8_t flags = static_cast<uint8_t>(ResetCause::Unknown);

    if (raw_reset_status & (1U << 25)) flags |= static_cast<uint8_t>(ResetCause::BrownOut);
    if (raw_reset_status & (1U << 26)) flags |= static_cast<uint8_t>(ResetCause::PinReset);
    if (raw_reset_status & (1U << 29)) flags |= static_cast<uint8_t>(ResetCause::Watchdog);
    if (raw_reset_status & (1U << 27)) flags |= static_cast<uint8_t>(ResetCause::Software);

    dump->boot_count = boot_counter;
    dump->last_reset_flags = flags;
}

void FlightRecorder::log_power_drop(uint16_t vdd_mv, int16_t temp_c_x10) noexcept {
    if (storage_.size() < sizeof(CrashDump)) return;

    pvd_event_counter_++;
    auto* dump = reinterpret_cast<CrashDump*>(storage_.data());
    dump->supply_mv = vdd_mv;
    dump->die_temp_c_x10 = temp_c_x10;
    dump->brownout_count = pvd_event_counter_;
}

void FlightRecorder::capture_hardfault(uint32_t cfsr, uint32_t hfsr, uint32_t bfar,
                                      uint32_t lr, uint32_t pc, uint16_t vdd, int16_t temp) noexcept {
    if (storage_.size() < sizeof(CrashDump)) return;

    auto* dump = reinterpret_cast<CrashDump*>(storage_.data());
    dump->magic = CrashDump::MagicIdentifier;
    dump->version = CrashDump::CurrentVersion;
    dump->cfsr = cfsr;
    dump->hfsr = hfsr;
    dump->bfar = bfar;
    dump->lr = lr;
    dump->pc = pc;
    dump->supply_mv = vdd;
    dump->die_temp_c_x10 = temp;
    dump->brownout_count = pvd_event_counter_;
    dump->bus_error_count = bus_error_counter_;

    constexpr size_t payload_len = offsetof(CrashDump, crc32);
    dump->crc32 = calculate_crc32(std::span<const uint8_t>(storage_.data(), payload_len));
}

std::expected<CrashDump, DumpError> FlightRecorder::load_and_verify() const noexcept {
    if (storage_.size() < sizeof(CrashDump)) {
        return std::unexpected(DumpError::EmptyStorage);
    }

    CrashDump dump;
    std::memcpy(&dump, storage_.data(), sizeof(CrashDump));

    if (dump.magic != CrashDump::MagicIdentifier) {
        return std::unexpected(DumpError::InvalidMagic);
    }
    if (dump.version != CrashDump::CurrentVersion) {
        return std::unexpected(DumpError::VersionMismatch);
    }

    constexpr size_t payload_len = offsetof(CrashDump, crc32);
    const uint32_t computed = calculate_crc32(std::span<const uint8_t>(storage_.data(), payload_len));

    if (dump.crc32 != computed) {
        return std::unexpected(DumpError::CrcMismatch);
    }

    return dump;
}

void FlightRecorder::erase_log() noexcept {
    if (!storage_.empty()) {
        std::fill(storage_.begin(), storage_.end(), 0);
    }
}

} // namespace notary::diagnostics
