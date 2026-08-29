#include "sleep.hpp"

namespace lowpower {
namespace {

Stage g_stage = Stage::Awake;

constexpr std::uint8_t kSwoPin = 3U;
constexpr std::uint8_t kSwdioPin = 13U;
constexpr std::uint8_t kSwclkPin = 14U;

void waitForInterrupt(soc::Word lowPowerMode) noexcept
{
    soc::pwr::cr1.modify(soc::pwr::lowPowerModeMask, lowPowerMode);
    soc::core::systemControl.setBits(soc::core::sleepDeep);
    asm volatile("dsb");
    asm volatile("wfi");
    asm volatile("isb");
    soc::core::systemControl.clearBits(soc::core::sleepDeep);
}

[[nodiscard]] std::expected<void, Fault> armRtcTimer(std::chrono::seconds duration) noexcept
{
    soc::rtc::unlock();
    soc::rtc::control.clearBits(soc::rtc::wakeupEnable);

    // Таймер приймає нове значення лише коли сам його відпустив.
    const bool writable = hal::spinUntil(
        []() noexcept { return soc::rtc::status.anyOf(soc::rtc::wakeupWriteAllowed); },
        200'000U);
    if (!writable) {
        soc::rtc::lock();
        return std::unexpected{Fault::RtcTimeout};
    }

    soc::rtc::wakeupTimer.store(static_cast<soc::Word>(duration.count() - 1)); // такт 1 Гц
    soc::rtc::control.modify(0x7U, soc::rtc::clockSelectSecond | soc::rtc::wakeupEnable
                                       | soc::rtc::wakeupInterrupt);
    soc::rtc::status.clearBits(soc::rtc::wakeupFlag);
    soc::rtc::lock();

    soc::exti::pending.store(soc::exti::rtcWakeupLine);
    soc::nvic::pendingClear.store(soc::nvic::rtcWakeupIrq);
    return {};
}

void disarmRtcTimer() noexcept
{
    soc::rtc::unlock();
    soc::rtc::control.clearBits(soc::rtc::wakeupEnable);
    soc::rtc::status.clearBits(soc::rtc::wakeupFlag);
    soc::rtc::lock();
    soc::exti::pending.store(soc::exti::rtcWakeupLine);
}

// Крок 1. Лінії комутованого домену йдуть у нуль, поки шина ще під напругою.
void parkBuses() noexcept
{
    board::parkSwitchedDomain();
    g_stage = Stage::BusesParked;
}

// Крок 2. Ключ розмикається, і ми перевіряємо, що шина справді просіла.
[[nodiscard]] std::expected<void, Fault> cutRail() noexcept
{
    if (g_stage != Stage::BusesParked) {
        return std::unexpected{Fault::OutOfOrder};
    }
    board::railOff();
    g_stage = Stage::RailOff;

    if (board::railIsDischarged()) {
        return {};
    }
    // Одна спроба: часто досить довше потримати лінії в нулі, щоб ємності
    // знеструмленого вузла розрядилися через власне навантаження.
    board::delayFor(std::chrono::milliseconds{10});
    if (board::railIsDischarged()) {
        return {};
    }
    return std::unexpected{Fault::RailStillPowered};
}

// Крок 3. Усе, що не має ролі, втрачає цифровий буфер.
[[nodiscard]] std::expected<void, Fault> isolatePins() noexcept
{
    if (g_stage != Stage::RailOff) {
        return std::unexpected{Fault::OutOfOrder};
    }
    board::allPinsToAnalog();
    g_stage = Stage::PinsAnalog;
    return {};
}

// Крок 4. Блок налагодження перестає тримати генератори.
[[nodiscard]] std::expected<bool, Fault> silenceDebug() noexcept
{
    if (g_stage != Stage::PinsAnalog) {
        return std::unexpected{Fault::OutOfOrder};
    }
    const bool probe = coresight::probeAttached();
    coresight::silence();
    coresight::unfreezePeripherals();
    coresight::relaxSupervisors();
    g_stage = Stage::DebugSilent;
    return probe;
}

// Крок 5. Озброюємо пробудження: таймер RTC і кнопка на WKUP1.
[[nodiscard]] std::expected<void, Fault> armWakeSources(std::chrono::seconds duration) noexcept
{
    if (g_stage != Stage::DebugSilent) {
        return std::unexpected{Fault::OutOfOrder};
    }
    if (duration.count() > 0) {
        if (const auto armed = armRtcTimer(duration); !armed) {
            return armed;
        }
    }
    soc::pwr::scr.store(soc::pwr::clearWakeupFlags);
    soc::pwr::cr4.setBits(soc::pwr::wakeupPin1Falling); // кнопка замикає на землю
    soc::pwr::cr3.setBits(soc::pwr::wakeupPin1);
    g_stage = Stage::WakeArmed;
    return {};
}

// Крок 6. Останній огляд перед WFI.
[[nodiscard]] std::expected<board::FloatingPins, Fault> finalAudit() noexcept
{
    if (g_stage != Stage::WakeArmed) {
        return std::unexpected{Fault::OutOfOrder};
    }
    const bool timerArmed = soc::rtc::control.anyOf(soc::rtc::wakeupEnable);
    const bool buttonArmed = soc::pwr::cr3.anyOf(soc::pwr::wakeupPin1);
    if (!timerArmed && !buttonArmed) {
        return std::unexpected{Fault::NoWakeSource};
    }

    board::FloatingPins report = board::auditFloating();
    if (!report.none()) {
        // Плаваючий вивід — це сотні мікроампер. Замість того щоб заснути
        // з витоком, приводимо виводи в порядок і дивимося ще раз.
        board::allPinsToAnalog();
        report = board::auditFloating();
        if (!report.none()) {
            return std::unexpected{Fault::FloatingPins};
        }
    }
    g_stage = Stage::Ready;
    return report;
}

[[nodiscard]] WakeSource identifyWakeSource() noexcept
{
    WakeSource source = WakeSource::Unknown; // сторонній EXTI: наводка на лінію
    if (soc::pwr::sr1.anyOf(soc::pwr::wakeupFlag1)) {
        source = WakeSource::Button;
    } else if (soc::rtc::status.anyOf(soc::rtc::wakeupFlag)) {
        source = WakeSource::RtcTimer;
    }
    soc::pwr::scr.store(soc::pwr::clearWakeupFlags);
    disarmRtcTimer();
    return source;
}

} // namespace

namespace coresight {

bool probeAttached() noexcept
{
    return soc::core::debugStatus.anyOf(soc::core::debugEnabled);
}

void silence() noexcept
{
    // Головне: жодного утримання тактових дерев під час WFI.
    soc::dbgmcu::control.store(0U);

    // Трасування. TRCENA живить увесь блок DWT/ITM/TPIU, і поки він стоїть,
    // вихідний каскад SWO лишається в режимі надшвидкого фронту.
    soc::trace::itmLock.store(soc::trace::lockKey);
    soc::trace::itmEnable.store(0U);
    soc::trace::itmControl.clearBits(soc::trace::itmEnabledBit);
    soc::trace::dwtControl.clearBits(soc::trace::cycleCounterEnable);
    soc::core::debugExceptionControl.clearBits(soc::core::traceEnabled);

    // Внутрішні підтяжки SWDIO/SWCLK зникають разом з цифровим буфером;
    // зовнішні, у самому зонді, лишаються — тому релізний вимір роблять
    // із від'єднаним шлейфом.
    for (const std::uint8_t pin : {kSwdioPin, kSwclkPin}) {
        soc::portA.setPull(pin, soc::PinPull::None);
        soc::portA.setMode(pin, soc::PinMode::Analog);
    }
    soc::portB.setPull(kSwoPin, soc::PinPull::None);
    soc::portB.setMode(kSwoPin, soc::PinMode::Analog);
}

void unfreezePeripherals() noexcept
{
    soc::dbgmcu::freezeApb1Low.store(0U);
    soc::dbgmcu::freezeApb1High.store(0U);
    soc::dbgmcu::freezeApb2.store(0U);
}

void relaxSupervisors() noexcept
{
    soc::pwr::cr2.clearBits(soc::pwr::voltageDetectorEnable);
    soc::pwr::cr3.setBits(soc::pwr::sampledSupervisors);
}

} // namespace coresight

Stage stage() noexcept { return g_stage; }

std::expected<void, Fault> initRtc() noexcept
{
    soc::pwr::cr1.setBits(soc::pwr::backupDomainWrite);

    if (!soc::rcc::bdcr.anyOf(soc::rcc::lseReady)) {
        soc::rcc::bdcr.setBits(soc::rcc::lseOn);
        const bool started = hal::spinUntil(
            []() noexcept { return soc::rcc::bdcr.anyOf(soc::rcc::lseReady); }, 2'000'000U);
        if (!started) {
            return std::unexpected{Fault::RtcTimeout}; // кварц 32 кГц не завівся
        }
    }

    if (!soc::rcc::bdcr.anyOf(soc::rcc::rtcEnable)) {
        soc::rcc::bdcr.setBits(soc::rcc::rtcSelectLse | soc::rcc::rtcEnable);
    }

    // Без дозволеної лінії EXTI подія таймера не витягне ядро зі Stop2.
    soc::exti::risingTrigger.setBits(soc::exti::rtcWakeupLine);
    soc::exti::interruptMask.setBits(soc::exti::rtcWakeupLine);
    soc::nvic::enableSet.store(soc::nvic::rtcWakeupIrq);
    return {};
}

std::expected<Report, Fault> enterStop2(std::chrono::seconds duration) noexcept
{
    Report report{};
    g_stage = Stage::Awake;

    parkBuses();

    if (const auto cut = cutRail(); !cut) {
        if (cut.error() != Fault::RailStillPowered) {
            return std::unexpected{cut.error()};
        }
        report.railSuspect = true; // дефект плати, але спати однаково треба
    }

    if (const auto isolated = isolatePins(); !isolated) {
        return std::unexpected{isolated.error()};
    }

    const auto probe = silenceDebug();
    if (!probe) {
        return std::unexpected{probe.error()};
    }
    report.probeAttached = *probe;

    if (const auto armed = armWakeSources(duration); !armed) {
        return std::unexpected{armed.error()};
    }

    const auto audit = finalAudit();
    if (!audit) {
        return std::unexpected{audit.error()};
    }
    report.audit = *audit;

    waitForInterrupt(soc::pwr::modeStop2);

    report.source = identifyWakeSource();
    g_stage = Stage::Awake;
    return report;
}

std::expected<void, Fault> enterStandby(std::chrono::seconds duration) noexcept
{
    g_stage = Stage::Awake;
    parkBuses();

    if (const auto cut = cutRail(); !cut && cut.error() != Fault::RailStillPowered) {
        return std::unexpected{cut.error()};
    }
    if (const auto isolated = isolatePins(); !isolated) {
        return std::unexpected{isolated.error()};
    }
    if (const auto probe = silenceDebug(); !probe) {
        return std::unexpected{probe.error()};
    }

    // У Standby конфігурацію GPIO втрачено — рівні задає блок живлення.
    board::applyStandbyPulls();

    if (const auto armed = armWakeSources(duration); !armed) {
        return std::unexpected{armed.error()};
    }

    soc::pwr::scr.store(soc::pwr::clearWakeupFlags | soc::pwr::clearStandbyFlag);
    waitForInterrupt(soc::pwr::modeStandby);

    // Сюди керування не повертається: вихід зі Standby — це скидання.
    // Якщо ми все ж тут, режим не відбувся, і причина зазвичай одна.
    return std::unexpected{coresight::probeAttached() ? Fault::StandbyRefused
                                                      : Fault::OutOfOrder};
}

} // namespace lowpower

// Переривання таймера пробудження. Уся його робота — зняти прапорці,
// інакше подія негайно розбудить ядро вдруге.
extern "C" void RTC_WKUP_IRQHandler()
{
    soc::rtc::unlock();
    soc::rtc::status.clearBits(soc::rtc::wakeupFlag);
    soc::rtc::lock();
    soc::exti::pending.store(soc::exti::rtcWakeupLine);
}
