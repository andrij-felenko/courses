#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Параметри розподільчої мережі живлення (PDN) */
typedef struct {
    double v_source;        /* ЕРС джерела живлення, В */
    double r_source;        /* Внутрішній опір джерела, Ом */
    double r_wire;          /* Активний опір провідників (туди й назад), Ом */
    double l_wire;          /* Паразитна індуктивність кабелю, Гн */
    
    double c_bulk;          /* Ємність об'ємного електроліту, Ф */
    double esr_bulk;        /* ESR електролітичного конденсатора, Ом */
    
    double c_mlcc;          /* Ємність локального керамічного конденсатора, Ф */
    double esr_mlcc;        /* ESR керамічного конденсатора, Ом */
    
    double v_bor_threshold; /* Поріг детектора Brownout Reset, В */
} PdnConfig;

/* Параметри навантаження: двигун постійного струму та МК */
typedef struct {
    double i_mcu_base;      /* Базовий струм МК у спокої, А */
    double motor_r_coil;    /* Опір обмотки двигуна, Ом */
    double motor_i_run;     /* Сталий струм двигуна під навантаженням, А */
    double motor_tau_mech;  /* Механічна стала часу розгону ротора, с */
    double motor_t_start;   /* Момент ввімкнення двигуна, с */
} LoadConfig;

/* Результати моделювання перехідного процесу */
typedef struct {
    double v_min;           /* Мінімальна зафіксована напруга на шині, В */
    double t_v_min;         /* Час досягнення мінімуму, с */
    double v_final;         /* Усталена напруга після перехідного процесу, В */
    bool bor_triggered;     /* Чи відбулося аварійне перезавантаження МК */
    double bor_duration;    /* Сумарний час перебування нижче порогу BOR, с */
} SimResult;

/* Обчислення струму навантаження в момент часу t */
static double compute_load_current(const LoadConfig *load, double t, double v_bus) {
    double i_total = load->i_mcu_base;
    if (t >= load->motor_t_start) {
        double dt_motor = t - load->motor_t_start;
        /* Струм застопореного двигуна I_stall обмежений лише опором обмотки */
        double i_stall = (v_bus > 0.1) ? (v_bus / load->motor_r_coil) : 0.0;
        /* У міру розгону ротора проти-ЕРС зменшує струм до робочого значення */
        double i_motor = load->motor_i_run + (i_stall - load->motor_i_run) * exp(-dt_motor / load->motor_tau_mech);
        i_total += i_motor;
    }
    return i_total;
}

/* Чисельна симуляція перехідного процесу */
SimResult simulate_pdn(const PdnConfig *pdn, const LoadConfig *load, double t_total, double dt) {
    SimResult res;
    res.v_min = pdn->v_source;
    res.t_v_min = 0.0;
    res.bor_triggered = false;
    res.bor_duration = 0.0;

    /* Початкові умови (стан спокою до пуску мотора) */
    double i_wire = load->i_mcu_base;
    double u_c_bulk = pdn->v_source - i_wire * (pdn->r_source + pdn->r_wire);
    double u_c_mlcc = u_c_bulk;
    double v_bus = u_c_bulk;

    double t = 0.0;
    size_t steps = (size_t)(t_total / dt);

    /* Провідність паралельних гілок ємностей для миттєвого розв'язку */
    double g_bulk = 1.0 / pdn->esr_bulk;
    double g_mlcc = 1.0 / pdn->esr_mlcc;
    double g_caps_total = g_bulk + g_mlcc;

    for (size_t step = 0; step < steps; ++step) {
        t = step * dt;
        double i_load = compute_load_current(load, t, v_bus);

        /* Напруга шини з урахуванням закону Ома для вузла */
        v_bus = (i_wire - i_load + g_bulk * u_c_bulk + g_mlcc * u_c_mlcc) / g_caps_total;

        /* Струми у внутрішні ємності конденсаторів */
        double i_c_bulk = (v_bus - u_c_bulk) * g_bulk;
        double i_c_mlcc = (v_bus - u_c_mlcc) * g_mlcc;

        /* Похідні стану кола */
        double di_wire_dt = (pdn->v_source - i_wire * (pdn->r_source + pdn->r_wire) - v_bus) / pdn->l_wire;
        double du_bulk_dt = i_c_bulk / pdn->c_bulk;
        double du_mlcc_dt = i_c_mlcc / pdn->c_mlcc;

        /* Інтегрування методом Ейлера */
        i_wire += di_wire_dt * dt;
        u_c_bulk += du_bulk_dt * dt;
        u_c_mlcc += du_mlcc_dt * dt;

        /* Аналіз екстремумів та спрацьовування захисту */
        if (v_bus < res.v_min) {
            res.v_min = v_bus;
            res.t_v_min = t;
        }

        if (v_bus < pdn->v_bor_threshold) {
            res.bor_triggered = true;
            res.bor_duration += dt;
        }
    }

    res.v_final = v_bus;
    return res;
}

int main(void) {
    /* Конфігурація системи: 3.3 В джерело, довгий кабель 20 см */
    PdnConfig pdn = {
        .v_source = 3.30,
        .r_source = 0.05,       /* 50 мОм внутрішній опір джерела */
        .r_wire = 0.20,         /* 200 мОм провідники туди й назад */
        .l_wire = 150e-9,       /* 150 нГн індуктивність шлейфа */
        .c_bulk = 47e-6,        /* 47 мкФ електроліт */
        .esr_bulk = 0.35,       /* 350 мОм ESR електроліту */
        .c_mlcc = 10e-6,        /* 10 мкФ кераміка */
        .esr_mlcc = 0.01,       /* 10 мОм ESR кераміки */
        .v_bor_threshold = 2.70 /* Поріг Brownout Reset 2.7 В */
    };

    LoadConfig load = {
        .i_mcu_base = 0.030,    /* 30 мА МК */
        .motor_r_coil = 1.50,   /* 1.5 Ом обмотка двигуна */
        .motor_i_run = 0.250,   /* 250 мА номінальний струм */
        .motor_tau_mech = 3e-3, /* 3 мс розгін ротора */
        .motor_t_start = 1e-3   /* Старт на 1.0 мс */
    };

    printf("=== Моделювання кола живлення під час пуску двигуна ===\n");
    printf("Початкова напруга: %.2f В, поріг BOR: %.2f В\n", pdn.v_source, pdn.v_bor_threshold);

    /* Тест 1: Базова конфігурація з недостатнім демпфуванням */
    SimResult r1 = simulate_pdn(&pdn, &load, 10e-3, 10e-9);
    printf("\n[Тест 1: C_bulk = 47 мкФ, R_wire = 0.20 Ом]\n");
    printf("  Мінімальна напруга V_min: %.3f В на %.3f мс\n", r1.v_min, r1.t_v_min * 1000.0);
    printf("  Усталена напруга V_final: %.3f В\n", r1.v_final);
    printf("  Статус BOR: %s (тривалість провалу: %.2f мкс)\n",
           r1.bor_triggered ? "АВАРІЯ (МК скинуто)" : "НОРМА",
           r1.bor_duration * 1e6);

    /* Тест 2: Додавання посиленого Bulk-конденсатора 220 мкФ з низьким ESR */
    pdn.c_bulk = 220e-6;
    pdn.esr_bulk = 0.10;
    SimResult r2 = simulate_pdn(&pdn, &load, 10e-3, 10e-9);
    printf("\n[Тест 2: Посилений C_bulk = 220 мкФ (ESR = 100 мОм)]\n");
    printf("  Мінімальна напруга V_min: %.3f В на %.3f мс\n", r2.v_min, r2.t_v_min * 1000.0);
    printf("  Усталена напруга V_final: %.3f В\n", r2.v_final);
    printf("  Статус BOR: %s (тривалість провалу: %.2f мкс)\n",
           r2.bor_triggered ? "АВАРІЯ (МК скинуто)" : "НОРМА (живлення втримано)",
           r2.bor_duration * 1e6);

    return 0;
}
