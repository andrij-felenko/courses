#include <math.h>
#include <stdio.h>

#include "delayline.h"
#include "pilot.h"
#include "pio.h"
#include "vehicle.h"

#define DT       0.002f     /* 500 Гц — крок дискретизації симуляції */
#define SIM_SEC  8.0f
#define RAD2DEG  57.2957795f
#define OMEGA_C  2.5f       /* робоча частота зрізу людського контуру, рад/с */

typedef struct {
    const char *name;
    ControlMode mode;
    float link_delay;  /* «скло-до-скла» плюс «стік-до-мотора», с */
    float jitter;      /* половина розкиду затримки відеотракту, с */
    bool  jitter_buffer;
    bool  suppression; /* бортове пригнічення PIO */
    bool  lead_ahead;  /* предиктивний маркер на екрані оператора */
    float expo;        /* крива стіка на пульті */
} Scenario;

/* Порив вітру: імпульс моменту 0.8 Н*м тривалістю 150 мс на 0.5 с. */
static float gust(float t) {
    return (t >= 0.5f && t < 0.65f) ? 0.8f : 0.0f;
}

static bool run(const Scenario *sc) {
    Airframe air;
    Autopilot ap;
    DelayLine video, uplink;
    Pilot pilot;
    ObjectDynamics obj;
    PilotParams pp;
    PioMonitor angle_mon, stick_mon, rate_mon;
    PioCorrelator corr;
    float pure_delay, pm0, pm, tau_crit, max_angle = 0.0f;
    int i, steps;
    bool pio_hit;

    airframe_init(&air, 0.02f, 0.05f, 1.2f);
    autopilot_init(&ap, sc->mode, DT);
    autopilot_enable_suppression(&ap, sc->suppression);

    /* Відеотракт забирає ~70% лагу, командний радіолінк ~30%. */
    if (!delay_init(&video, sc->link_delay * 0.7f, sc->jitter, sc->jitter_buffer,
                    DT, 0xBEEFu) ||
        !delay_init(&uplink, sc->link_delay * 0.3f, 0.0f, false, DT, 0xF00Du)) {
        fprintf(stderr, "  ! не вистачило пам'яті на черги затримки\n");
        delay_free(&video);
        delay_free(&uplink);
        return false;
    }

    obj = autopilot_object(&ap, &air);
    pp = pilot_crossover_tune(obj, OMEGA_C);
    if (!pilot_init(&pilot, pp, DT)) {
        fprintf(stderr, "  ! не вдалося зібрати модель оператора\n");
        delay_free(&video);
        delay_free(&uplink);
        return false;
    }

    /* Аналітичний бюджет фази — той самий, що в чеклисті. */
    pure_delay = pp.tau_p + delay_effective(&video) + delay_effective(&uplink);
    pm0 = pilot_phase_margin0(&pp, obj, OMEGA_C);
    pm = pio_phase_margin(pm0, OMEGA_C, pure_delay);
    tau_crit = pio_tau_critical(pm0, OMEGA_C) - pp.tau_p;
    if (tau_crit < 0.0f) {
        tau_crit = 0.0f;
    }

    pio_init(&angle_mon, DT);
    pio_init(&stick_mon, DT);
    pio_init(&rate_mon, DT);
    pio_corr_init(&corr, DT, 1.5f);

    printf("--- %s\n", sc->name);
    printf("    K_p = %.2f | T_L = %.2f c | tau_чиста = %.0f мс | "
           "PM_0 = %.0f град -> PM = %.0f град | запас лінка = %.0f мс\n",
           pp.kp, pp.tl, pure_delay * 1000.0f, pm0, pm, tau_crit * 1000.0f);

    steps = (int)(SIM_SEC / DT);
    for (i = 0; i < steps; ++i) {
        float t = (float)i * DT;
        LinkPacket tm = {{0.0f}}, cmd = {{0.0f}}, seen;
        float shown, error, stick, onboard_stick, torque;

        /* 1. Борт віддає телеметрію у відеотракт. */
        tm.v[LINK_ANGLE] = air.angle;
        tm.v[LINK_RATE] = air.rate;
        delay_push(&video, tm, t);
        seen = delay_pop(&video, t);

        /* 2. Наземна станція за потреби малює прогнозну позначку
              y_pred = y + tau*v — це компенсує фазовий набіг затримки. */
        shown = seen.v[LINK_ANGLE];
        if (sc->lead_ahead) {
            shown += pure_delay * seen.v[LINK_RATE];
        }

        /* 3. Оператор бачить похибку: уставка — горизонт, r = 0. */
        error = 0.0f - shown;
        stick = pilot_update(&pilot, error, t, DT);

        /* 4. Крива пульта й політ команди зворотним радіоканалом. */
        cmd.v[LINK_STICK] = rc_expo(stick, sc->expo);
        delay_push(&uplink, cmd, t);
        onboard_stick = delay_pop(&uplink, t).v[LINK_STICK];

        /* 5. Бортовий контролер і фізика апарата. */
        torque = autopilot_update(&ap, onboard_stick, &air, DT);
        airframe_step(&air, torque, gust(t), DT);

        /* 6. Діагностика — рівно те, що інженер робить із логом польоту. */
        pio_update(&angle_mon, air.angle);
        pio_update(&rate_mon, air.rate);
        pio_update(&stick_mon, stick);
        pio_corr_update(&corr, pio_hp(&stick_mon), pio_hp(&rate_mon));

        if (fabsf(air.angle) > max_angle) {
            max_angle = fabsf(air.angle);
        }
        if (i % 500 == 0) {
            printf("    t=%4.1f c | кут %7.1f град | стік %6.2f | "
                   "переляк %.2f | чутливість %.2f\n",
                   t, air.angle * RAD2DEG, stick,
                   pilot_panic(&pilot), autopilot_sensitivity(&ap));
        }
    }

    /* Підпис PIO: коливання в людській смузі, помітна амплітуда й стік у
       протифазі до гіроскопа. Вібрація рами чи D-терм так не виглядають. */
    pio_hit = pio_active(&angle_mon, 0.10f) && pio_correlation(&corr) < -0.3f;

    printf("    коливання %.2f Гц, амплітуда %.1f град, наростання x%.2f, "
           "кореляція стік/гіро %+.2f\n",
           pio_frequency(&angle_mon), pio_amplitude(&angle_mon) * RAD2DEG,
           pio_growth(&angle_mon), pio_correlation(&corr));
    printf("    насичення моторів %.0f%% кроків, застигань кадру %d, втрат %d\n",
           autopilot_saturation(&ap) * 100.0f, delay_freezes(&video),
           delay_drops(&video));
    printf("    -> %s (макс. нахил %.1f град)\n\n",
           pio_hit ? "РОЗКАЧКА ОПЕРАТОРОМ (PIO)" : "контур стійкий",
           max_angle * RAD2DEG);

    pilot_free(&pilot);
    delay_free(&video);
    delay_free(&uplink);
    return true;
}

int main(void) {
    static const Scenario list[] = {
        {"Rate, лаг 50 мс — прямий аналоговий лінк",
         MODE_RATE, 0.050f, 0.000f, false, false, false, 0.0f},
        {"Rate, лаг 250 мс — цифровий HD-лінк",
         MODE_RATE, 0.250f, 0.000f, false, false, false, 0.0f},
        {"Rate, лаг 120 мс сталий",
         MODE_RATE, 0.120f, 0.000f, false, false, false, 0.0f},
        {"Rate, лаг 120 мс з розкидом +-80 мс",
         MODE_RATE, 0.120f, 0.080f, false, false, false, 0.0f},
        {"Rate, той самий розкид, але з буфером джитера",
         MODE_RATE, 0.120f, 0.080f, true, false, false, 0.0f},
        {"Rate, 250 мс + бортове пригнічення PIO",
         MODE_RATE, 0.250f, 0.000f, false, true, false, 0.0f},
        {"Rate, 250 мс + предиктивний маркер HUD",
         MODE_RATE, 0.250f, 0.000f, false, false, true, 0.0f},
        {"Rate, 250 мс + Expo 0.6 на пульті",
         MODE_RATE, 0.250f, 0.000f, false, false, false, 0.6f},
        {"Angle, 250 мс — швидкий контур перенесено на борт",
         MODE_ANGLE, 0.250f, 0.000f, false, false, false, 0.0f}
    };
    const int n = (int)(sizeof(list) / sizeof(list[0]));
    int i;

    printf("=== Людина в контурі: бюджет фази й розкачка оператором ===\n\n");
    printf("Аналітична межа лагу tau_crit = PM_0 / omega_c:\n");
    printf("  FPV-дрон (omega_c = 5.0 рад/с, PM_0 = 65 град): %.0f мс\n",
           pio_tau_critical(65.0f, 5.0f) * 1000.0f);
    printf("  ровер    (omega_c = 1.5 рад/с, PM_0 = 60 град): %.0f мс\n\n",
           pio_tau_critical(60.0f, 1.5f) * 1000.0f);

    for (i = 0; i < n; ++i) {
        if (!run(&list[i])) {
            return 1;
        }
    }
    return 0;
}
