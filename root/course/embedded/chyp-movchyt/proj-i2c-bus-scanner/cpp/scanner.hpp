/* Перебір адресного простору й читання результату як діагнозу */
#pragma once

#include <cstdint>
#include <optional>
#include <print>
#include <vector>

#include "bit_bang_master.hpp"

/* Робочий діапазон 7-бітних адрес: 0x00..0x07 і 0x78..0x7F стандарт
   віддав під General Call, CBUS, 10-бітний префікс і Device ID. */
inline constexpr std::uint8_t first_addr = 0x08;
inline constexpr std::uint8_t last_addr = 0x77;
inline constexpr std::size_t addr_space = last_addr - first_addr + 1;

struct ScanReport {
    std::vector<std::uint8_t> found;
    unsigned nacks = 0;   /* порожня адреса — це нормальний стан, а не збій */
    unsigned errors = 0;  /* транзакція не відбулася взагалі — це дефект ліній */
    std::optional<BusError> last_error;
};

enum class Verdict {
    device_as_expected,
    address_mismatch,
    phantom_all_ack,
    silent_but_healthy,
    lines_broken
};

template <OpenDrainLines Lines>
[[nodiscard]] ScanReport scan_range(BitBangMaster<Lines>& master) {
    ScanReport report;
    report.found.reserve(4);

    std::println("Сканування 0x{:02X}..0x{:02X}...", first_addr, last_addr);

    for (std::uint8_t addr = first_addr; addr <= last_addr; ++addr) {
        const auto result = master.probe(addr);

        if (result) {
            report.found.push_back(addr);
            std::println("  ACK: 7-бітна адреса 0x{:02X} (байт запису 0x{:02X}, байт читання 0x{:02X})",
                         addr, addr << 1, (addr << 1) | 1);
        } else if (result.error() == BusError::nack) {
            ++report.nacks;
        } else {
            ++report.errors;
            report.last_error = result.error();
        }
    }

    std::println("Підсумок: вузлів {}, NACK {}, помилок шини {}",
                 report.found.size(), report.nacks, report.errors);
    return report;
}

[[nodiscard]] Verdict classify(const ScanReport& report, std::uint8_t expected_addr) noexcept;
void print_report(const ScanReport& report, std::uint8_t expected_addr, Verdict verdict);
