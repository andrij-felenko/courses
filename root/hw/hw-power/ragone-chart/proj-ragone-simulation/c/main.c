#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура паспортних параметрів накопичувального елемента */
typedef struct {
    double v_oc_max;    /* Напруга холостого ходу при 100% SOC (Вольт) */
    double v_oc_min;    /* Напруга холостого ходу при 0% SOC (Вольт) */
    double v_cutoff;    /* Гранична напруга відсічки (Вольт) */
    double r_in;        /* Внутрішній опір постійному струму (Ом) */
    double capacity_ah; /* Номінальна електрична ємність (Ампер-години) */
    double mass_kg;     /* Повна маса осередку (кілограми) */
} EnergyStorage;

/* Структура результату розрахунку для однієї точки потужності */
typedef struct {
    double p_specific_w_kg;  /* Обчислена питома потужність (Вт/кг) */
    double e_specific_wh_kg; /* Обчислена питома енергія (Вт·год/кг) */
    double discharge_time_s; /* Повний час розряджання (секунди) */
    int is_valid;            /* Прапорець успішності симуляції (1/0) */
} RagonePoint;

/* Обчислення ЕРС залежно від поточного рівня зарядженості SOC (0.0 - 1.0) */
static double calculate_voc(const EnergyStorage *dev, double soc) {
    return dev->v_oc_min + soc * (dev->v_oc_max - dev->v_oc_min);
}

/* Основна функція симуляції розряду за постійної потужності P_const */
RagonePoint simulate_constant_power_c(const EnergyStorage *dev, double p_const, double dt_sec) {
    RagonePoint res = {0.0, 0.0, 0.0, 0};
    double soc = 1.0;
    double q_total_as = dev->capacity_ah * 3600.0; /* Переведення ємності в Кулони */
    double time_elapsed = 0.0;
    double energy_joules = 0.0;

    while (soc > 0.0) {
        double v_oc = calculate_voc(dev, soc);
        double discr = v_oc * v_oc - 4.0 * dev->r_in * p_const;

        /* Перевірка перевищення теоретичної межі потужності */
        if (discr < 0.0) {
            break;
        }

        /* Обчислення оптимального робочого струму */
        double current = (v_oc - sqrt(discr)) / (2.0 * dev->r_in);
        double v_terminal = v_oc - current * dev->r_in;

        /* Перевірка досягнення граничної напруги відсічки */
        if (v_terminal <= dev->v_cutoff) {
            break;
        }

        /* Дискретне оновлення стану системи */
        soc -= (current * dt_sec) / q_total_as;
        energy_joules += p_const * dt_sec;
        time_elapsed += dt_sec;
    }

    if (time_elapsed > 0.0) {
        res.p_specific_w_kg = p_const / dev->mass_kg;
        res.e_specific_wh_kg = (energy_joules / 3600.0) / dev->mass_kg;
        res.discharge_time_s = time_elapsed;
        res.is_valid = 1;
    }

    return res;
}

int main(void) {
    /* Параметри літій-іонного елемента 18650 (NMC 622) */
    EnergyStorage nmc_cell = {
        .v_oc_max = 4.2,
        .v_oc_min = 3.0,
        .v_cutoff = 2.8,
        .r_in = 0.025,      /* 25 міліом */
        .capacity_ah = 3.0, /* 3.0 А·год */
        .mass_kg = 0.048    /* 48 грамів */
    };

    printf("=== РЕЗУЛЬТАТИ СИМУЛЯЦІЇ ДІАГРАМИ РАГОНЕ (C) ===\n");
    printf("Питома потужність (Вт/кг) | Питома енергія (Вт·год/кг) | Час розряду (с)\n");
    printf("-----------------------------------------------------------------------\n");

    for (double p = 1.0; p <= 120.0; p *= 1.6) {
        RagonePoint pt = simulate_constant_power_c(&nmc_cell, p, 0.05);
        if (pt.is_valid) {
            printf("%25.2f | %26.2f | %15.1f\n",
                   pt.p_specific_w_kg, pt.e_specific_wh_kg, pt.discharge_time_s);
        }
    }

    return 0;
}
