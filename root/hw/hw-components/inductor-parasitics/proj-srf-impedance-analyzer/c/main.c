#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double freq_hz;
    double s11_re;
    double s11_im;
} VnaPoint;

typedef struct {
    double freq_hz;
    double r_ohm;
    double x_ohm;
    double z_mag;
    double q_factor;
} ImpedancePoint;

typedef struct {
    double dcr_ohm;
    double l0_henry;
    double srf_hz;
    double epc_farad;
    double r_peak_ohm;
    double q_max;
    double q_max_freq_hz;
    bool srf_found;
} InductorModel;

static bool s11_to_z(const VnaPoint* pt, double z0, ImpedancePoint* out_z) {
    double denom = (1.0 - pt->s11_re) * (1.0 - pt->s11_re) + (pt->s11_im * pt->s11_im);
    if (denom < 1e-15) {
        return false;
    }
    
    out_z->freq_hz = pt->freq_hz;
    out_z->r_ohm = z0 * (1.0 - pt->s11_re * pt->s11_re - pt->s11_im * pt->s11_im) / denom;
    out_z->x_ohm = z0 * (2.0 * pt->s11_im) / denom;
    out_z->z_mag = sqrt(out_z->r_ohm * out_z->r_ohm + out_z->x_ohm * out_z->x_ohm);
    
    if (out_z->r_ohm > 1e-9) {
        out_z->q_factor = fabs(out_z->x_ohm) / out_z->r_ohm;
    } else {
        out_z->q_factor = 0.0;
    }
    return true;
}

bool extract_inductor_parasitics(const VnaPoint* points, size_t count, double z0, InductorModel* result) {
    if (!points || count < 3 || !result) {
        return false;
    }

    result->dcr_ohm = 0.0;
    result->l0_henry = 0.0;
    result->srf_hz = 0.0;
    result->epc_farad = 0.0;
    result->r_peak_ohm = 0.0;
    result->q_max = 0.0;
    result->q_max_freq_hz = 0.0;
    result->srf_found = false;

    ImpedancePoint prev_z, curr_z;
    if (!s11_to_z(&points[0], z0, &curr_z)) {
        return false;
    }

    result->dcr_ohm = curr_z.r_ohm;
    
    /* Оцінка L0 на першій ненульовій низькій частоті */
    if (curr_z.freq_hz > 10.0 && curr_z.x_ohm > 0.0) {
        result->l0_henry = curr_z.x_ohm / (2.0 * M_PI * curr_z.freq_hz);
    }

    result->q_max = curr_z.q_factor;
    result->q_max_freq_hz = curr_z.freq_hz;

    for (size_t i = 1; i < count; ++i) {
        prev_z = curr_z;
        if (!s11_to_z(&points[i], z0, &curr_z)) {
            continue;
        }

        /* Оновлення пікової добротності */
        if (curr_z.q_factor > result->q_max && curr_z.x_ohm > 0.0) {
            result->q_max = curr_z.q_factor;
            result->q_max_freq_hz = curr_z.freq_hz;
        }

        /* Уточнення оцінки L0 в індуктивній зоні */
        if (result->l0_henry <= 0.0 && curr_z.x_ohm > 0.0 && curr_z.freq_hz > 100.0) {
            result->l0_henry = curr_z.x_ohm / (2.0 * M_PI * curr_z.freq_hz);
        }

        /* Пошук точки зміни знака реактивного опору (SRF) */
        if (!result->srf_found && prev_z.x_ohm > 0.0 && curr_z.x_ohm <= 0.0) {
            double dx = curr_z.x_ohm - prev_z.x_ohm;
            double frac = (fabs(dx) > 1e-12) ? (-prev_z.x_ohm / dx) : 0.5;
            result->srf_hz = prev_z.freq_hz + frac * (curr_z.freq_hz - prev_z.freq_hz);
            result->r_peak_ohm = prev_z.r_ohm + frac * (curr_z.r_ohm - prev_z.r_ohm);
            result->srf_found = true;
        }
    }

    /* Якщо знайдено SRF та L0, розраховуємо EPC */
    if (result->srf_found && result->l0_henry > 0.0 && result->srf_hz > 0.0) {
        double omega_srf = 2.0 * M_PI * result->srf_hz;
        result->epc_farad = 1.0 / (omega_srf * omega_srf * result->l0_henry);
    }

    return true;
}

int main(void) {
    /* Синтетичні дані вимірювання дроселя 10 мкГн, DCR = 0.15 Ом, EPC = 4.5 пФ (SRF ≈ 23.7 МГц) */
    const size_t num_points = 5;
    VnaPoint dataset[5] = {
        { 100000.0,    0.0029,  0.0628 },   /* 100 кГц */
        { 1000000.0,   0.0035,  0.6270 },   /* 1 МГц */
        { 10000000.0,  0.0520,  0.9200 },   /* 10 МГц */
        { 23720000.0,  0.9650,  0.0010 },   /* 23.72 МГц (SRF) */
        { 50000000.0,  0.0810, -0.8500 }    /* 50 МГц (Ємнісна зона) */
    };

    InductorModel model;
    if (extract_inductor_parasitics(dataset, num_points, 50.0, &model)) {
        printf("--- Результати екстракції моделі котушки ---\n");
        printf("DCR:            %.3f Ом\n", model.dcr_ohm);
        printf("Індуктивність L0: %.3f мкГн\n", model.l0_henry * 1e6);
        if (model.srf_found) {
            printf("Частота SRF:    %.2f МГц\n", model.srf_hz / 1e6);
            printf("Паразитна EPC:  %.2f пФ\n", model.epc_farad * 1e12);
            printf("Піковий опір:   %.1f кОм\n", model.r_peak_ohm / 1e3);
        } else {
            printf("SRF не досягнуто у діапазоні вимірювання\n");
        }
        printf("Макс. добротність Q: %.1f на частоті %.2f МГц\n", 
               model.q_max, model.q_max_freq_hz / 1e6);
    }
    return 0;
}
