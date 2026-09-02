/*
 * Той самий інвертор, що й у варіанті на C: контур струму в обробнику АЦП
 * на 20 кГц, траєкторія у фоні, спільний стан більший за машинне слово.
 * Різниця в тому, що жодного парного «увійшов — вийшов» у коді немає:
 * секцію тримає об'єкт, а спільні дані взагалі не мають доступу без неї.
 */

#include "critical_section.hpp"
#include "fault_report.hpp"
#include "nvic_priority.hpp"

#include <algorithm>
#include <atomic>
#include <cstdint>

namespace {

constexpr std::uint8_t kAdcPriority = 5;
constexpr std::uint8_t kTripPriority = 0;   /* поріг його не маскує — так і треба */
constexpr cortexm::Basepri kMotorLock = cortexm::basepri(kAdcPriority);

constexpr std::uint64_t kPwmTickUs = 50;
constexpr std::int32_t kPwmPeriod = 4199;        /* 84 МГц / (4199 + 1) = 20 кГц */
constexpr std::int32_t kCurrentLimitMa = 18000;
constexpr std::int32_t kMaPerLsb = 10;

/* Коефіцієнти ПІ у форматі Q10. */
constexpr int kGainShift = 10;
constexpr std::int32_t kKpQ10 = 120;
constexpr std::int32_t kKiQ10 = 3;
constexpr std::int32_t kIntegralLimit = 1 << 20;

struct MotorState {
    std::uint64_t timestamp_us{};
    std::int32_t iq_ref{};       /* уставка моменту, мА — пише фон */
    std::int32_t ia_meas{};      /* виміряний струм фази A, мА — пише ISR */
    std::int32_t iq_integral{};  /* накопичена помилка ПІ — пише ISR */
    std::int32_t duty{};         /* остання шпаруватість, такти — пише ISR */
};

/* Ось причина всієї цієї роботи: 24 байти атомарно не читаються ніяк. */
static_assert(!std::atomic<MotorState>::is_always_lock_free,
              "Якби структура була lock-free, критична секція була б зайвою");

cortexm::Shared<MotorState> g_motor{kMotorLock};

/* А 32 біти — читаються: компілятор розгорне fetch_add у цикл LDREX/STREX. */
std::atomic<std::uint32_t> g_pwm_cycles{0};
static_assert(std::atomic<std::uint32_t>::is_always_lock_free,
              "На ARMv7-M 32-бітний лічильник обходиться без секції");

std::atomic<bool> g_trip{false};

void pwm_disable_outputs() noexcept
{
    TIM1->BDTR &= ~TIM_BDTR_MOE;   /* знімаємо Main Output Enable */
}

[[noreturn]] void fatal() noexcept
{
    pwm_disable_outputs();
    cortexm::regs::mask_all_irq();
    for (;;) {
    }
}

/* Сирий відлік 12-бітного АЦП -> струм фази у мА зі знаком. */
[[nodiscard]] constexpr std::int32_t adc_to_ma(std::uint32_t raw) noexcept
{
    return (static_cast<std::int32_t>(raw & 0x0FFFU) - 2048) * kMaPerLsb;
}

/*
 * Те, що документація ARM обіцяє, а кремній підтверджує. Викликати з main()
 * до дозволу переривань периферії.
 */
[[nodiscard]] bool selftest() noexcept
{
    if (cortexm::regs::in_isr()) {
        return false;
    }

    bool ok = true;

#if !defined(__ARM_ARCH_6M__)
    /* Саме #if, а не if constexpr: відкинута гілка теж має компілюватися,
     * а на ARMv6-M цих функцій просто немає в природі. */
    {
        const cortexm::PrimaskGuard guard;   /* сам тест — критична секція */
        const std::uint32_t entry = cortexm::regs::read_basepri();

        /* Сире число пріоритету апаратура з'їдає: молодші біти не реалізовані. */
        cortexm::regs::write_basepri(0U);
        cortexm::regs::write_basepri(5U);
        ok = ok && (cortexm::regs::read_basepri() == 0U);

        /* Закодований байт лягає як є. */
        cortexm::regs::write_basepri(cortexm::basepri(5).raw());
        ok = ok && (cortexm::regs::read_basepri() == cortexm::basepri(5).raw());

        /* BASEPRI_MAX слабшим порогом не переписує... */
        cortexm::regs::raise_basepri(cortexm::basepri(7).raw());
        ok = ok && (cortexm::regs::read_basepri() == cortexm::basepri(5).raw());

        /* ...а суворішим — переписує. На цьому й тримається вкладеність. */
        cortexm::regs::raise_basepri(cortexm::basepri(3).raw());
        ok = ok && (cortexm::regs::read_basepri() == cortexm::basepri(3).raw());

        cortexm::regs::write_basepri(entry);
    }
#endif

    /* Вкладені guard-и: внутрішній деструктор не має відкривати переривання. */
    {
        const cortexm::PrimaskGuard outer;
        {
            const cortexm::PrimaskGuard inner;
            ok = ok && (cortexm::regs::read_primask() == cortexm::regs::PrimaskState::Masked);
        }
        ok = ok && (cortexm::regs::read_primask() == cortexm::regs::PrimaskState::Masked);
    }

    ok = ok && !cortexm::regs::active_irq().has_value();   /* ми у Thread Mode */
    return ok;
}

/*
 * Розбір попереднього запуску. Нас цікавить одна конкретна комбінація:
 * ескалація плюс піднята маска. Вона означає, що помилка сталася всередині
 * критичної секції — настроюваний обробник був заблокований, і апаратура
 * підмінила його HardFault-ом. Піднімати привід після такого не можна:
 * причина лишилася в коді, і наступний прохід контуру повторить її з тим
 * самим струмом в обмотці.
 */
void inspect_previous_run() noexcept
{
    const std::optional<cortexm::FaultRecord> crash = cortexm::take_last_fault();
    if (!crash.has_value()) {
        return;
    }

    const std::string_view what = crash->cause();
    const std::string_view where = cortexm::to_string(crash->kind);
    const std::optional<std::uint32_t> address = crash->fault_address();
    /* Сюди ж лягає виклик журналу, коли він у системі є. */
    static_cast<void>(what);
    static_cast<void>(where);
    static_cast<void>(address);

    if (crash->inside_critical_section()) {
        fatal();
    }
}

void trajectory_step(MotorState& state) noexcept
{
    constexpr std::int32_t target = 4000;
    constexpr std::int32_t step = 25;

    if (state.iq_ref < target) {
        state.iq_ref += step;
    } else if (state.iq_ref > target) {
        state.iq_ref -= step;
    }
}

}  // namespace

/* --- Обробник АЦП: єдиний письменник вимірів --------------------------- */
extern "C" void ADC_IRQHandler()
{
    const std::uint32_t sr = ADC1->SR;

    if ((sr & ADC_SR_OVR) != 0U) {
        ADC1->SR &= ~static_cast<std::uint32_t>(ADC_SR_OVR);
        g_trip.store(true, std::memory_order_release);
        pwm_disable_outputs();
        return;
    }

    if ((sr & ADC_SR_EOC) == 0U) {
        return;   /* вектор спільний на ADC1/2/3 — перерив не наш */
    }

    const std::int32_t ia_ma = adc_to_ma(ADC1->DR);   /* читання DR скидає EOC */

    g_pwm_cycles.fetch_add(1, std::memory_order_relaxed);

    /* from_isr(): обробник не витісняється ані фоном, ані рівним собі. */
    MotorState& state = g_motor.from_isr();
    state.timestamp_us += kPwmTickUs;
    state.ia_meas = ia_ma;

    if (ia_ma > kCurrentLimitMa || ia_ma < -kCurrentLimitMa) {
        g_trip.store(true, std::memory_order_release);
        pwm_disable_outputs();
        return;
    }

    /*
     * ПІ-регулятор струму. Уставку iq_ref фон поклав під секцією — саме тому
     * обробник читає ціле число, а не половину старого і половину нового.
     */
    const std::int32_t error = state.iq_ref - ia_ma;
    state.iq_integral = std::clamp(state.iq_integral + error,
                                   -kIntegralLimit, kIntegralLimit);

    const std::int32_t out = (kKpQ10 * error + kKiQ10 * state.iq_integral) >> kGainShift;
    state.duty = std::clamp(out, 0, kPwmPeriod);

    TIM1->CCR1 = static_cast<std::uint32_t>(state.duty);
}

/* --- Апаратний захист по перевищенню струму (вивід EXTI13) ------------- */
extern "C" void EXTI15_10_IRQHandler()
{
    if ((EXTI->PR & EXTI_PR_PR13) != 0U) {
        EXTI->PR = EXTI_PR_PR13;   /* запис одиниці скидає прапорець */

        {
            /* Кілька інструкцій, поки гасимо виходи, — без жодних виключень. */
            const cortexm::FaultmaskGuard guard;
            pwm_disable_outputs();
        }

        g_trip.store(true, std::memory_order_release);
    }
}

int main()
{
    inspect_previous_run();

    /* Без цього MemManage, BusFault та UsageFault не існують як окремі
     * виключення: усе приходить HardFault-ом одразу, і біт FORCED уже нічого
     * не розрізняє. */
    cortexm::enable_configurable_faults();

    cortexm::use_flat_priority_grouping();
    if (!cortexm::priority_grouping_is_flat()) {
        fatal();
    }

    if (!selftest()) {
        fatal();
    }

    NVIC_SetPriority(ADC_IRQn, kAdcPriority);       /* CMSIS зсуває сам */
    NVIC_SetPriority(EXTI15_10_IRQn, kTripPriority);
    if (NVIC_GetPriority(ADC_IRQn) != kAdcPriority) {
        fatal();   /* поріг рахували під один пріоритет, а виставили інший */
    }

    NVIC_EnableIRQ(EXTI15_10_IRQn);
    NVIC_EnableIRQ(ADC_IRQn);

    for (;;) {
        const MotorState snapshot = g_motor.load();   /* цілісні 24 байти */

        if (g_trip.load(std::memory_order_acquire)) {
            pwm_disable_outputs();
            continue;
        }

        MotorState next = snapshot;
        trajectory_step(next);   /* довгий розрахунок — поза секцією */

        /* Віддаємо назад тільки уставку: виміри, інтегратор і мітку часу веде
         * обробник, і перезапис знімком відкотив би контур на такт назад. */
        g_motor.modify([&next](MotorState& state) noexcept {
            state.iq_ref = next.iq_ref;
        });

        __WFI();
    }
}
