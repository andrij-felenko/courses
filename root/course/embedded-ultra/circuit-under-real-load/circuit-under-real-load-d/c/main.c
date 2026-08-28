#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Структура параметрів кола живлення */
typedef struct {
    double v_nominal;       /* Номінальна напруга джерела, В */
    double r_source_esr;    /* Внутрішній опір джерела (ESR батареї), Ом */
    double r_cable;         /* Опір кабелю та роз'ємів, Ом */
    double l_cable;         /* Індуктивність кабелю підключення, Гн */
    double v_bor_limit;     /* Поріг спрацьовування Brownout Reset МК, В */
} PowerRail;

/* Структура параметрів навантаження */
typedef struct {
    double i_quiescent;     /* Базовий струм спокою схеми, А */
    double motor_r_winding; /* Опір обмотки двигуна постійного струму, Ом */
    double motor_i_nominal; /* Номінальний струм двигуна під навантаженням, А */
    double motor_t_ramp;    /* Час механічного розгону ротора, с */
} DynamicLoad;

/* Розрахунок статичного спаду напруги */
double calc_static_voltage(const PowerRail *rail, double current) {
    double r_total = rail->r_source_esr + rail->r_cable;
    return rail->v_nominal - current * r_total;
}

/* Розрахунок мінімальної необхідної ємності фільтра для стрибка струму */
double calc_required_decoupling_cap(double delta_i, double dt_response, double max_droop_v) {
    if (max_droop_v <= 0.0) return 0.0;
    return (delta_i * dt_response) / max_droop_v;
}

/* Перевірка працездатності системи при пуску навантаження */
void evaluate_power_stability(const PowerRail *rail, const DynamicLoad *load, double c_bulk_uf) {
    double c_bulk_f = c_bulk_uf * 1e-6;
    double r_total = rail->r_source_esr + rail->r_cable;
    
    /* Максимальний пусковий струм застопореного двигуна */
    double i_stall = rail->v_nominal / load->motor_r_winding;
    double i_peak_total = load->i_quiescent + i_stall;
    
    /* Статична напруга під повним пусковим струмом */
    double v_static_sag = rail->v_nominal - i_peak_total * r_total;
    
    /* Добротність еквівалентного RLC контуру */
    double q_factor = 0.0;
    if (r_total > 0.0 && c_bulk_f > 0.0) {
        q_factor = (1.0 / r_total) * sqrt(rail->l_cable / c_bulk_f);
    }
    
    printf("--- Аналіз стабільності шини живлення (C_bulk = %.1f мкФ) ---\n", c_bulk_uf);
    printf("  Пусковий струм навантаження: %.2f А (номінальний: %.2f А)\n", i_stall, load->motor_i_nominal);
    printf("  Статичний спад напруги на опорі (IR drop): %.3f В\n", i_peak_total * r_total);
    printf("  Напруга на шині під час пуску: %.3f В (поріг BOR: %.3f В)\n", v_static_sag, rail->v_bor_limit);
    printf("  Добротність контуру Q: %.2f (%s)\n", q_factor, 
           (q_factor > 0.5) ? "Схильність до дзвону (недодемпфовано)" : "Стабільно (демпфовано)");
    
    if (v_static_sag < rail->v_bor_limit) {
        printf("  [УВАГА] Ризик перезавантаження МК: напруга провалюється нижче порогу BOR!\n");
        double delta_v_allowed = rail->v_nominal - rail->v_bor_limit;
        double c_rec = calc_required_decoupling_cap(i_stall, 50e-6, delta_v_allowed);
        printf("  -> Рекомендована мінімальна ємність: %.1f мкФ\n", c_rec * 1e6);
    } else {
        printf("  [OK] Запас стійкості живлення: +%.3f В над порогом скидання.\n", v_static_sag - rail->v_bor_limit);
    }
    printf("\n");
}

int main(void) {
    /* Параметри реального кола: акумулятор 3.7 В, кабель 20 см */
    PowerRail rail = {
        .v_nominal = 3.70,
        .r_source_esr = 0.08,   /* 80 мОм акумулятор */
        .r_cable = 0.22,        /* 220 мОм провід та роз'єми */
        .l_cable = 180e-9,      /* 180 нГн індуктивність дротів */
        .v_bor_limit = 2.80     /* Поріг BOR мікроконтролера 2.80 В */
    };
    
    /* Параметри споживача: МК 30 мА + мікромотор 2 Ом */
    DynamicLoad load = {
        .i_quiescent = 0.030,
        .motor_r_winding = 2.0, /* 2.0 Ом обмотка */
        .motor_i_nominal = 0.250,
        .motor_t_ramp = 0.020
    };
    
    evaluate_power_stability(&rail, &load, 10.0);   /* Мала ємність 10 мкФ */
    evaluate_power_stability(&rail, &load, 470.0);  /* Об'ємний електроліт 470 мкФ */
    
    return 0;
}
