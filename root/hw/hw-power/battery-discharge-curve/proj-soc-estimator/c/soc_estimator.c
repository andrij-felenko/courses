/* soc_estimator.c — C-версія модуля оцінки стану заряду батареї */
#include <stdio.h>
#include <stdbool.h>

#define OCV_TABLE_SIZE 11

typedef struct {
    float soc_percent;     /* Точка SoC у відсотках (0.0 - 100.0) */
    float ocv_volts;       /* Напруга розімкненого кола в вольтах */
} OcvPoint;

/* Опорна крива OCV(SoC) для типового Li-ion елемента (3.7V nominal) */
static const OcvPoint ocv_lookup[OCV_TABLE_SIZE] = {
    {  0.0f, 3.00f},
    { 10.0f, 3.45f},
    { 20.0f, 3.68f},
    { 30.0f, 3.74f},
    { 40.0f, 3.77f},
    { 50.0f, 3.79f},
    { 60.0f, 3.83f},
    { 70.0f, 3.92f},
    { 80.0f, 4.02f},
    { 90.0f, 4.11f},
    {100.0f, 4.20f}
};

typedef struct {
    float nominal_capacity_ah;  /* Номінальна ємність батареї (А·год) */
    float internal_resistance;  /* Внутрішній опір R_i (Ом) */
    float v_cutoff;             /* Напруга відсічки (В) */
    float current_soc;          /* Поточний розрахований SoC (0.0 - 1.0) */
    float accumulated_mah;      /* Накопичений розряд в мА·год */
} BatteryEstimator;

void battery_estimator_init(BatteryEstimator *est, float capacity_ah, float r_internal_ohm, float v_cut) {
    est->nominal_capacity_ah = capacity_ah;
    est->internal_resistance = r_internal_ohm;
    est->v_cutoff = v_cut;
    est->current_soc = 1.0f; /* Початковий стан — 100% заряд */
    est->accumulated_mah = 0.0f;
}

/* Кусково-лінійна інтерполяція SoC за відновильним потенціалом OCV */
float ocv_to_soc(float ocv_volts) {
    if (ocv_volts <= ocv_lookup[0].ocv_volts) {
        return 0.0f;
    }
    if (ocv_volts >= ocv_lookup[OCV_TABLE_SIZE - 1].ocv_volts) {
        return 100.0f;
    }

    for (int i = 0; i < OCV_TABLE_SIZE - 1; i++) {
        if (ocv_volts >= ocv_lookup[i].ocv_volts && ocv_volts <= ocv_lookup[i + 1].ocv_volts) {
            float v_min = ocv_lookup[i].ocv_volts;
            float v_max = ocv_lookup[i + 1].ocv_volts;
            float soc_min = ocv_lookup[i].soc_percent;
            float soc_max = ocv_lookup[i + 1].soc_percent;

            float ratio = (ocv_volts - v_min) / (v_max - v_min);
            return soc_min + ratio * (soc_max - soc_min);
        }
    }
    return 0.0f;
}

/* Оновлення стану estimator на кожному такті вимірювання (dt в секундах) */
bool battery_estimator_update(BatteryEstimator *est, float v_cell, float current_amps, float dt_sec) {
    /* Перевірка критичної відсічки за напругою */
    if (v_cell <= est->v_cutoff) {
        est->current_soc = 0.0f;
        return false; /* Сигнал зупинити розряд */
    }

    /* Інтегрування струму (Coulomb Counting) */
    float delta_ah = (current_amps * dt_sec) / 3600.0f;
    est->accumulated_mah += delta_ah * 1000.0f;

    float soc_coulomb = est->current_soc - (delta_ah / est->nominal_capacity_ah);
    if (soc_coulomb < 0.0f) soc_coulomb = 0.0f;
    if (soc_coulomb > 1.0f) soc_coulomb = 1.0f;

    /* Якщо струм малий (|I| < 50 мА), корегуємо SoC за таблицею OCV */
    if (current_amps > -0.05f && current_amps < 0.05f) {
        float ocv_est = v_cell + current_amps * est->internal_resistance;
        float soc_ocv = ocv_to_soc(ocv_est) / 100.0f;

        /* Комплексне зважування (Alpha-filter): 95% Кулон + 5% OCV-корекція */
        est->current_soc = 0.95f * soc_coulomb + 0.05f * soc_ocv;
    } else {
        est->current_soc = soc_coulomb;
    }

    return true;
}
