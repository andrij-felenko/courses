#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Результати розрахунку добротності та параметрів котушки */
typedef struct {
    double f0_hz;          /* Точна резонансна частота */
    double bw_3db_hz;      /* Смуга пропускання за рівнем -3 дБ */
    double q_loaded;       /* Навантажена добротність */
    double q_unloaded;     /* Ненавантажена (власна) добротність котушки */
    double esr_ohm;        /* Еквівалентний послідовний опір втрат (R_s) */
    double inductance_h;   /* Розрахована індуктивність на резонансі */
    bool is_valid;         /* Ознака успішного розрахунку */
} QFactorResult;

/* Структура вхідної точки вимірювання */
typedef struct {
    double freq_hz;        /* Частота генератора */
    double magnitude;      /* Амплітуда напруги або |S21| */
} SweepPoint;

/**
 * Обчислення добротності та екстракція параметрів котушки.
 * @param sweep Масив точок вимірювання (впорядкований за зростанням частоти)
 * @param count Кількість точок у масиві (мінімум 5)
 * @param z_system Характеристичний опір вимірювальної системи (типово 50.0 Ом)
 */
QFactorResult calculate_q_factor(const SweepPoint *sweep, size_t count, double z_system) {
    QFactorResult res = {0};
    if (!sweep || count < 5) {
        return res;
    }

    /* 1. Пошук грубого дискретного максимуму */
    size_t k = 0;
    double max_val = sweep[0].magnitude;
    for (size_t i = 1; i < count; ++i) {
        if (sweep[i].magnitude > max_val) {
            max_val = sweep[i].magnitude;
            k = i;
        }
    }

    /* Якщо максимум на краях діапазону — резонанс не захоплено */
    if (k == 0 || k == count - 1) {
        return res;
    }

    /* 2. Квадратична субпіксельна інтерполяція вершини */
    double y1 = sweep[k - 1].magnitude;
    double y2 = sweep[k].magnitude;
    double y3 = sweep[k + 1].magnitude;

    double denom = y1 - 2.0 * y2 + y3;
    if (fabs(denom) < 1e-15) {
        return res;
    }

    double delta = 0.5 * (y1 - y3) / denom;
    double df = sweep[k].freq_hz - sweep[k - 1].freq_hz;
    res.f0_hz = sweep[k].freq_hz + delta * df;
    double peak_mag = y2 - 0.25 * (y1 - y3) * delta;

    /* 3. Рівень половинної потужності (-3.01 дБ) */
    double target_3db = peak_mag * 0.7071067811865475;

    /* Пошук лівої межі f_low */
    double f_low = 0.0;
    bool found_low = false;
    for (size_t i = k; i > 0; --i) {
        if (sweep[i - 1].magnitude <= target_3db && sweep[i].magnitude >= target_3db) {
            double dy = sweep[i].magnitude - sweep[i - 1].magnitude;
            if (fabs(dy) > 1e-15) {
                double frac = (target_3db - sweep[i - 1].magnitude) / dy;
                f_low = sweep[i - 1].freq_hz + frac * (sweep[i].freq_hz - sweep[i - 1].freq_hz);
                found_low = true;
                break;
            }
        }
    }

    /* Пошук правої межі f_high */
    double f_high = 0.0;
    bool found_high = false;
    for (size_t i = k; i < count - 1; ++i) {
        if (sweep[i].magnitude >= target_3db && sweep[i + 1].magnitude <= target_3db) {
            double dy = sweep[i].magnitude - sweep[i + 1].magnitude;
            if (fabs(dy) > 1e-15) {
                double frac = (sweep[i].magnitude - target_3db) / dy;
                f_high = sweep[i].freq_hz + frac * (sweep[i + 1].freq_hz - sweep[i].freq_hz);
                found_high = true;
                break;
            }
        }
    }

    if (!found_low || !found_high || f_high <= f_low) {
        return res;
    }

    /* 4. Розрахунок смуги та добротності */
    res.bw_3db_hz = f_high - f_low;
    res.q_loaded = res.f0_hz / res.bw_3db_hz;

    /* Корекція навантаження системи для трансмісійного методу S21 */
    /* Коефіцієнт передачі на резонансі T_0 = peak_mag */
    double t0 = (peak_mag > 1.0) ? 1.0 : peak_mag;
    if (t0 > 0.001) {
        /* Власна ненавантажена добротність: Q0 = Q_L / (1 - T_0) */
        res.q_unloaded = res.q_loaded / (1.0 - t0);
        /* Еквівалентний послідовний опір втрат */
        res.esr_ohm = (2.0 * z_system) * (1.0 - t0) / t0;
    } else {
        res.q_unloaded = res.q_loaded;
        res.esr_ohm = 2.0 * z_system;
    }

    /* Індуктивність: L = Q0 * ESR / (2 * pi * f0) */
    double omega0 = 2.0 * 3.141592653589793 * res.f0_hz;
    res.inductance_h = (res.q_unloaded * res.esr_ohm) / omega0;
    res.is_valid = true;

    return res;
}

int main(void) {
    /* Демонстраційний масив сканування контуру з f0 = 10 МГц */
    SweepPoint data[] = {
        { 9.6e6, 0.120 },
        { 9.7e6, 0.220 },
        { 9.8e6, 0.450 },
        { 9.9e6, 0.780 },
        { 10.0e6, 0.940 },
        { 10.1e6, 0.810 },
        { 10.2e6, 0.480 },
        { 10.3e6, 0.240 },
        { 10.4e6, 0.130 }
    };
    size_t n = sizeof(data) / sizeof(data[0]);

    QFactorResult r = calculate_q_factor(data, n, 50.0);
    if (r.is_valid) {
        printf("Резонансна частота f0 : %.4f МГц\n", r.f0_hz / 1e6);
        printf("Смуга пропускання BW  : %.2f кГц\n", r.bw_3db_hz / 1e3);
        printf("Навантажена Q_L       : %.1f\n", r.q_loaded);
        printf("Власна добротність Q0 : %.1f\n", r.q_unloaded);
        printf("Втрати котушки ESR    : %.3f Ом\n", r.esr_ohm);
        printf("Індуктивність L       : %.2f мкГн\n", r.inductance_h * 1e6);
    } else {
        printf("Помилка розрахунку добротності: резонанс не знайдено.\n");
    }
    return 0;
}
