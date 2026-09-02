/*
 * Керування трифазним інвертором: контур струму в обробнику АЦП на 20 кГц
 * і фонова траєкторія в main(). Спільні дані більші за машинне слово, тому
 * доступ до них із фону загорнуто в BASEPRI-секцію рівно того пріоритету,
 * на якому працює обробник-письменник.
 */

#include "cortexm_mask.h"
#include "fault_report.h"
#include "nvic_priority.h"

#define ADC_ISR_PRIORITY    5U   /* контур струму, 50 мкс */
#define TRIP_ISR_PRIORITY   0U   /* апаратний захист: BASEPRI його не маскує */
#define MOTOR_LOCK          NVIC_BASEPRI(ADC_ISR_PRIORITY)

#define PWM_TICK_US         50U
#define PWM_PERIOD          4199    /* 84 МГц / (4199 + 1) = 20 кГц */
#define CURRENT_LIMIT_MA    18000
#define MA_PER_LSB          10      /* шунт + підсилювач, 12 біт, нуль на 2048 */

/* Коефіцієнти ПІ у форматі Q10: множимо, потім зсуваємо на GAIN_SHIFT. */
#define GAIN_SHIFT          10
#define KP_Q10              120
#define KI_Q10              3
/* Обмеження інтегратора: KI_Q10 * INTEGRAL_LIMIT ще влазить в int32. */
#define INTEGRAL_LIMIT      (1L << 20)

typedef struct {
    uint64_t timestamp_us;   /* 64 біти — два LDR, класичний розрив */
    int32_t  iq_ref;         /* уставка моменту, мА — пише фон */
    int32_t  ia_meas;        /* виміряний струм фази A, мА — пише ISR */
    int32_t  iq_integral;    /* накопичена помилка ПІ — пише ISR */
    int32_t  duty;           /* остання шпаруватість, такти — пише ISR */
} motor_state_t;

/*
 * volatile тут не потрібен: до g_motor звертаються або з обробника АЦП, або
 * з фону під секцією, а вхід і вихід із секції містять клоббер пам'яті —
 * компілятор не має права кешувати поля в регістрах через ці межі.
 */
static motor_state_t g_motor;

/* Інкрементується і з фону, і з обробника — через LDREX/STREX. */
static volatile uint32_t g_pwm_cycles;

/* Пишеться обробником пріоритету 0, який не маскується жодною нашою секцією. */
static volatile bool g_trip;

static void pwm_disable_outputs(void)
{
    TIM1->BDTR &= ~TIM_BDTR_MOE;   /* знімаємо Main Output Enable — виходи в Z */
}

static void fatal(void)
{
    pwm_disable_outputs();
    __disable_irq();
    for (;;) {
        /* тримаємо привід вимкненим до апаратного скидання */
    }
}

/* Сирий відлік 12-бітного АЦП -> струм фази у мА зі знаком. */
static int32_t adc_to_ma(uint32_t raw)
{
    return ((int32_t)(raw & 0x0FFFU) - 2048) * MA_PER_LSB;
}

static int32_t clamp_i32(int32_t value, int32_t lo, int32_t hi)
{
    if (value < lo) {
        return lo;
    }
    if (value > hi) {
        return hi;
    }
    return value;
}

/* --- Обробник АЦП: єдиний письменник вимірів ---------------------------- */
void ADC_IRQHandler(void)
{
    const uint32_t sr = ADC1->SR;

    if ((sr & ADC_SR_OVR) != 0U) {
        /* Переповнення означає, що ми пропустили відлік: у контурі струму
         * це вже аварія, а не дрібниця. */
        ADC1->SR &= ~(uint32_t)ADC_SR_OVR;
        g_trip = true;
        pwm_disable_outputs();
        return;
    }

    if ((sr & ADC_SR_EOC) == 0U) {
        return;   /* вектор спільний на ADC1/2/3 — перерив не наш */
    }

    const int32_t ia_ma = adc_to_ma(ADC1->DR);   /* читання DR скидає EOC */

    (void)cortexm_atomic_inc(&g_pwm_cycles);

    /* Секція тут не потрібна: фон не може витіснити обробник, а обробник
     * пріоритету 0 цих полів не торкається. */
    g_motor.timestamp_us += PWM_TICK_US;
    g_motor.ia_meas = ia_ma;

    if ((ia_ma > CURRENT_LIMIT_MA) || (ia_ma < -CURRENT_LIMIT_MA)) {
        g_trip = true;
        pwm_disable_outputs();
        return;
    }

    /*
     * ПІ-регулятор струму. Уставку iq_ref фон поклав під секцією — саме тому
     * обробник читає ціле число, а не половину старого і половину нового.
     */
    const int32_t error = g_motor.iq_ref - ia_ma;
    g_motor.iq_integral = clamp_i32(g_motor.iq_integral + error,
                                    -INTEGRAL_LIMIT, INTEGRAL_LIMIT);

    const int32_t out = (KP_Q10 * error + KI_Q10 * g_motor.iq_integral) >> GAIN_SHIFT;
    const int32_t duty = clamp_i32(out, 0, PWM_PERIOD);

    g_motor.duty = duty;
    TIM1->CCR1 = (uint32_t)duty;   /* нова шпаруватість діє з наступного періоду */
}

/* --- Апаратний захист по перевищенню струму (вивід EXTI13) -------------- */
void EXTI15_10_IRQHandler(void)
{
    if ((EXTI->PR & EXTI_PR_PR13) != 0U) {
        EXTI->PR = EXTI_PR_PR13;      /* запис одиниці скидає прапорець */

        /* Найкоротша секція в системі: поки гасимо виходи, нам не потрібен
         * навіть обробник помилки шини. Вихід із виключення скине FAULTMASK
         * і сам, але покладатися на це в явному коді не варто. */
        const cortexm_state_t fm = cortexm_faultmask_enter();
        pwm_disable_outputs();
        cortexm_faultmask_exit(fm);

        g_trip = true;
    }
}

/* Фонова траєкторія: рахує наступну уставку за знімком стану. */
static void trajectory_step(motor_state_t *snapshot)
{
    const int32_t target = 4000;
    const int32_t step = 25;

    if (snapshot->iq_ref < target) {
        snapshot->iq_ref += step;
    } else if (snapshot->iq_ref > target) {
        snapshot->iq_ref -= step;
    }
}

/*
 * Розбір попереднього запуску. Запис лишає обробник HardFault із
 * fault_report.c, і нас цікавить одна конкретна комбінація: ескалація плюс
 * піднята маска. Вона означає, що помилка сталася всередині критичної
 * секції — настроюваний обробник був заблокований, і апаратура підмінила
 * його HardFault-ом. Піднімати привід після такого не можна: причина
 * лишилася в коді, і наступний прохід контуру повторить її з тим самим
 * струмом в обмотці.
 */
static void inspect_previous_run(void)
{
    const fault_record_t *crash = fault_report_last();
    if (crash == NULL) {
        return;
    }

    const bool escalated_in_section = crash->escalated
                                   && fault_report_masked_at_fault(crash);
    const char *cause = fault_report_cause(crash);
    (void)cause;   /* сюди ж лягає виклик журналу, коли він у системі є */

    uint32_t address = 0U;
    if (fault_report_data_address(crash, &address)) {
        (void)address;   /* точна помилка: адресу апаратура зберегла */
    }

    fault_report_clear();   /* один запис розбирається рівно один раз */

    if (escalated_in_section) {
        fatal();
    }
}

int main(void)
{
    inspect_previous_run();

    /* Без цього MemManage, BusFault та UsageFault не існують як окремі
     * виключення: будь-яка помилка приходить HardFault-ом одразу, і біт
     * FORCED уже нічого не розрізняє. */
    fault_report_enable_configurable_faults();

    nvic_priority_use_flat_grouping();
    if (!nvic_priority_grouping_is_flat()) {
        fatal();   /* змішаний PRIGROUP робить поріг BASEPRI неочевидним */
    }

    /* Пріоритет 0 порогом не закривається — його не можна давати
     * письменнику спільних даних. Перевіряємо це до першого переривання. */
    if (nvic_basepri_from_priority(ADC_ISR_PRIORITY) != MOTOR_LOCK) {
        fatal();
    }

    if (!cortexm_mask_selftest()) {
        fatal();
    }

    NVIC_SetPriority(ADC_IRQn, ADC_ISR_PRIORITY);          /* CMSIS зсуває сам */
    NVIC_SetPriority(EXTI15_10_IRQn, TRIP_ISR_PRIORITY);
    if (NVIC_GetPriority(ADC_IRQn) != ADC_ISR_PRIORITY) {
        fatal();   /* поріг рахували під один пріоритет, а виставили інший */
    }

    NVIC_EnableIRQ(EXTI15_10_IRQn);
    NVIC_EnableIRQ(ADC_IRQn);

    for (;;) {
        /* 1. Знімок спільного стану — цілісний, бо письменник замаскований. */
        cortexm_state_t saved = cortexm_basepri_enter(MOTOR_LOCK);
        motor_state_t snapshot = g_motor;
        cortexm_basepri_exit(saved);

        if (g_trip) {
            pwm_disable_outputs();
            continue;   /* далі — розбір аварії, привід уже знеструмлено */
        }

        /* 2. Довгий розрахунок — поза секцією. Обробник АЦП тут працює. */
        trajectory_step(&snapshot);

        /* 3. Назад віддаємо тільки уставку: виміри, інтегратор і мітку часу
         *    веде ISR, і перезаписати їх знімком означало б відкотити контур. */
        saved = cortexm_basepri_enter(MOTOR_LOCK);
        g_motor.iq_ref = snapshot.iq_ref;
        cortexm_basepri_exit(saved);

        /* Цілісне читання 64 бітів — окремим викликом, без ручної секції. */
        const uint64_t now_us = cortexm_read_u64(&g_motor.timestamp_us, MOTOR_LOCK);
        (void)now_us;

        __WFI();
    }
}
