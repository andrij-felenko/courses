#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define SIM_TIME_SEC       0.050f   /* Час симуляції 50 мс */
#define SIM_DT_SEC         0.00001f /* Крок інтегрування 10 мкс */

/* Параметри джерела живлення LiPo 6S */
#define BAT_CELLS          6
#define BAT_OCV_PER_CELL   4.10f    /* Початковий заряд на банку, В */
#define BAT_R_INT_OHM      0.024f   /* 24 мОм внутрішній опір батареї */

/* Параметри силового джгута та роз'єму */
#define WIRE_R_OHM         0.003f   /* 3 мОм опір дротів і XT60 */
#define WIRE_L_HENRY       80e-9f   /* 80 нГн індуктивність джгута */

/* Параметри Low-ESR конденсатора */
#define CAP_C_FARAD        1000e-6f /* 1000 мкФ */
#define CAP_ESR_OHM        0.012f   /* 12 мОм */

/* Параметри вторинних стабілізаторів польотного контролера */
#define BEC_TARGET_V       5.00f    /* Цільова напруга BEC 5V */
#define BEC_DROPOUT_V      1.40f    /* Мінімальне падіння напруги Buck */
#define BEC_UVLO_V         6.00f    /* Поріг відсічки UVLO BEC */

#define LDO_TARGET_V       3.30f    /* Цільова напруга ядра 3.3V */
#define LDO_DROPOUT_V      0.25f    /* Падіння напруги LDO */

/* Поріг супервізора STM32 BOR Level 3 */
#define STM32_BOR_THRESH_V 2.70f

typedef struct {
    float v_ocv;
    float r_total;
    float l_wire;
    float cap_c;
    float cap_esr;
    float v_cap;       /* Напруга безпосередньо на ємності */
    float i_wire;      /* Струм через силовий джгут */
} PowerBus;

typedef struct {
    float v_5v;
    float v_3v3;
    bool  in_brownout;
    float brownout_time_ms;
} FlightControllerPower;

static void power_bus_init(PowerBus *bus, float ocv, float r_int, float r_wire, 
                           float l_wire, float c_farad, float esr) {
    bus->v_ocv = ocv;
    bus->r_total = r_int + r_wire;
    bus->l_wire = l_wire;
    bus->cap_c = c_farad;
    bus->cap_esr = esr;
    bus->v_cap = ocv;
    bus->i_wire = 0.0f;
}

static void simulate_step(PowerBus *bus, FlightControllerPower *fc, 
                          float i_load, float dt) {
    /* 1. Струм через внутрішній конденсатор і напруга на шині */
    /* V_bus = v_cap + i_cap * cap_esr */
    /* i_wire = (v_ocv - v_bus - i_wire * r_total) / l_wire (динаміка індуктивності) */
    
    float v_bus_est = bus->v_cap + (bus->i_wire - i_load) * bus->cap_esr;
    float di_wire = ((bus->v_ocv - v_bus_est - bus->i_wire * bus->r_total) / bus->l_wire) * dt;
    bus->i_wire += di_wire;
    if (bus->i_wire < 0.0f) bus->i_wire = 0.0f;

    float i_cap = bus->i_wire - i_load;
    bus->v_cap += (i_cap / bus->cap_c) * dt;
    float v_bus = bus->v_cap + i_cap * bus->cap_esr;

    /* 2. Модель стабілізатора Buck BEC 5.0V */
    if (v_bus < BEC_UVLO_V) {
        fc->v_5v = 0.0f; /* UVLO відсічка */
    } else if (v_bus < (BEC_TARGET_V + BEC_DROPOUT_V)) {
        fc->v_5v = v_bus - BEC_DROPOUT_V;
    } else {
        fc->v_5v = BEC_TARGET_V;
    }

    /* 3. Модель лінійного стабілізатора LDO 3.3V */
    if (fc->v_5v < (LDO_TARGET_V + LDO_DROPOUT_V)) {
        fc->v_3v3 = fc->v_5v - LDO_DROPOUT_V;
        if (fc->v_3v3 < 0.0f) fc->v_3v3 = 0.0f;
    } else {
        fc->v_3v3 = LDO_TARGET_V;
    }

    /* 4. Стан супервізора STM32 Brown-Out Reset (BOR) */
    if (fc->v_3v3 < STM32_BOR_THRESH_V) {
        if (!fc->in_brownout) {
            fc->in_brownout = true;
            fc->brownout_time_ms = 0.0f;
        }
        fc->brownout_time_ms += dt * 1000.0f;
    } else {
        fc->in_brownout = false;
    }
}

int main(void) {
    PowerBus bus;
    FlightControllerPower fc = {0};
    
    float ocv = BAT_CELLS * BAT_OCV_PER_CELL;
    power_bus_init(&bus, ocv, BAT_R_INT_OHM, WIRE_R_OHM, 
                   WIRE_L_HENRY, CAP_C_FARAD, CAP_ESR_OHM);

    printf("=== Симуляція просадки напруги при ривку газу (C) ===\n");
    printf("Початкова напруга 6S: %.2f В, R_int: %.1f мОм, Cap: %.0f мкФ\n\n",
           ocv, BAT_R_INT_OHM * 1000.0f, CAP_C_FARAD * 1e6f);
    printf("Час(мс) | Струм(А) | V_bat(В) | BEC(В) | MCU(В) | Стан BOR\n");
    printf("-----------------------------------------------------------\n");

    bool brownout_detected = false;
    float max_sag_v = ocv;

    for (float t = 0.0f; t <= SIM_TIME_SEC; t += SIM_DT_SEC) {
        /* Профіль струму: ривок на t = 5 мс від 15 А до 180 А за 3 мс */
        float i_load = 15.0f;
        if (t >= 0.005f && t < 0.008f) {
            float ramp = (t - 0.005f) / 0.003f;
            i_load = 15.0f + ramp * (180.0f - 15.0f);
        } else if (t >= 0.008f && t < 0.030f) {
            i_load = 180.0f;
        } else if (t >= 0.030f) {
            i_load = 60.0f; /* Вихід на стабільну тягу */
        }

        simulate_step(&bus, &fc, i_load, SIM_DT_SEC);

        float v_bus_now = bus.v_cap;
        if (v_bus_now < max_sag_v) {
            max_sag_v = v_bus_now;
        }

        if (fc.in_brownout) {
            brownout_detected = true;
        }

        /* Вивід зразків кожні 5 мс */
        int step_idx = (int)(t / SIM_DT_SEC);
        if (step_idx % 500 == 0) {
            printf("%6.1f  | %7.1f  | %7.2f  | %5.2f  | %5.2f  | %s\n",
                   t * 1000.0f, i_load, v_bus_now, fc.v_5v, fc.v_3v3,
                   fc.in_brownout ? "FAIL (RESET!)" : "OK (Норма)");
        }
    }

    printf("-----------------------------------------------------------\n");
    printf("Результат: Мін. напруга батареї: %.2f В. Аварійний BOR: %s\n",
           max_sag_v, brownout_detected ? "СПРАЦЮВАВ (АВАРІЯ)" : "НЕ ВИЯВЛЕНО");

    return 0;
}
