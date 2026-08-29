// Доступ до заліза STM32L4: описи блоків, кілька примітивів ядра і сторож
// заборони переривань. Збирається як -std=c++23 -fno-exceptions -fno-rtti.
#pragma once

#include <chrono>
#include <cstdint>

namespace mcu {

// Після скидання ядро йде від MSI 4 МГц.
inline constexpr std::uint32_t kCpuHz = 4'000'000U;

using u32 = std::uint32_t;

// reg |= bit на volatile-змінній з C++20 оголошено застарілим: у виразі
// ховаються два різні звертання до заліза, і стандарт більше не гарантує їх
// порядку. Тому читання-модифікація-запис виписані явно й одним місцем.
inline void set_bits(volatile u32& reg, u32 mask) noexcept { reg = reg | mask; }
inline void clear_bits(volatile u32& reg, u32 mask) noexcept { reg = reg & ~mask; }
inline void modify(volatile u32& reg, u32 clear, u32 set) noexcept
{
    reg = (reg & ~clear) | set;
}

// ------------------------------ порти ------------------------------------

struct GpioBlock {
    volatile u32 moder;   // режим виводу, два біти на вивід
    volatile u32 otyper;  // 0 — двотактний, 1 — відкритий стік
    volatile u32 ospeedr;
    volatile u32 pupdr;   // внутрішні підтяжки
    volatile u32 idr;
    volatile u32 odr;
    volatile u32 bsrr;    // атомарна установка/скидання
    volatile u32 lckr;
    volatile u32 afr[2];
    volatile u32 brr;
};

enum class Mode : u32 { Input = 0, Output = 1, Alternate = 2, Analog = 3 };
enum class Pull : u32 { None = 0, Up = 1, Down = 2 };

template <typename T>
[[nodiscard]] inline T& at(std::uintptr_t address) noexcept
{
    return *reinterpret_cast<T*>(address);
}

[[nodiscard]] inline GpioBlock& gpioa() noexcept { return at<GpioBlock>(0x4800'0000U); }
[[nodiscard]] inline GpioBlock& gpiob() noexcept { return at<GpioBlock>(0x4800'0400U); }
[[nodiscard]] inline GpioBlock& gpioc() noexcept { return at<GpioBlock>(0x4800'0800U); }

// Вивід як значення: порт і номер разом, щоб не тягати їх окремими аргументами.
class Pin {
public:
    constexpr Pin(GpioBlock& port, unsigned number) noexcept
        : port_{&port}, number_{number} {}

    [[nodiscard]] GpioBlock& port() const noexcept { return *port_; }
    [[nodiscard]] unsigned number() const noexcept { return number_; }
    [[nodiscard]] u32 mask() const noexcept { return 1U << number_; }

    void mode(Mode m) const noexcept
    {
        const unsigned shift = number_ * 2U;
        port_->moder = (port_->moder & ~(0b11U << shift)) |
                       (static_cast<u32>(m) << shift);
    }

    void pull(Pull p) const noexcept
    {
        const unsigned shift = number_ * 2U;
        port_->pupdr = (port_->pupdr & ~(0b11U << shift)) |
                       (static_cast<u32>(p) << shift);
    }

    void open_drain(bool on) const noexcept
    {
        if (on) { set_bits(port_->otyper, mask()); }
        else { clear_bits(port_->otyper, mask()); }
    }

    void alternate(u32 af) const noexcept
    {
        const unsigned half = number_ >> 3U;
        const unsigned shift = (number_ & 7U) * 4U;
        port_->afr[half] = (port_->afr[half] & ~(0xFU << shift)) | (af << shift);
        mode(Mode::Alternate);
    }

    // Через BSRR, а не читанням-модифікацією ODR: сусідній вивід того ж порту
    // може змінювати обробник переривання просто між читанням і записом.
    void write(bool level) const noexcept
    {
        port_->bsrr = level ? mask() : (mask() << 16U);
    }

    [[nodiscard]] bool read() const noexcept { return (port_->idr & mask()) != 0U; }

private:
    GpioBlock* port_;
    unsigned number_;
};

// --------------------------- решта блоків --------------------------------

struct RccBlock {
    volatile u32 cr, icscr, cfgr, pllcfgr, pllsai1cfgr, pllsai2cfgr;
    volatile u32 cier, cifr, cicr, reserved0;
    volatile u32 ahb1rstr, ahb2rstr, ahb3rstr, reserved1;
    volatile u32 apb1rstr1, apb1rstr2, apb2rstr, reserved2;
    volatile u32 ahb1enr, ahb2enr, ahb3enr, reserved3;
    volatile u32 apb1enr1, apb1enr2, apb2enr, reserved4;
    volatile u32 ahb1smenr, ahb2smenr, ahb3smenr, reserved5;
    volatile u32 apb1smenr1, apb1smenr2, apb2smenr, reserved6;
    volatile u32 ccipr, reserved7;
    volatile u32 bdcr, csr;
};

struct PwrBlock {
    volatile u32 cr1, cr2, cr3, cr4;
    volatile u32 sr1, sr2, scr, reserved0;
    volatile u32 pucra, pdcra, pucrb, pdcrb, pucrc, pdcrc;
};

struct UsartBlock {
    volatile u32 cr1, cr2, cr3, brr, gtpr, rtor, rqr, isr, icr, rdr, tdr;
};

struct SpiBlock {
    volatile u32 cr1, cr2, sr, dr;
};

struct I2cBlock {
    volatile u32 cr1, cr2, oar1, oar2, timingr, timeoutr;
    volatile u32 isr, icr, pecr, rxdr, txdr;
};

struct ExtiBlock {
    volatile u32 imr1, emr1, rtsr1, ftsr1, swier1, pr1;
};

struct SyscfgBlock {
    volatile u32 memrmp, cfgr1, exticr[4];
};

struct RtcBlock {
    volatile u32 tr, dr, cr, isr, prer, wutr, reserved0;
    volatile u32 alrmar, alrmbr, wpr;
};

[[nodiscard]] inline RccBlock&    rcc()    noexcept { return at<RccBlock>(0x4002'1000U); }
[[nodiscard]] inline PwrBlock&    pwr()    noexcept { return at<PwrBlock>(0x4000'7000U); }
[[nodiscard]] inline UsartBlock&  usart2() noexcept { return at<UsartBlock>(0x4000'4400U); }
[[nodiscard]] inline SpiBlock&    spi1()   noexcept { return at<SpiBlock>(0x4001'3000U); }
[[nodiscard]] inline I2cBlock&    i2c1()   noexcept { return at<I2cBlock>(0x4000'5400U); }
[[nodiscard]] inline ExtiBlock&   exti()   noexcept { return at<ExtiBlock>(0x4001'0400U); }
[[nodiscard]] inline SyscfgBlock& syscfg() noexcept { return at<SyscfgBlock>(0x4001'0000U); }
[[nodiscard]] inline RtcBlock&    rtc()    noexcept { return at<RtcBlock>(0x4000'2800U); }

[[nodiscard]] inline volatile u32& scb_scr() noexcept { return at<volatile u32>(0xE000'ED10U); }
// DBGMCU_CR і є той «завжди ввімкнений вузол»: поки в ньому стоять біти
// налагодження, тактове дерево живе крізь Stop.
[[nodiscard]] inline volatile u32& dbgmcu_cr() noexcept { return at<volatile u32>(0xE004'2004U); }

namespace bits {
inline constexpr u32 kRccGpioAEn   = 1U << 0;
inline constexpr u32 kRccGpioBEn   = 1U << 1;
inline constexpr u32 kRccGpioCEn   = 1U << 2;
inline constexpr u32 kRccRtcApbEn  = 1U << 10;
inline constexpr u32 kRccUsart2En  = 1U << 17;
inline constexpr u32 kRccI2c1En    = 1U << 21;
inline constexpr u32 kRccPwrEn     = 1U << 28;
inline constexpr u32 kRccSyscfgEn  = 1U << 0;
inline constexpr u32 kRccSpi1En    = 1U << 12;

inline constexpr u32 kBdcrLseOn    = 1U << 0;
inline constexpr u32 kBdcrLseRdy   = 1U << 1;
inline constexpr u32 kBdcrRtcSelLse = 1U << 8;
inline constexpr u32 kBdcrRtcEn    = 1U << 15;

inline constexpr u32 kPwrLpmsMask  = 0x7U;
inline constexpr u32 kPwrLpmsStop2 = 0x2U;
inline constexpr u32 kPwrDbp       = 1U << 8;
inline constexpr u32 kPwrScrCwuf   = 0x1FU;

inline constexpr u32 kUsartUe      = 1U << 0;
inline constexpr u32 kUsartTe      = 1U << 3;
inline constexpr u32 kUsartIsrTxe  = 1U << 7;
inline constexpr u32 kUsartIsrTc   = 1U << 6;   // кадр повністю вийшов на лінію

inline constexpr u32 kSpiSpe       = 1U << 6;
inline constexpr u32 kSpiSrBsy     = 1U << 7;
inline constexpr u32 kSpiSrFtlvl   = 0b11U << 11;

inline constexpr u32 kI2cPe        = 1U << 0;
inline constexpr u32 kI2cRdWrn     = 1U << 10;
inline constexpr u32 kI2cStart     = 1U << 13;
inline constexpr u32 kI2cAutoEnd   = 1U << 25;
inline constexpr u32 kI2cIsrTxis   = 1U << 1;
inline constexpr u32 kI2cIsrRxne   = 1U << 2;
inline constexpr u32 kI2cIsrNackf  = 1U << 4;
inline constexpr u32 kI2cIsrStopf  = 1U << 5;
inline constexpr u32 kI2cIsrTc     = 1U << 6;
inline constexpr u32 kI2cIsrBusy   = 1U << 15;
inline constexpr u32 kI2cIcrNackcf = 1U << 4;
inline constexpr u32 kI2cIcrStopcf = 1U << 5;

inline constexpr u32 kScrSleepDeep = 1U << 2;

inline constexpr u32 kDbgSleep     = 1U << 0;
inline constexpr u32 kDbgStop      = 1U << 1;
inline constexpr u32 kDbgStandby   = 1U << 2;

inline constexpr u32 kRtcWute      = 1U << 10;
inline constexpr u32 kRtcWutie     = 1U << 14;
inline constexpr u32 kRtcWucksel1Hz = 4U << 0;
inline constexpr u32 kRtcIsrWutwf  = 1U << 2;
inline constexpr u32 kRtcIsrWutf   = 1U << 10;
} // namespace bits

[[nodiscard]] constexpr u32 i2c_addr(u32 addr7) noexcept { return (addr7 << 1) & 0x3FFU; }
[[nodiscard]] constexpr u32 i2c_nbytes(u32 n) noexcept { return (n & 0xFFU) << 16; }

// ---------------------------- ядро й час ---------------------------------

inline constexpr unsigned kIrqRtcWakeup = 3U;
inline constexpr unsigned kIrqExti0 = 6U;

inline void nvic_enable(unsigned irq) noexcept
{
    at<volatile u32>(0xE000'E100U + 4U * (irq >> 5U)) = 1U << (irq & 31U);
}

inline void nvic_clear_pending(unsigned irq) noexcept
{
    at<volatile u32>(0xE000'E280U + 4U * (irq >> 5U)) = 1U << (irq & 31U);
}

inline void dsb() noexcept { asm volatile("dsb 0xF" ::: "memory"); }
inline void isb() noexcept { asm volatile("isb 0xF" ::: "memory"); }
inline void wfi() noexcept { asm volatile("wfi"); }

// Заборона переривань як область видимості: пара cpsid/cpsie руками рано чи
// пізно розходиться на ранньому return, а сторож — ні.
class IrqLock {
public:
    IrqLock() noexcept { asm volatile("cpsid i" ::: "memory"); }
    ~IrqLock() noexcept { asm volatile("cpsie i" ::: "memory"); }

    IrqLock(const IrqLock&) = delete;
    IrqLock& operator=(const IrqLock&) = delete;
};

// Затримка порожнім циклом. Лічильник тактів DWT був би точнішим, але він
// живе в тому самому блоці трасування, який ця стаття вчить вимикати.
inline void delay(std::chrono::microseconds us) noexcept
{
    auto loops = static_cast<u32>(us.count() * (kCpuHz / 1'000'000U) / 4);
    while (loops-- != 0U) { asm volatile("nop"); }
}

inline void delay(std::chrono::milliseconds ms) noexcept
{
    for (auto left = ms.count(); left > 0; --left) {
        delay(std::chrono::microseconds{1000});
    }
}

} // namespace mcu
