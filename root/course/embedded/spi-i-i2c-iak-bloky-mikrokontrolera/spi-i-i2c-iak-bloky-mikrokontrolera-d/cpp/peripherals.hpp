#pragma once

#include <cstdint>

// Регістри STM32F4 (RM0090) для SPI1, I2C1, GPIO і DMA2.
// Замість макросів — constexpr-константи в іменованих просторах: компілятор
// бачить типи, а імена прапорців не течуть у весь проєкт.
namespace mcu {

struct SpiRegs {
    volatile std::uint32_t cr1, cr2, sr, dr;
    volatile std::uint32_t crcpr, rxcrcr, txcrcr, i2scfgr, i2spr;
};

namespace spi_cr1 {
inline constexpr std::uint32_t cpha = 1u << 0;
inline constexpr std::uint32_t cpol = 1u << 1;
inline constexpr std::uint32_t mstr = 1u << 2;
inline constexpr std::uint32_t brPos = 3u;
inline constexpr std::uint32_t spe = 1u << 6;
inline constexpr std::uint32_t ssi = 1u << 8;
inline constexpr std::uint32_t ssm = 1u << 9;
}  // namespace spi_cr1

namespace spi_cr2 {
inline constexpr std::uint32_t rxdmaen = 1u << 0;
inline constexpr std::uint32_t txdmaen = 1u << 1;
inline constexpr std::uint32_t errie = 1u << 5;
inline constexpr std::uint32_t rxneie = 1u << 6;
inline constexpr std::uint32_t txeie = 1u << 7;
}  // namespace spi_cr2

namespace spi_sr {
inline constexpr std::uint32_t rxne = 1u << 0;
inline constexpr std::uint32_t txe = 1u << 1;
inline constexpr std::uint32_t modf = 1u << 5;
inline constexpr std::uint32_t ovr = 1u << 6;
inline constexpr std::uint32_t bsy = 1u << 7;
}  // namespace spi_sr

struct I2cRegs {
    volatile std::uint32_t cr1, cr2, oar1, oar2, dr, sr1, sr2, ccr, trise, fltr;
};

namespace i2c_cr1 {
inline constexpr std::uint32_t pe = 1u << 0;
inline constexpr std::uint32_t start = 1u << 8;
inline constexpr std::uint32_t stop = 1u << 9;
inline constexpr std::uint32_t ack = 1u << 10;
inline constexpr std::uint32_t pos = 1u << 11;
inline constexpr std::uint32_t swrst = 1u << 15;
}  // namespace i2c_cr1

namespace i2c_sr1 {
inline constexpr std::uint32_t sb = 1u << 0;
inline constexpr std::uint32_t addr = 1u << 1;
inline constexpr std::uint32_t btf = 1u << 2;
inline constexpr std::uint32_t rxne = 1u << 6;
inline constexpr std::uint32_t txe = 1u << 7;
inline constexpr std::uint32_t berr = 1u << 8;
inline constexpr std::uint32_t arlo = 1u << 9;
inline constexpr std::uint32_t af = 1u << 10;
}  // namespace i2c_sr1

namespace i2c_sr2 {
inline constexpr std::uint32_t busy = 1u << 1;
}

namespace i2c_ccr {
inline constexpr std::uint32_t fastMode = 1u << 15;
}

struct GpioRegs {
    volatile std::uint32_t moder, otyper, ospeedr, pupdr;
    volatile std::uint32_t idr, odr, bsrr, lckr;
    volatile std::uint32_t afr[2];
};

struct DmaStreamRegs {
    volatile std::uint32_t cr, ndtr, par, m0ar, m1ar, fcr;
};

struct DmaRegs {
    volatile std::uint32_t lisr, hisr, lifcr, hifcr;
    DmaStreamRegs stream[8];
};

namespace dma_cr {
inline constexpr std::uint32_t enable = 1u << 0;
inline constexpr std::uint32_t transferErrorIrq = 1u << 2;
inline constexpr std::uint32_t transferCompleteIrq = 1u << 4;
inline constexpr std::uint32_t memToPeriph = 1u << 6;
inline constexpr std::uint32_t memIncrement = 1u << 10;
inline constexpr std::uint32_t priorityHigh = 2u << 16;
inline constexpr std::uint32_t channelPos = 25u;
}  // namespace dma_cr

struct RccRegs {
    volatile std::uint32_t cr, pllcfgr, cfgr, cir;
    volatile std::uint32_t ahb1rstr, ahb2rstr, ahb3rstr, reserved0;
    volatile std::uint32_t apb1rstr, apb2rstr, reserved1[2];
    volatile std::uint32_t ahb1enr, ahb2enr, ahb3enr, reserved2;
    volatile std::uint32_t apb1enr, apb2enr;
};

namespace rcc_bits {
inline constexpr std::uint32_t gpioaEn = 1u << 0;
inline constexpr std::uint32_t gpiobEn = 1u << 1;
inline constexpr std::uint32_t dma2En = 1u << 22;
inline constexpr std::uint32_t i2c1En = 1u << 21;
inline constexpr std::uint32_t spi1En = 1u << 12;
}  // namespace rcc_bits

inline constexpr std::uintptr_t rccBase = 0x40023800u;
inline constexpr std::uintptr_t gpioaBase = 0x40020000u;
inline constexpr std::uintptr_t gpiobBase = 0x40020400u;
inline constexpr std::uintptr_t spi1Base = 0x40013000u;
inline constexpr std::uintptr_t i2c1Base = 0x40005400u;
inline constexpr std::uintptr_t dma2Base = 0x40026400u;

inline RccRegs& rcc() noexcept { return *reinterpret_cast<RccRegs*>(rccBase); }
inline GpioRegs& gpioA() noexcept { return *reinterpret_cast<GpioRegs*>(gpioaBase); }
inline GpioRegs& gpioB() noexcept { return *reinterpret_cast<GpioRegs*>(gpiobBase); }
inline SpiRegs& spi1() noexcept { return *reinterpret_cast<SpiRegs*>(spi1Base); }
inline I2cRegs& i2c1() noexcept { return *reinterpret_cast<I2cRegs*>(i2c1Base); }
inline DmaRegs& dma2() noexcept { return *reinterpret_cast<DmaRegs*>(dma2Base); }

enum class Irq : std::uint8_t { Spi1 = 35, Dma2Stream2 = 58, Dma2Stream3 = 59 };

inline void enableIrq(Irq irq) noexcept
{
    auto n = static_cast<std::uint32_t>(irq);
    auto* iser = reinterpret_cast<volatile std::uint32_t*>(0xE000E100u);
    iser[n >> 5] = 1u << (n & 31u);
}

// Груба затримка холостим циклом: ядро 168 МГц, тіло ~4 такти.
inline void delayUs(std::uint32_t us) noexcept
{
    volatile std::uint32_t n = us * 42u;
    while (n--) {
        asm volatile("nop");
    }
}

// Налаштування однієї ніжки — те, що в C розписано трьома масками підряд.
enum class PinMode : std::uint32_t { Input = 0, Output = 1, Alternate = 2 };

inline void configurePin(GpioRegs& port, unsigned pin, PinMode mode,
                         bool openDrain, unsigned altFunction = 0) noexcept
{
    const unsigned shift2 = pin * 2u;
    port.otyper = openDrain ? (port.otyper | (1u << pin)) : (port.otyper & ~(1u << pin));
    port.pupdr = (port.pupdr & ~(3u << shift2)) | (1u << shift2);  // підтяжка вгору
    port.ospeedr |= 3u << shift2;
    if (mode == PinMode::Alternate) {
        const unsigned idx = pin / 8u;
        const unsigned shift4 = (pin % 8u) * 4u;
        port.afr[idx] = (port.afr[idx] & ~(0xFu << shift4)) | (altFunction << shift4);
    }
    port.moder = (port.moder & ~(3u << shift2)) | (static_cast<std::uint32_t>(mode) << shift2);
}

inline void writePin(GpioRegs& port, unsigned pin, bool level) noexcept
{
    port.bsrr = level ? (1u << pin) : (1u << (pin + 16u));
}

inline bool readPin(const GpioRegs& port, unsigned pin) noexcept
{
    return (port.idr & (1u << pin)) != 0u;
}

}  // namespace mcu
