#include <math.h>
#include <stdio.h>

#include "arbiter.h"
#include "ingest.h"
#include "trace.h"

/* Крок стенда — 25 мс: рівно з таким періодом шле уставки комп'ютер зору, і на
   такому кроці роботу лімітера видно оком. На борту evaluate() кличуть кожні
   2.5 мс (400 Гц) — логіка та сама, кроки лімітера вдесятеро дрібніші. */
#define TICK_US 25000u

static arbiter_t    g_arb;
static sp_mailbox_t g_mail[SRC_COUNT];

/* Імітація обробника переривання приймача CRSF / MAVLink: кадр лягає у скриньку
   й НЕ торкається арбітра — арбітр живе тільки в польотному циклі. */
static void isr_frame(source_id_t src, float roll, float pitch, float yaw,
                      float thrust, uint64_t now_us)
{
    setpoint_t sp;

    sp.stamp_us       = now_us;
    sp.ch[AX_ROLL]    = roll;
    sp.ch[AX_PITCH]   = pitch;
    sp.ch[AX_YAW]     = yaw;
    sp.ch[AX_THRUST]  = thrust;
    sp_mailbox_publish(&g_mail[src], &sp);
}

/* Рядок чорної скриньки: активне джерело, відхилення стіків і стан сторожів —
   без цих трьох полів розслідувати інцидент у польоті нічим. */
static void log_record(uint64_t now_us, source_id_t src, const setpoint_t *out)
{
    int i;

    printf("[%6.3fs] %-8s defl=%.3f | roll=%+.3f pitch=%+.3f yaw=%+.3f thr=%.3f | ",
           (double)now_us * 1e-6, source_name(src), arbiter_deflection(&g_arb),
           out->ch[AX_ROLL], out->ch[AX_PITCH], out->ch[AX_YAW], out->ch[AX_THRUST]);
    for (i = 0; i < SRC_COUNT; ++i)
        printf("%s:%s ", source_name((source_id_t)i),
               arbiter_is_live(&g_arb, (source_id_t)i) ? "ok" : "--");
    printf("%s\n", arbiter_output_valid(&g_arb) ? "" : "[вихід недійсний]");
}

/* Один такт польотного циклу: забрати кадри, розсудити, віддати мікшеру. */
static void flight_cycle(uint64_t now_us)
{
    setpoint_t  out;
    source_id_t src;
    int         i;

    for (i = 0; i < SRC_COUNT; ++i) {
        setpoint_t   sp;
        arb_status_t st;

        if (!sp_mailbox_take(&g_mail[i], &sp))
            continue;
        st = arbiter_submit(&g_arb, (source_id_t)i, &sp, now_us);
        if (st != ARB_OK)
            printf("          кадр від %s відкинуто: %s\n",
                   source_name((source_id_t)i), arb_status_name(st));
    }

    src = arbiter_evaluate(&g_arb, now_us, &out);
    /* Тут уставка йде в мікшер моторів і далі в DShot-кадр. */
    diag_pin_low();
    log_record(now_us, src, &out);
}

int main(void)
{
    uint64_t now = 1000000u;   /* 1.000 с від старту борту */
    int      i, step;

    arbiter_init(&g_arb);
    diag_pin_init();
    for (i = 0; i < SRC_COUNT; ++i)
        sp_mailbox_init(&g_mail[i]);

    printf("=== ДИСПЕТЧЕР ПРІОРИТЕТІВ ДЖЕРЕЛ КЕРУВАННЯ ===\n\n");

    printf("-- 1. Автономний політ: пульт живий, ручки в центрі — керує комп'ютер зору\n");
    isr_frame(SRC_GCS_MISSION, 0.0f, 0.05f, 0.0f, 0.50f, now);
    isr_frame(SRC_RC_PILOT,    0.0f, 0.00f, 0.0f, 0.50f, now);
    isr_frame(SRC_OFFBOARD,    0.35f, 0.00f, 0.0f, 0.55f, now);
    flight_cycle(now);

    printf("-- 2. Процес зору впав: кадр із NaN відкинуто, серце слоту не б'ється\n");
    now += TICK_US;
    isr_frame(SRC_RC_PILOT, 0.0f, 0.0f, 0.0f, 0.50f, now);
    isr_frame(SRC_OFFBOARD, 0.35f, NAN, 0.0f, 0.55f, now);
    flight_cycle(now);

    printf("-- 3. Перед апаратом трос: пілот смикає тангаж на 0.78 рад\n");
    now += TICK_US;
    isr_frame(SRC_RC_PILOT, 0.0f, 0.78f, 0.0f, 0.70f, now);
    flight_cycle(now);

    printf("-- 4. Безударне наростання: крок лімітера 6.0 * 0.025 = 0.15 рад\n");
    for (step = 0; step < 4; ++step) {
        now += TICK_US;
        isr_frame(SRC_RC_PILOT, 0.0f, 0.78f, 0.0f, 0.70f, now);
        flight_cycle(now);
    }

    printf("-- 5. Банка просіла до 3.2 В: аварійний автомат витісняє й пілота\n");
    now += 10000u;
    arbiter_raise_failsafe(&g_arb, 0.30f, now);
    isr_frame(SRC_RC_PILOT, 0.0f, 0.78f, 0.0f, 0.70f, now);  /* стік досі відхилено — марно */
    flight_cycle(now);
    for (step = 0; step < 3; ++step) {
        now += TICK_US;
        isr_frame(SRC_RC_PILOT, 0.0f, 0.78f, 0.0f, 0.70f, now);
        flight_cycle(now);
    }

    printf("\nперемикань авторитету: %u, відкинутих кадрів: %u\n",
           arbiter_switch_count(&g_arb), arbiter_reject_count(&g_arb));
    printf("реакція на стік: остання %u мкс, найгірша %u мкс, імпульсів %u (бюджет такту 2500 мкс)\n",
           diag_pulse_last_us(), diag_pulse_worst_us(), diag_pulse_count());
    printf("скринька offboard: пропущено циклом %u, рваних копій %u\n",
           sp_mailbox_dropped(&g_mail[SRC_OFFBOARD]), sp_mailbox_torn(&g_mail[SRC_OFFBOARD]));
    return 0;
}
