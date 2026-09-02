#pragma once

#include <cstdint>

// Доступ до регістрів, відображених у пам'ять, і адреси тих блоків STM32F103,
// яких вимагає обв'язка плати.
namespace mmio {

// Адреса — параметр шаблона, тож регістр існує як окремий ТИП: переплутати
// два регістри в рантаймі неможливо, а звертання лишається одним записом.
template <std::uintptr_t Address>
struct Reg {
    static std::uint32_t read() noexcept {
        return *reinterpret_cast<volatile std::uint32_t *>(Address);
    }
    static void write(std::uint32_t value) noexcept {
        *reinterpret_cast<volatile std::uint32_t *>(Address) = value;
    }
    static void setBits(std::uint32_t mask) noexcept { write(read() | mask); }
    static void clearBits(std::uint32_t mask) noexcept { write(read() & ~mask); }
    static void modify(std::uint32_t clearMask, std::uint32_t setMask) noexcept {
        write((read() & ~clearMask) | setMask);
    }
};

}  // namespace mmio

namespace soc {

// Після скидання ядро тактує внутрішній генератор HSI: 8 МГц, PLL не вмикаємо.
inline constexpr std::uint32_t kCpuHz = 8'000'000;

inline constexpr std::uintptr_t kRccApb2Enr = 0x40021000 + 0x18;
inline constexpr std::uintptr_t kRccApb1Enr = 0x40021000 + 0x1C;
inline constexpr std::uint32_t kAfioEn = 1u << 0;
inline constexpr std::uint32_t kIopaEn = 1u << 2;
inline constexpr std::uint32_t kIopcEn = 1u << 4;
inline constexpr std::uint32_t kTim3En = 1u << 1;

inline constexpr std::uintptr_t kGpioA = 0x40010800;
inline constexpr std::uintptr_t kGpioC = 0x40011000;
inline constexpr std::uintptr_t kAfioBase = 0x40010000;
inline constexpr std::uintptr_t kExtiBase = 0x40010400;
inline constexpr std::uintptr_t kTim3Base = 0x40000400;
inline constexpr std::uintptr_t kSysTickBase = 0xE000E010;
inline constexpr std::uintptr_t kNvicIser0 = 0xE000E100;

inline constexpr unsigned kExti0Irq = 6;
inline constexpr unsigned kTim3Irq = 29;

}  // namespace soc
