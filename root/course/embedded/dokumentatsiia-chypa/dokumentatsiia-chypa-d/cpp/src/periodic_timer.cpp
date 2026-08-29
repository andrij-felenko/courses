#include "hw/periodic_timer.hpp"

#include <utility>

#include "hw/clock_gate.hpp"
#include "hw/registers.hpp"

namespace hw {
namespace {

/* Проміжна частота лічильника: один такт = одна мікросекунда, тому ARR
 * читається просто як період у мікросекундах. */
constexpr Hertz tick_hz = 1'000'000U;
constexpr Hertz rate_hz = 1'000U;

/* Лічильник мілісекунд. volatile обов'язковий: значення змінює обробник
 * переривання, а головний цикл його читає. Без volatile компілятор має
 * право зчитати змінну один раз до циклу й більше до пам'яті не ходити. */
volatile std::uint32_t g_ticks = 0;

} // namespace

std::expected<PeriodicTimer, TimerError> PeriodicTimer::start_1khz(Hertz timer_clock) noexcept
{
    /* Арифметику перевіряємо ДО того, як щось поїхало в залізо. Мовчазне
     * округлення тут коштувало б дрейфу годинника, який шукають тижнями. */
    if (timer_clock < tick_hz) {
        return std::unexpected{TimerError::clock_too_slow};
    }
    if (timer_clock % tick_hz != 0U) {
        return std::unexpected{TimerError::clock_not_exact};
    }

    const std::uint32_t prescaler = timer_clock / tick_hz - 1U;
    if (prescaler > 0xFFFFU) {
        return std::unexpected{TimerError::prescaler_overflow};
    }
    const std::uint32_t reload = tick_hz / rate_hz - 1U;  // 999

    /* Крок 1. Тактування, потім скидання блоку: жодних припущень про те,
     * що лишив у регістрах завантажувач чи попередній запуск. */
    clocks::enable_apb1(rcc_bits::apb1en_tim2);
    clocks::reset_apb1(rcc_bits::apb1rst_tim2);

    /* Крок 2 (виводи) цьому режиму не потрібен: таймер рахує всередині
     * кристала й піднімає лише лінію переривання до NVIC. */

    TimerBlock& timer = tim2();

    /* Крок 3. Конфігурація при вимкненому блоці. */
    timer.cr1  = 0;                 // CEN = 0
    timer.dier = 0;                 // жодних переривань під час набору
    timer.psc  = prescaler;
    timer.arr  = reload;
    timer.cnt  = 0;

    /* URS = 1: запит переривання дає лише переповнення. Без цього біта
     * програмна подія UG нижче теж викликала б обробник. */
    timer.cr1 |= tim_bits::cr1_urs;

    /* PSC і ARR буферовані: залізо переносить їх у робочі тіньові копії за
     * подією оновлення (RM0090 §18.4.11). Генеруємо цю подію самі. */
    timer.egr = tim_bits::egr_ug;

    /* UG усе одно підняв UIF. TIMx_SR має тип доступу rc_w0: нуль скидає
     * біт, одиниця не діє. Тому пишемо одиниці всюди, крім UIF, — сусідні
     * прапорці цілі, а циклу read-modify-write, у якому залізо могло б
     * втратити щойно піднятий прапорець, просто немає. */
    timer.sr = ~tim_bits::sr_uif;

    /* Крок 4. Дозволи й активація. NVIC — це вже Programming Manual. */
    timer.dier |= tim_bits::dier_uie;
    nvic_enable(tim2_irqn, 0x08U);

    g_ticks = 0;
    timer.cr1 |= tim_bits::cr1_cen;

    return PeriodicTimer{};
}

PeriodicTimer::PeriodicTimer(PeriodicTimer&& other) noexcept
    : owns_{std::exchange(other.owns_, false)}
{
}

PeriodicTimer& PeriodicTimer::operator=(PeriodicTimer&& other) noexcept
{
    if (this != &other) {
        release();
        owns_ = std::exchange(other.owns_, false);
    }
    return *this;
}

PeriodicTimer::~PeriodicTimer()
{
    release();
}

void PeriodicTimer::release() noexcept
{
    if (!owns_) {
        return;
    }
    owns_ = false;

    TimerBlock& timer = tim2();
    timer.cr1  &= ~tim_bits::cr1_cen;
    timer.dier &= ~tim_bits::dier_uie;

    /* Запит міг дійти до NVIC, поки ми знімали дозвіл у самому таймері:
     * знімаємо вектор і гасимо прапорець, щоб обробник не викликався після
     * знищення об'єкта. */
    nvic_disable(tim2_irqn);
    timer.sr = ~tim_bits::sr_uif;
    dsb();

    clocks::disable_apb1(rcc_bits::apb1en_tim2);
}

std::uint32_t PeriodicTimer::ticks() const noexcept
{
    /* 32-бітне вирівняне читання на Cortex-M атомарне — блокувати
     * переривання заради нього не треба. */
    return g_ticks;
}

} // namespace hw

/* Ім'я вектора беруть із таблиці переривань стартового коду, тому потрібне
 * сишне зв'язування — інакше компонувальник шукатиме спотворене ім'я. */
extern "C" void TIM2_IRQHandler()
{
    using namespace hw;

    TimerBlock& timer = tim2();

    /* Перевіряємо і прапорець, і дозвіл: один вектор обслуговує всі події
     * таймера, а прапорець без дозволу чекає на інший код. */
    if ((timer.sr & tim_bits::sr_uif) != 0U && (timer.dier & tim_bits::dier_uie) != 0U) {
        timer.sr = ~tim_bits::sr_uif;   // rc_w0

        ++hw::g_ticks;

        /* Запис у периферію ще летить шиною APB, коли ядро вже виходить
         * з обробника: без бар'єра NVIC устигає побачити прапорець піднятим
         * і викликає обробник удруге. */
        dsb();
    }
}
