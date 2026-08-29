#include "wakeup.hpp"

namespace lowpower::wakeup {

// Не анонімний простір імен: до цих імен дотягуються обробники переривань,
// які за правилами мови живуть у глобальному просторі.
namespace detail {

const mcu::Pin kButton{mcu::gpioa(), 0};
constexpr mcu::u32 kExtiLineButton = 1U << 0;
constexpr mcu::u32 kExtiLineRtc = 1U << 20;  // лінія 20 — будильник RTC

volatile bool woken_by_button = false;
volatile bool woken_by_rtc = false;

// Захист від запису в регістри RTC знімається двома ключами з даташита.
inline void unlock_rtc() { mcu::rtc().wpr = 0xCAU; mcu::rtc().wpr = 0x53U; }
inline void lock_rtc()   { mcu::rtc().wpr = 0xFFU; }

} // namespace detail

using namespace std::chrono_literals;
using namespace detail;

namespace {

void init_rtc_clock()
{
    auto& rcc = mcu::rcc();
    mcu::set_bits(rcc.apb1enr1, mcu::bits::kRccPwrEn | mcu::bits::kRccRtcApbEn);
    mcu::set_bits(mcu::pwr().cr1, mcu::bits::kPwrDbp);  // без цього домен RTC не пускає запис

    if ((rcc.bdcr & mcu::bits::kBdcrRtcEn) != 0U) {
        return;  // RTC уже йде; переінакшувати його означало б збити час
    }

    mcu::set_bits(rcc.bdcr, mcu::bits::kBdcrLseOn);
    // Годинниковий кварц заводиться повільно — сотні мілісекунд.
    for (int left = 2000; left > 0 && (rcc.bdcr & mcu::bits::kBdcrLseRdy) == 0U; --left) {
        mcu::delay(1ms);
    }

    mcu::set_bits(rcc.bdcr, mcu::bits::kBdcrRtcSelLse | mcu::bits::kBdcrRtcEn);
}

} // namespace

void init()
{
    mcu::set_bits(mcu::rcc().apb2enr, mcu::bits::kRccSyscfgEn);
    mcu::clear_bits(mcu::syscfg().exticr[0], 0xFU);  // лінію EXTI0 бере порт A (код 0)

    kButton.mode(mcu::Mode::Input);
    // Кнопка замикає на землю, тому підтяжка вгору потрібна. Це та сама
    // підтяжка, що тягне струм увесь сон: 40 кОм на 3.3 В — 82 мкА, поки
    // кнопку тримають натиснутою. Ціна за живий вхід.
    kButton.pull(mcu::Pull::Up);

    auto& exti = mcu::exti();
    mcu::set_bits(exti.ftsr1, kExtiLineButton);  // натискання — це спадний фронт
    exti.pr1 = kExtiLineButton;
    mcu::set_bits(exti.imr1, kExtiLineButton);
    mcu::nvic_clear_pending(mcu::kIrqExti0);
    mcu::nvic_enable(mcu::kIrqExti0);

    init_rtc_clock();

    mcu::set_bits(exti.rtsr1, kExtiLineRtc);
    exti.pr1 = kExtiLineRtc;
    mcu::set_bits(exti.imr1, kExtiLineRtc);
    mcu::nvic_clear_pending(mcu::kIrqRtcWakeup);
    mcu::nvic_enable(mcu::kIrqRtcWakeup);
}

void arm(std::chrono::seconds after)
{
    auto& rtc = mcu::rtc();
    unlock_rtc();

    mcu::clear_bits(rtc.cr, mcu::bits::kRtcWute);
    // Лічильник можна переписувати лише тоді, коли залізо це дозволило.
    for (int left = 1000; left > 0 && (rtc.isr & mcu::bits::kRtcIsrWutwf) == 0U; --left) {
        mcu::delay(100us);
    }

    const auto ticks = (after.count() > 0) ? static_cast<mcu::u32>(after.count() - 1) : 0U;
    rtc.wutr = ticks;
    rtc.cr = (rtc.cr & ~0x7U) | mcu::bits::kRtcWucksel1Hz;
    mcu::clear_bits(rtc.isr, mcu::bits::kRtcIsrWutf);
    mcu::set_bits(rtc.cr, mcu::bits::kRtcWute | mcu::bits::kRtcWutie);

    lock_rtc();
}

void clear_pending()
{
    // Черга переривань мусить бути порожня в момент WFI. Незнятий прапорець
    // будить ядро тієї ж миті, і зовні це виглядає так, ніби плата взагалі не
    // засинає: споживання лишається робочим, а програма крутиться далі.
    unlock_rtc();
    mcu::clear_bits(mcu::rtc().isr, mcu::bits::kRtcIsrWutf);
    lock_rtc();

    mcu::exti().pr1 = kExtiLineButton | kExtiLineRtc;
    mcu::nvic_clear_pending(mcu::kIrqExti0);
    mcu::nvic_clear_pending(mcu::kIrqRtcWakeup);

    woken_by_button = false;
    woken_by_rtc = false;
}

std::optional<WakeReason> last_reason()
{
    if (woken_by_button) { return WakeReason::Button; }
    if (woken_by_rtc) { return WakeReason::Rtc; }
    return std::nullopt;
}

} // namespace lowpower::wakeup

// Обробники лише знімають прапорці й називають причину: усе інше робиться в
// головному циклі, куди ядро повертається одразу після WFI.
extern "C" void EXTI0_IRQHandler()
{
    namespace d = lowpower::wakeup::detail;
    mcu::exti().pr1 = d::kExtiLineButton;
    d::woken_by_button = true;
}

extern "C" void RTC_WKUP_IRQHandler()
{
    namespace d = lowpower::wakeup::detail;
    d::unlock_rtc();
    mcu::clear_bits(mcu::rtc().isr, mcu::bits::kRtcIsrWutf);
    d::lock_rtc();

    mcu::exti().pr1 = d::kExtiLineRtc;
    d::woken_by_rtc = true;
}
