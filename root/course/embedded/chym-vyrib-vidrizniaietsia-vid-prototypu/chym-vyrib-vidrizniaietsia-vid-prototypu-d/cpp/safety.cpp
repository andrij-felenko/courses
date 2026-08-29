#include "safety.hpp"

#include "platform.hpp"
#include "telemetry.hpp"

#include <array>
#include <atomic>

namespace safety {
namespace {

// Розкладка керування силовою частиною на GPIOA:
//   PA8  — TIM1_CH1, верхнє плече мостового драйвера (альтернативна функція)
//   PA7  — TIM1_CH1N, нижнє плече
//   PA9  — ENABLE драйвера моста, активний високий
//   PA10 — реле відсікання силового живлення, активне високе
inline constexpr unsigned pin_driver_enable = 9U;
inline constexpr unsigned pin_main_relay = 10U;

// Обидва прапорці читає й пише обробник винятку, тож звичайного bool
// замало навіть на одноядерному Cortex-M.
std::atomic<bool> g_energised{false};
std::atomic<bool> g_latched{false};

void make_output_low(unsigned pin) noexcept
{
    using namespace stm32::gpioa;

    // Спершу рівень, потім напрямок: інакше між перемиканням у вихід
    // і записом нуля вивід на кілька тактів віддає невизначений рівень,
    // і драйвер моста встигає клацнути.
    write_pin(pin, false);

    otyper::clear(1U << pin);              // двотактний вихід
    set_pull(pin, Pull::down);
    ospeedr::set(1U << (pin * 2U));
    set_mode(pin, Mode::output);

    write_pin(pin, false);
}

void stages_off() noexcept
{
    using namespace stm32;

    // Головний дозвіл виходів таймера. Один запис у BDTR миттєво переводить
    // усі канали в неактивний стан — це швидше за роботу з окремими ніжками.
    tim1::bdtr::clear(tim1::moe);
    tim1::ccer::clear(tim1::cc1e | tim1::cc1ne);
    tim1::ccr1::write(0U);
    tim1::cr1::clear(tim1::cen);

    // Далі — окремі лінії дозволу драйвера й силового реле.
    gpioa::write_pin(pin_driver_enable, false);
    gpioa::write_pin(pin_main_relay, false);
    hw::dsb();

    g_energised.store(false, std::memory_order_release);
}

} // namespace

void PowerStage::arm_outputs() noexcept
{
    using namespace stm32;

    rcc::ahb1enr::set(rcc::gpioa_en);
    rcc::apb2enr::set(rcc::tim1_en);
    hw::dsb();

    // Таймер міг лишитися ввімкненим від попереднього запуску: теплий
    // рестарт скидає ядро, але не завжди зупиняє периферію на тому самому
    // такті. Гасимо виходи ще до налаштування ніжок.
    stages_off();

    make_output_low(pin_driver_enable);
    make_output_low(pin_main_relay);

    // Прапорець аварії живе у звичайній RAM і після теплого рестарту міг
    // лишитися виставленим. Старт — це нова спроба; рішення про блокування
    // ухвалюють за журналом, а не за сміттям у неініціалізованій змінній.
    g_latched.store(false, std::memory_order_release);
    g_energised.store(false, std::memory_order_release);
}

bool PowerStage::enable() noexcept
{
    if (g_latched.load(std::memory_order_acquire)) {
        // Один раз зафіксувавшись в аварії, ми з неї не виходимо без
        // рестарту: інакше прошивка, яка «полікувалася» сама, поверне рух
        // приводу, причини аварії так і не з'ясувавши.
        return false;
    }

    using namespace stm32;
    gpioa::write_pin(pin_main_relay, true);
    gpioa::write_pin(pin_driver_enable, true);

    tim1::ccer::set(tim1::cc1e | tim1::cc1ne);
    tim1::bdtr::set(tim1::moe);
    tim1::cr1::set(tim1::cen);

    g_energised.store(true, std::memory_order_release);
    return true;
}

void PowerStage::release() noexcept
{
    stages_off();
}

void PowerStage::shutdown() noexcept
{
    const bool was_latched = g_latched.exchange(true, std::memory_order_acq_rel);
    stages_off();

    // Лічильник рахує ПОДІЇ, а не виклики: обробник збою може зайти сюди
    // двічі, і другий раз — це та сама аварія.
    if (!was_latched) {
        diag::Journal::note_safe_state();
    }
}

bool PowerStage::energised() noexcept
{
    return g_energised.load(std::memory_order_acquire);
}

bool PowerStage::latched() noexcept
{
    return g_latched.load(std::memory_order_acquire);
}

PowerStageGuard::PowerStageGuard(bool permitted) noexcept
    : armed_{permitted && PowerStage::enable()}
{
}

PowerStageGuard::~PowerStageGuard() noexcept
{
    if (armed_) {
        // Вихід з області видимості означає, що керувати рухом більше
        // нікому. Каскад гасимо, але аварії не оголошуємо: це штатний
        // кінець сеансу керування, а не збій.
        PowerStage::release();
    }
}

void SupplyMonitor::init() noexcept
{
    using namespace stm32;

    rcc::apb1enr::set(rcc::pwr_en);
    hw::dsb();

    pwr::cr::modify(pwr::pls::mask, pwr::pls::of(pwr::level_2v9) | pwr::pvde);
}

bool SupplyMonitor::sagging() noexcept
{
    return stm32::pwr::csr::any(stm32::pwr::pvdo);
}

namespace {

[[noreturn]] void finish(diag::PanicReason reason, const diag::FaultContext& context) noexcept
{
    // 1. Механіка. Переривання вимикаємо ПІСЛЯ знеструмлення: робота
    //    з BDTR і BSRR — це кілька записів у регістри, вони не потребують
    //    переривань, зате будь-яка затримка тут коштує руху.
    PowerStage::shutdown();
    hw::disable_irq();

    // 2. Діагностика.
    diag::Journal::record(reason, context);

    // 3. Останнє слово в діагностичний порт — на випадок, якщо пристрій
    //    зараз на столі в сервісі й радіоканалу немає.
    std::array<char, 192> scratch{};
    if (const auto report = diag::Journal::load(); report) {
        diag::Telemetry::line(diag::Telemetry::render(*report, scratch));
    } else {
        diag::Telemetry::line(diag::to_string(report.error()));
    }

    // 4. Рестарт. Не «продовжуємо як є» і не зависаємо назавжди:
    //    пристрій у полі має спробувати піднятися сам.
    stm32::system_reset();
}

} // namespace

void panic(diag::PanicReason reason) noexcept
{
    const diag::FaultContext context{
        .pc = static_cast<std::uint32_t>(
            reinterpret_cast<std::uintptr_t>(__builtin_return_address(0))),
        .lr = 0U,
        .sp = hw::main_stack_pointer(),
        .cfsr = stm32::scb::cfsr::read(),
    };
    finish(reason, context);
}

void panic(diag::PanicReason reason, const diag::FaultContext& context) noexcept
{
    finish(reason, context);
}

} // namespace safety
