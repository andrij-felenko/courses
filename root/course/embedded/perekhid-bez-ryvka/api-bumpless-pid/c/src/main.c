/*
 * Демонстрація безривкової передачі повноважень.
 *
 * Сценарій одного польоту:
 *   0.0 с — ручний режим, пілот тримає фіксований хід газу;
 *   1.0 с — перемикання в утримання швидкості набору (handover);
 *   4.0 с — зрив обміну з давачем на 150 мс (NaN у вимірі);
 *   5.0 с — недосяжна ціль: привід у насиченні, працює анти-віндап;
 *   8.0 с — повернення цілі в межі досяжного.
 */
#include <stdio.h>
#include <string.h>

#include "bumpless_pid.h"
#include "pid_num.h"
#include "plant.h"

#define DT              0.005f   /* 200 Гц — типовий такт контуру швидкості */
#define T_SWITCH        1.0f
#define T_FAULT         4.0f
#define T_FAULT_END     4.15f
#define T_DEMAND        5.0f
#define T_RELAX         8.0f
#define T_END          12.0f
#define PRINT_PERIOD    0.5f

#define MANUAL_THROTTLE 0.62f
#define FIRST_TARGET    1.0f
#define HARD_TARGET     9.0f     /* понад повноваження апарата (~6.7 м/с) */
#define CALM_TARGET     0.0f

/*
 * Конфігурація контуру вертикальної швидкості. Живе у Flash: `const`,
 * одна копія на всі екземпляри регулятора.
 */
static const pid_config_t CLIMB_CFG = {
    .kp = 0.08f,
    .ki = 0.10f,
    .kd = 0.01f,
    .kff = 0.0667f,      /* 1/15: стільки ходу газу коштує 1 м/с усталеної швидкості */
    .out_min = 0.0f,
    .out_max = 1.0f,
    .i_min = 0.30f,      /* вужче за межі виходу: лишаємо запас на P-маневр */
    .i_max = 0.85f,
    .slew_rate_max = 2.0f
};

static const char *flags_text(uint8_t flags, char *buf, size_t size)
{
    static const struct {
        uint8_t bit;
        const char *name;
    } TABLE[] = {
        { PID_FLAG_SATURATED,    "SAT"    },
        { PID_FLAG_I_CLAMPED,    "ICLAMP" },
        { PID_FLAG_I_HELD,       "IHOLD"  },
        { PID_FLAG_SENSOR_FAULT, "NAN"    },
        { PID_FLAG_DT_INVALID,   "DT"     },
        { PID_FLAG_SLEWING,      "SLEW"   }
    };
    size_t used = 0;
    size_t i;

    buf[0] = '\0';
    for (i = 0; i < sizeof TABLE / sizeof TABLE[0]; ++i) {
        size_t len;
        if ((flags & TABLE[i].bit) == 0u) {
            continue;
        }
        len = strlen(TABLE[i].name);
        if (used + len + 2u >= size) {
            break;
        }
        if (used > 0u) {
            buf[used++] = '|';
        }
        memcpy(buf + used, TABLE[i].name, len);
        used += len;
        buf[used] = '\0';
    }
    if (used == 0u && size > 1u) {
        buf[0] = '-';
        buf[1] = '\0';
    }
    return buf;
}

static void print_header(void)
{
    printf("   t,с  режим   v_вим  v_уст      u       P      I       D      FF  прапорці\n");
    printf("  --------------------------------------------------------------------------\n");
}

static void print_row(float t, const char *mode, float measurement,
                      const pid_trace_t *tr, float output)
{
    char fbuf[48];

    printf("  %5.2f  %-6s %6.3f %6.3f  %6.3f  %6.3f %6.3f  %6.3f  %6.3f  %s\n",
           (double)t, mode, (double)measurement,
           (double)tr->setpoint, (double)output,
           (double)tr->p_term, (double)tr->i_term,
           (double)tr->d_term, (double)tr->ff_term,
           flags_text(tr->flags, fbuf, sizeof fbuf));
}

/*
 * Що видав би на перемиканні регулятор, який просто почав з чистого стану:
 * інтеграл нуль, історія виміру взята з давача. Уставка на цей момент
 * дорівнює виміру, тож лишається самий прямий зв'язок.
 */
static float naive_first_output(float measurement)
{
    float u = CLIMB_CFG.kff * measurement;
    return pid_clampf(u, CLIMB_CFG.out_min, CLIMB_CFG.out_max);
}

int main(void)
{
    plant_t plant;
    bumpless_pid_t pid;
    pid_trace_t trace = { 0 };
    float t = 0.0f;
    float u = MANUAL_THROTTLE;
    float next_print = 0.0f;
    bool auto_mode = false;
    bool demanded = false;
    bool relaxed = false;
    bool switch_captured = false;
    unsigned fault_ticks = 0;
    float u_before_switch = 0.0f;
    float u_after_switch = 0.0f;
    float m_at_switch = 0.0f;

    plant_init(&plant, 0.55f);
    bumpless_pid_init(&pid, &CLIMB_CFG);
    if (!pid.is_initialized) {
        printf("Конфігурація контуру непридатна — регулятор не запущено.\n");
        return 1;
    }

    printf("Безривкова передача повноважень: контур вертикальної швидкості\n");
    printf("Такт %.0f Гц, завислість %.2f, ручний хід газу %.2f\n\n",
           (double)(1.0f / DT), (double)plant.hover_throttle,
           (double)MANUAL_THROTTLE);
    print_header();

    while (t < T_END) {
        bool fault = (t >= T_FAULT && t < T_FAULT_END);
        float measurement = plant_sample(&plant, fault);
        const char *mode = "РУЧН";

        if (!auto_mode && t >= T_SWITCH) {
            /*
             * Той самий свіжий відлік іде і в передачу, і в перший update
             * цього ж такту — саме за цієї умови вимога
             * |u(0+) − prev_actuator_output| == 0 виконується бітово.
             */
            bumpless_pid_handover(&pid, measurement, FIRST_TARGET, u);
            u_before_switch = u;
            m_at_switch = measurement;
            auto_mode = true;
        }

        if (auto_mode && !demanded && t >= T_DEMAND) {
            bumpless_pid_set_target(&pid, HARD_TARGET);
            demanded = true;
        }
        if (auto_mode && !relaxed && t >= T_RELAX) {
            bumpless_pid_set_target(&pid, CALM_TARGET);
            relaxed = true;
        }

        if (auto_mode) {
            mode = "АВТО";
            u = bumpless_pid_update_traced(&pid, measurement, DT, &trace);
            if (!switch_captured) {
                /* Перший такт під керуванням регулятора — той самий, у якому
                   відбулася передача. Саме його порівнюємо з ручним ходом. */
                u_after_switch = u;
                switch_captured = true;
            }
            if ((trace.flags & PID_FLAG_SENSOR_FAULT) != 0u) {
                ++fault_ticks;
            }
        } else {
            /* У ручному режимі регулятор мовчить, але стан тримає. */
            u = MANUAL_THROTTLE;
            trace.setpoint = 0.0f;
            trace.p_term = 0.0f;
            trace.i_term = 0.0f;
            trace.d_term = 0.0f;
            trace.ff_term = 0.0f;
            trace.flags = 0u;
        }

        plant_step(&plant, u, DT);

        if (t + 0.5f * DT >= next_print) {
            print_row(t, mode, measurement, &trace, u);
            next_print += PRINT_PERIOD;
        }
        t += DT;
    }

    printf("\nСтик на перемиканні (t = %.2f с, вимір %.3f м/с):\n",
           (double)T_SWITCH, (double)m_at_switch);
    printf("  безривкова передача : |%.6f − %.6f| = %.6f\n",
           (double)u_after_switch, (double)u_before_switch,
           (double)(u_after_switch - u_before_switch >= 0.0f
                        ? u_after_switch - u_before_switch
                        : u_before_switch - u_after_switch));
    printf("  наївний рестарт     : |%.6f − %.6f| = %.6f  ← удар по моторах\n",
           (double)naive_first_output(m_at_switch), (double)u_before_switch,
           (double)(u_before_switch - naive_first_output(m_at_switch)));
    printf("\nВідкинутих тактів через нескінченний вимір: %u\n", fault_ticks);
    printf("Висота наприкінці: %.2f м, швидкість %.3f м/с\n",
           (double)plant.altitude, (double)plant.climb_rate);
    return 0;
}
