/* Стенд часового профілю: обробник контуру струму на 20 кГц, який сам
 * себе міряє. Осцилограф бачить строб, лічильник DWT — такти, фоновий
 * код друкує період, джитер і найгірший час виконання.
 */
#include <stdbool.h>
#include <stdint.h>

#include "bsp.h"
#include "dwt.h"
#include "fir.h"
#include "foc.h"
#include "ramfunc.h"
#include "strobe.h"

#define CAL_SAMPLES      2048U
#define VDC_VOLT         24.0f
/* Дедлайн: половина періоду ШІМ, 25 мкс = 4200 тактів на 168 МГц. */
#define DEADLINE_CYCLES  (BSP_SYSCLK_MHZ * 25U)
/* Демонстраційна електрична швидкість 50 Гц: приріст фази Q32 за такт ШІМ.
   У виробі кут приходить з давача положення, а не з накопичувача. */
#define THETA_STEP       ((uint32_t)((50.0f / (float)BSP_PWM_HZ) * 4294967296.0f))

typedef struct {
    uint32_t period_min;   /* такти між сусідніми входами в ISR */
    uint32_t period_max;
    uint32_t exec_min;     /* BCET корисної роботи */
    uint32_t exec_max;     /* WCET корисної роботи */
    uint32_t overruns;     /* скільки разів робота не влізла в дедлайн */
    uint32_t tripped;      /* міст знято за двома простроченнями поспіль */
} profile_t;

static profile_t s_prof;
static volatile uint32_t s_seq;         /* лічильник поколінь для читача */
static volatile uint32_t s_isr_count;

static uint32_t s_prev_entry;
static bool     s_have_prev;
static uint32_t s_overrun_run;

static fir_f32 s_fir_a;
static fir_f32 s_fir_b;
static uint32_t s_cal_left = CAL_SAMPLES;
static uint32_t s_cal_acc_a;
static uint32_t s_cal_acc_b;
static float s_off_a;
static float s_off_b;
static uint32_t s_theta;

/* ---- статистика ---------------------------------------------------------- */

/* Публікація без заборони переривань: непарний s_seq означає «дані в русі».
   __disable_irq() тут був би джерелом того самого джитера, який ми міряємо. */
RAM_FUNC static void stats_update(uint32_t t_entry, uint32_t exec)
{
    ++s_seq;
    __DMB();

    if (s_have_prev) {
        const uint32_t period = t_entry - s_prev_entry;
        if (period < s_prof.period_min) { s_prof.period_min = period; }
        if (period > s_prof.period_max) { s_prof.period_max = period; }
    }
    s_prev_entry = t_entry;
    s_have_prev = true;

    if (exec < s_prof.exec_min) { s_prof.exec_min = exec; }
    if (exec > s_prof.exec_max) { s_prof.exec_max = exec; }

    if (exec > DEADLINE_CYCLES) {
        ++s_prof.overruns;
        ++s_overrun_run;
        if (s_overrun_run >= 2U) {
            /* Два прострочені такти поспіль — саме той сценарій, що палить
               ключі. Міст знімаємо негайно, розбір лишаємо фоновому коду. */
            bsp_trip();
            s_prof.tripped = 1U;
        }
    } else {
        s_overrun_run = 0U;
    }

    __DMB();
    ++s_seq;
}

static bool profile_snapshot(profile_t *out)
{
    const uint32_t s0 = s_seq;
    __DMB();
    if ((s0 & 1U) != 0U) {
        return false;   /* обробник саме зараз пише */
    }
    *out = s_prof;
    __DMB();
    return s_seq == s0;
}

/* ---- обробник контуру струму --------------------------------------------- */

/* Сам обробник теж лежить у SRAM: інакше кожен його перехід коштував би
   п'яти тактів очікування Flash, а промах ART додавав би випадкові такти. */
RAM_FUNC void ADC_IRQHandler(void)
{
    const uint32_t t_entry = dwt_now();
    strobe_high();
    bsp_ack_adc();

    const uint32_t raw_a = ADC1->JDR1;
    const uint32_t raw_b = ADC1->JDR2;

    if (s_cal_left != 0U) {
        /* Калібрування нуля датчиків: міст стоїть у нульовому векторі,
           струму немає, тому середнє за 2048 вибірок і є зсув. */
        s_cal_acc_a += raw_a;
        s_cal_acc_b += raw_b;
        --s_cal_left;
        if (s_cal_left == 0U) {
            s_off_a = (float)s_cal_acc_a / (float)CAL_SAMPLES;
            s_off_b = (float)s_cal_acc_b / (float)CAL_SAMPLES;
        }
    } else {
        const float ia = fir_f32_push(&s_fir_a, ((float)raw_a - s_off_a) * BSP_ADC_TO_A);
        const float ib = fir_f32_push(&s_fir_b, ((float)raw_b - s_off_b) * BSP_ADC_TO_A);

        s_theta += THETA_STEP;
        bsp_set_duties(foc_step(ia, ib, s_theta, VDC_VOLT));
    }

    stats_update(t_entry, dwt_since(t_entry));
    ++s_isr_count;

    strobe_low();
    /* Прапорець уже знято на початку, але запис міг ще йти шиною APB:
       без DSB ядро встигає вийти й одразу увійти в те саме переривання. */
    __DSB();
}

/* ---- звіт у налагоджувальний порт ITM ------------------------------------ */

static void itm_puts(const char *s)
{
    while (*s != '\0') {
        ITM_SendChar((uint32_t)(unsigned char)*s++);
    }
}

static void itm_u32(uint32_t v)
{
    char buf[11];
    unsigned i = sizeof buf;

    buf[--i] = '\0';
    do {
        buf[--i] = (char)('0' + (v % 10U));
        v /= 10U;
    } while (v != 0U && i > 0U);
    itm_puts(&buf[i]);
}

static void report(void)
{
    static uint32_t last;
    profile_t p;

    if ((s_isr_count - last) < BSP_PWM_HZ) {
        return;   /* раз на секунду; фоновий код у контур не втручається */
    }
    last = s_isr_count;

    if (!profile_snapshot(&p)) {
        return;   /* натрапили на оновлення — надрукуємо наступного разу */
    }

    itm_puts("період ");
    itm_u32(p.period_min);
    itm_puts("..");
    itm_u32(p.period_max);
    itm_puts(" т, джитер ");
    itm_u32(p.period_max - p.period_min);
    itm_puts(" т; BCET ");
    itm_u32(p.exec_min);
    itm_puts(" т, WCET ");
    itm_u32(p.exec_max);
    itm_puts(" т (");
    itm_u32(dwt_us_x100(p.exec_max, BSP_SYSCLK_MHZ));
    itm_puts(" сотих мкс); прострочень ");
    itm_u32(p.overruns);
    itm_puts(p.tripped != 0U ? "; МІСТ ЗНЯТО\r\n" : "\r\n");
}

static void fault_stop(const char *why)
{
    bsp_trip();
    for (;;) {
        itm_puts(why);
        itm_puts("\r\n");
        for (volatile uint32_t i = 0U; i < 4000000U; ++i) {
        }
    }
}

int main(void)
{
    /* .ramfunc копіюємо найпершим: далі майже все, що ми викликаємо,
       уже мусить виконуватися з SRAM. */
    ramfunc_copy();

    if (!bsp_clock_init()) {
        fault_stop("HSE/PLL не завелися");
    }

    strobe_init();
    if (!dwt_init()) {
        itm_puts("DWT недоступний: лишається тільки осцилограф\r\n");
    }

    s_prof.period_min = 0xFFFFFFFFU;
    s_prof.exec_min = 0xFFFFFFFFU;

    fir_f32_reset(&s_fir_a);
    fir_f32_reset(&s_fir_b);
    foc_init();
    foc_set_targets(0.0f, 2.0f);   /* id = 0, iq = 2 А */

    bsp_pwm_init();
    bsp_adc_init();

    for (;;) {
        report();
    }
}
