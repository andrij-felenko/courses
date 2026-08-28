// SpiEmergencyDump.hpp - Низькорівневий драйвер аварійного зливу (C++20)
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>

namespace embedded::drivers {

class EmergencySpiFram {
public:
    static constexpr uint32_t Spi1Base = 0x40013000U;
    static constexpr uint8_t  OpcodeWren  = 0x06U;
    static constexpr uint8_t  OpcodeWrite = 0x02U;

    static void flush_buffer(uint32_t dest_address, std::span<const uint8_t> dump_data) noexcept {
        cs_assert(false);
        transfer_byte(OpcodeWren);
        cs_assert(true);

        cs_assert(false);
        transfer_byte(OpcodeWrite);
        transfer_byte(static_cast<uint8_t>(dest_address >> 16));
        transfer_byte(static_cast<uint8_t>(dest_address >> 8));
        transfer_byte(static_cast<uint8_t>(dest_address & 0xFFU));

        for (const uint8_t byte : dump_data) {
            transfer_byte(byte);
        }
        cs_assert(true);
    }

private:
    static void cs_assert(bool state) noexcept {
        auto* const bsrr = reinterpret_cast<volatile uint32_t*>(0x40020000U + 0x18U);
        *bsrr = state ? (1U << 4) : (1U << (4 + 16));
    }

    static uint8_t transfer_byte(uint8_t byte) noexcept {
        auto* const sr = reinterpret_cast<volatile uint32_t*>(Spi1Base + 0x08U);
        auto* const dr = reinterpret_cast<volatile uint32_t*>(Spi1Base + 0x0CU);

        while (!(*sr & (1U << 1))) { /* Очікування TXE */ }
        *dr = byte;
        while (*sr & (1U << 7))     { /* Очікування BSY */ }
        return static_cast<uint8_t>(*dr);
    }
};

} // namespace embedded::drivers
