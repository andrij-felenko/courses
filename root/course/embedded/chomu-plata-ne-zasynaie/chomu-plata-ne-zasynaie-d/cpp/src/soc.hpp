// soc.hpp — периферія STM32L4 як типи й constexpr-об'єкти.
//
// Береться тільки те, що бере участь в аудиті струму спокою: порти,
// тактування, блок живлення, RTC з таймером пробудження, I2C1 і
// налагоджувальна інфраструктура ядра.
#pragma once

#include <cstdint>

#include "mmio.hpp"

namespace soc {

using hal::bit;
using hal::Mmio;
using hal::Word;

enum class PinMode : Word { Input = 0, Output = 1, Alternate = 2, Analog = 3 };
enum class PinPull : Word { None = 0, Up = 1, Down = 2 };

class GpioPort {
public:
    explicit constexpr GpioPort(std::uintptr_t base) noexcept : base_{base} {}

    void setMode(std::uint8_t pin, PinMode mode) const noexcept
    {
        moder().writeField(2U, pin * 2U, static_cast<Word>(mode));
    }

    void setPull(std::uint8_t pin, PinPull pull) const noexcept
    {
        pupdr().writeField(2U, pin * 2U, static_cast<Word>(pull));
    }

    [[nodiscard]] PinMode mode(std::uint8_t pin) const noexcept
    {
        return static_cast<PinMode>(moder().field(2U, pin * 2U));
    }

    [[nodiscard]] PinPull pull(std::uint8_t pin) const noexcept
    {
        return static_cast<PinPull>(pupdr().field(2U, pin * 2U));
    }

    void selectAlternate(std::uint8_t pin, Word function) const noexcept
    {
        const Mmio reg = (pin < 8U) ? afrLow() : afrHigh();
        reg.writeField(4U, (pin % 8U) * 4U, function);
    }

    void setOpenDrain(std::uint8_t pin, bool openDrain) const noexcept
    {
        if (openDrain) {
            otyper().setBits(bit(pin));
        } else {
            otyper().clearBits(bit(pin));
        }
    }

    void write(std::uint8_t pin, bool level) const noexcept
    {
        bsrr().store(level ? bit(pin) : bit(pin + 16U));
    }

    [[nodiscard]] bool read(std::uint8_t pin) const noexcept { return idr().anyOf(bit(pin)); }

    // Аналоговий комутатор L4: розімкнений — до входів АЦП нічого не тягнеться.
    void openAnalogSwitches() const noexcept { ascr().store(0U); }

    [[nodiscard]] constexpr std::uintptr_t base() const noexcept { return base_; }

private:
    [[nodiscard]] constexpr Mmio moder() const noexcept { return Mmio{base_ + 0x00U}; }
    [[nodiscard]] constexpr Mmio otyper() const noexcept { return Mmio{base_ + 0x04U}; }
    [[nodiscard]] constexpr Mmio pupdr() const noexcept { return Mmio{base_ + 0x0CU}; }
    [[nodiscard]] constexpr Mmio idr() const noexcept { return Mmio{base_ + 0x10U}; }
    [[nodiscard]] constexpr Mmio bsrr() const noexcept { return Mmio{base_ + 0x18U}; }
    [[nodiscard]] constexpr Mmio afrLow() const noexcept { return Mmio{base_ + 0x20U}; }
    [[nodiscard]] constexpr Mmio afrHigh() const noexcept { return Mmio{base_ + 0x24U}; }
    [[nodiscard]] constexpr Mmio ascr() const noexcept { return Mmio{base_ + 0x2CU}; }

    std::uintptr_t base_;
};

inline constexpr GpioPort portA{0x4800'0000U};
inline constexpr GpioPort portB{0x4800'0400U};
inline constexpr GpioPort portC{0x4800'0800U};

namespace rcc {
inline constexpr Mmio ahb2enr{0x4002'104CU};
inline constexpr Mmio apb1enr1{0x4002'1058U};
inline constexpr Mmio bdcr{0x4002'1090U};

inline constexpr Word gpioAEnable = bit(0);
inline constexpr Word gpioBEnable = bit(1);
inline constexpr Word gpioCEnable = bit(2);
inline constexpr Word i2c1Enable = bit(21);
inline constexpr Word pwrEnable = bit(28);

inline constexpr Word lseOn = bit(0);
inline constexpr Word lseReady = bit(1);
inline constexpr Word rtcSelectLse = bit(8);
inline constexpr Word rtcEnable = bit(15);
} // namespace rcc

namespace pwr {
inline constexpr Mmio cr1{0x4000'7000U};
inline constexpr Mmio cr2{0x4000'7004U};
inline constexpr Mmio cr3{0x4000'7008U};
inline constexpr Mmio cr4{0x4000'700CU};
inline constexpr Mmio sr1{0x4000'7010U};
inline constexpr Mmio scr{0x4000'7018U};
inline constexpr Mmio pucrA{0x4000'7020U};
inline constexpr Mmio pdcrA{0x4000'7024U};
inline constexpr Mmio pucrB{0x4000'7028U};
inline constexpr Mmio pdcrB{0x4000'702CU};
inline constexpr Mmio pucrC{0x4000'7030U};
inline constexpr Mmio pdcrC{0x4000'7034U};

inline constexpr Word lowPowerModeMask = 0x7U;
inline constexpr Word modeStop2 = 0x2U;
inline constexpr Word modeStandby = 0x3U;
inline constexpr Word backupDomainWrite = bit(8);
inline constexpr Word voltageDetectorEnable = bit(0); // PWR_CR2
inline constexpr Word wakeupPin1 = bit(0);            // PWR_CR3
inline constexpr Word sampledSupervisors = bit(9);    // PWR_CR3: BOR/PVD імпульсно
inline constexpr Word applyPullConfig = bit(10);      // PWR_CR3
inline constexpr Word wakeupPin1Falling = bit(0);     // PWR_CR4
inline constexpr Word wakeupFlag1 = bit(0);           // PWR_SR1
inline constexpr Word clearWakeupFlags = 0x1FU;       // PWR_SCR
inline constexpr Word clearStandbyFlag = bit(8);      // PWR_SCR
} // namespace pwr

namespace rtc {
inline constexpr Mmio control{0x4000'2808U};
inline constexpr Mmio status{0x4000'280CU};
inline constexpr Mmio wakeupTimer{0x4000'2814U};
inline constexpr Mmio writeProtection{0x4000'2824U};
inline constexpr Mmio backup0{0x4000'2850U};
inline constexpr Mmio backup1{0x4000'2854U};

inline constexpr Word clockSelectSecond = 4U << 0;
inline constexpr Word wakeupEnable = bit(10);
inline constexpr Word wakeupInterrupt = bit(14);
inline constexpr Word wakeupWriteAllowed = bit(2);
inline constexpr Word wakeupFlag = bit(10);

inline void unlock() noexcept
{
    writeProtection.store(0xCAU);
    writeProtection.store(0x53U);
}

inline void lock() noexcept { writeProtection.store(0xFFU); }
} // namespace rtc

namespace exti {
inline constexpr Mmio interruptMask{0x4001'0400U};
inline constexpr Mmio risingTrigger{0x4001'0408U};
inline constexpr Mmio pending{0x4001'0414U};
inline constexpr Word rtcWakeupLine = bit(20);
} // namespace exti

namespace nvic {
inline constexpr Mmio enableSet{0xE000'E100U};
inline constexpr Mmio pendingClear{0xE000'E280U};
inline constexpr Word rtcWakeupIrq = bit(3);
} // namespace nvic

namespace core {
inline constexpr Mmio systemControl{0xE000'ED10U};
inline constexpr Mmio debugStatus{0xE000'EDF0U};
inline constexpr Mmio debugExceptionControl{0xE000'EDFCU};
inline constexpr Word sleepDeep = bit(2);
inline constexpr Word debugEnabled = bit(0);
inline constexpr Word traceEnabled = bit(24);
} // namespace core

namespace trace {
inline constexpr Mmio itmEnable{0xE000'0E00U};
inline constexpr Mmio itmControl{0xE000'0E80U};
inline constexpr Mmio itmLock{0xE000'0FB0U};
inline constexpr Mmio dwtControl{0xE000'1000U};
inline constexpr Word lockKey = 0xC5AC'CE55U;
inline constexpr Word itmEnabledBit = bit(0);
inline constexpr Word cycleCounterEnable = bit(0);
} // namespace trace

namespace dbgmcu {
inline constexpr Mmio control{0xE004'2004U};
inline constexpr Mmio freezeApb1Low{0xE004'2008U};
inline constexpr Mmio freezeApb1High{0xE004'200CU};
inline constexpr Mmio freezeApb2{0xE004'2010U};
} // namespace dbgmcu

namespace i2c1 {
inline constexpr Mmio control1{0x4000'5400U};
inline constexpr Mmio control2{0x4000'5404U};
inline constexpr Mmio timing{0x4000'5410U};
inline constexpr Mmio status{0x4000'5418U};
inline constexpr Mmio clearFlags{0x4000'541CU};
inline constexpr Mmio receive{0x4000'5424U};
inline constexpr Mmio transmit{0x4000'5428U};

inline constexpr Word peripheralEnable = bit(0);
inline constexpr Word readTransfer = bit(10);
inline constexpr Word start = bit(13);
inline constexpr Word stop = bit(14);
inline constexpr Word autoEnd = bit(25);
inline constexpr unsigned byteCountShift = 16U;

inline constexpr Word txInterruptStatus = bit(1);
inline constexpr Word rxNotEmpty = bit(2);
inline constexpr Word nackReceived = bit(4);
inline constexpr Word stopDetected = bit(5);
inline constexpr Word transferComplete = bit(6);
inline constexpr Word busError = bit(8);
inline constexpr Word arbitrationLost = bit(9);
inline constexpr Word busy = bit(15);
inline constexpr Word clearAll = 0x0000'3F38U;

// ≈100 кГц при I2CCLK = MSI 4 МГц (саме на цій частоті ядро виходить зі Stop2).
inline constexpr Word timing100kHz = 0x0042'0F13U;
} // namespace i2c1

} // namespace soc
