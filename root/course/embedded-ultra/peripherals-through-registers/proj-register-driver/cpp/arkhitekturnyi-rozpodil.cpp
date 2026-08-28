#include <cstdint>
#include <concepts>

/* Базові адреси периферійних блоків */
namespace MemoryMap {
    inline constexpr std::uintptr_t PeriphBase     = 0x40000000UL;
    inline constexpr std::uintptr_t Apb1Base       = PeriphBase;
    inline constexpr std::uintptr_t Ahb1Base       = PeriphBase + 0x00020000UL;

    inline constexpr std::uintptr_t RccBase        = Ahb1Base + 0x3800UL;
    inline constexpr std::uintptr_t GpioABase      = Ahb1Base + 0x0000UL;
    inline constexpr std::uintptr_t Tim6Base       = Apb1Base + 0x1000UL;
}

/* Шаблонна типізована обгортка апаратного регістра з нульовою ціною абстракції */
template <std::uintptr_t Address, typename T = std::uint32_t>
struct HardwareRegister {
    static void write(T value) noexcept {
        *reinterpret_cast<volatile T*>(Address) = value;
    }

    [[nodiscard]] static T read() noexcept {
        return *reinterpret_cast<volatile T*>(Address);
    }

    static void setBits(T mask) noexcept {
        *reinterpret_cast<volatile T*>(Address) = read() | mask;
    }

    static void clearBits(T mask) noexcept {
        *reinterpret_cast<volatile T*>(Address) = read() & ~mask;
    }
};

/* Опис зміщень регістрів GPIO */
struct GpioRegisters {
    volatile std::uint32_t MODER;
    volatile std::uint32_t OTYPER;
    volatile std::uint32_t OSPEEDR;
    volatile std::uint32_t PUPDR;
    volatile std::uint32_t IDR;
    volatile std::uint32_t ODR;
    volatile std::uint32_t BSRR;
    volatile std::uint32_t LCKR;
    volatile std::uint32_t AFR[2];
};

/* Опис зміщень регістрів базового таймера */
struct TimerRegisters {
    volatile std::uint32_t CR1;
    volatile std::uint32_t CR2;
    std::uint32_t          RESERVED0;
    volatile std::uint32_t DIER;
    volatile std::uint32_t SR;
    volatile std::uint32_t EGR;
    std::uint32_t          RESERVED1[3];
    volatile std::uint32_t CNT;
    volatile std::uint32_t PSC;
    volatile std::uint32_t ARR;
};
