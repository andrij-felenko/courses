#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define DT_SEC 0.0005f               /* крок інтегрування 500 мкс */
#define V_CLAMP 28.0f                /* поріг обмеження Surge Stopper, В */
#define V_TMR_MAX 1.25f              /* поріг спрацьовування таймера, В */
#define I_TMR_CHARGE 10e-6f          /* струм заряду таймера, 10 мкА */
#define C_TMR_VAL 2.2e-6f            /* ємність конденсатора таймера, 2.2 мкФ */
#define RDS_ON 0.008f                /* опір відкритого каналу MOSFET, 8 мОм */
#define I_LOAD 4.0f                  /* постійний струм навантаження, 4 А */
#define TJ_AMB 25.0f                 /* початкова температура, °C */
#define RTH_JC 0.5f                  /* тепловий опір перехід-корпус, °C/Вт */
#define THERMAL_TAU 0.08f            /* теплова постійна часу кристала, 80 мс */

typedef enum {
    MODE_COLD_CRANK,
    MODE_LOAD_DUMP,
    MODE_REVERSE_POLARITY
} TestMode;

typedef enum {
    STATE_NORMAL,
    STATE_REVERSE_BLOCK,
    STATE_CLAMPING,
    STATE_TRIPPED
} ProtectionState;

typedef struct {
    ProtectionState state;
    float v_out;
    float v_ds;
    float p_fet;
    float v_tmr;
    float temp_j;
} CircuitStatus;

/* Генератор вхідного профілю напруги */
static float generate_voltage(TestMode mode, float t) {
    if (mode == MODE_REVERSE_POLARITY) {
        return -14.4f;
    }
    if (mode == MODE_LOAD_DUMP) {
        if (t < 0.02f) return 14.4f;
        /* стрибок до 100 В на 20-й мілісекунді з експонентою tau = 120 мс */
        return 14.4f + (100.0f - 14.4f) * expf(-(t - 0.02f) / 0.120f);
    }
    if (mode == MODE_COLD_CRANK) {
        if (t < 0.02f) return 12.0f;
        if (t < 0.035f) return 3.2f;       /* пусковий зрив 15 мс */
        if (t < 0.400f) {                  /* прокручування з пульсаціями */
            float t_crank = t - 0.035f;
            float v_base = 6.0f + 2.0f * (t_crank / 0.365f);
            return v_base + 1.0f * sinf(2.0f * 3.14159f * 15.0f * t_crank);
        }
        if (t < 0.500f) {                  /* відновлення від генератора */
            float p = (t - 0.400f) / 0.100f;
            return 8.0f + (14.4f - 8.0f) * p;
        }
        return 14.4f;
    }
    return 14.4f;
}

/* Моделювання одного дискретного кроку захисного тракту */
static void step_protection(CircuitStatus *status, float v_in, float dt) {
    /* 1. Захист від зворотної полярності (ідеальний діод) */
    if (v_in < 0.0f) {
        status->state = STATE_REVERSE_BLOCK;
        status->v_out = 0.0f;
        status->v_ds = -v_in;
        status->p_fet = 0.0f;
        status->v_tmr = 0.0f;
        return;
    }

    /* 2. Якщо таймер уже вибив — ключ залишається відімкненим */
    if (status->state == STATE_TRIPPED) {
        status->v_out = 0.0f;
        status->v_ds = v_in;
        status->p_fet = 0.0f;
        return;
    }

    /* 3. Режим нормальної роботи чи активного обмеження */
    if (v_in <= V_CLAMP) {
        status->state = STATE_NORMAL;
        status->v_ds = I_LOAD * RDS_ON;
        status->v_out = v_in - status->v_ds;
        status->p_fet = status->v_ds * I_LOAD;
        /* плавне остигання таймера */
        if (status->v_tmr > 0.0f) {
            status->v_tmr -= (I_TMR_CHARGE * dt / C_TMR_VAL) * 0.5f;
            if (status->v_tmr < 0.0f) status->v_tmr = 0.0f;
        }
    } else {
        /* Лінійне обмеження Surge Stopper */
        status->state = STATE_CLAMPING;
        status->v_out = V_CLAMP;
        status->v_ds = v_in - V_CLAMP;
        status->p_fet = status->v_ds * I_LOAD;

        /* Заряд конденсатора таймера струмом, пропорційним V_DS */
        float i_charge = I_TMR_CHARGE * (1.0f + status->v_ds / 20.0f);
        status->v_tmr += (i_charge * dt) / C_TMR_VAL;

        if (status->v_tmr >= V_TMR_MAX) {
            status->state = STATE_TRIPPED;
            status->v_out = 0.0f;
            status->p_fet = 0.0f;
        }
    }

    /* 4. Теплова модель переходу кристала (експоненційне фільтрування) */
    float target_temp = TJ_AMB + status->p_fet * RTH_JC;
    float alpha = dt / (THERMAL_TAU + dt);
    status->temp_j += alpha * (target_temp - status->temp_j);
}

int main(void) {
    CircuitStatus sim = {
        .state = STATE_NORMAL,
        .v_out = 14.4f,
        .v_ds = 0.0f,
        .p_fet = 0.0f,
        .v_tmr = 0.0f,
        .temp_j = TJ_AMB
    };

    printf("Час(мс)  Вхід(В)  Вихід(В)  V_DS(В)  P_FET(Вт)  T_крист(°C)  Стан\n");
    for (float t = 0.0f; t <= 0.350f; t += 0.025f) {
        for (float sub_t = t; sub_t < t + 0.025f; sub_t += DT_SEC) {
            float v_in = generate_voltage(MODE_LOAD_DUMP, sub_t);
            step_protection(&sim, v_in, DT_SEC);
        }
        const char *st_str = "НОРМА";
        if (sim.state == STATE_CLAMPING) st_str = "ОБМЕЖЕННЯ";
        else if (sim.state == STATE_TRIPPED) st_str = "ВІДСІЧЕННЯ";
        else if (sim.state == STATE_REVERSE_BLOCK) st_str = "РЕВЕРС";

        printf("%6.1f   %6.1f   %7.1f   %6.1f   %8.1f   %10.1f   %s\n",
               t * 1000.0f, generate_voltage(MODE_LOAD_DUMP, t),
               sim.v_out, sim.v_ds, sim.p_fet, sim.temp_j, st_str);
    }
    return 0;
}
