#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    POL_LINEAR,
    POL_CIRCULAR_RHCP,
    POL_CIRCULAR_LHCP,
    POL_ELLIPTICAL_RHCP,
    POL_ELLIPTICAL_LHCP
} PolarizationClass;

typedef struct {
    double ex0;          /* Амплітуда E_x */
    double ey0;          /* Амплітуда E_y */
    double delta_deg;    /* Зсув фази у градусах (y відносно x) */
} FieldInput;

typedef struct {
    double s0, s1, s2, s3;  /* Параметри Стокса */
    double s1_norm, s2_norm, s3_norm;
    double major_axis;   /* Велика піввісь a */
    double minor_axis;   /* Мала піввісь b */
    double tilt_deg;     /* Кут нахилу tau (град) */
    double ellipticity_deg; /* Кут еліптичності chi (град) */
    double ar_linear;    /* Осьове відношення (лінійне) */
    double ar_db;        /* Осьове відношення (дБ) */
    PolarizationClass pol_class;
    double plf_linear_h; /* PLF для горизонтальної антени (0.0 .. 1.0) */
    double plf_rhcp;     /* PLF для ідеальної RHCP антени */
} PolarizationAnalysis;

static double deg_to_rad(double deg) {
    return deg * M_PI / 180.0;
}

static double rad_to_deg(double rad) {
    return rad * 180.0 / M_PI;
}

PolarizationAnalysis analyze_polarization(FieldInput input) {
    PolarizationAnalysis res;
    double delta = deg_to_rad(input.delta_deg);
    double ex2 = input.ex0 * input.ex0;
    double ey2 = input.ey0 * input.ey0;

    /* 1. Розрахунок базових параметрів Стокса */
    res.s0 = ex2 + ey2;
    res.s1 = ex2 - ey2;
    res.s2 = 2.0 * input.ex0 * input.ey0 * cos(delta);
    res.s3 = 2.0 * input.ex0 * input.ey0 * sin(delta);

    /* 2. Нормування векторів Стокса */
    if (res.s0 > 1e-12) {
        res.s1_norm = res.s1 / res.s0;
        res.s2_norm = res.s2 / res.s0;
        res.s3_norm = res.s3 / res.s0;
    } else {
        res.s1_norm = res.s2_norm = res.s3_norm = 0.0;
    }

    /* 3. Кут нахилу tau [-90..90] та кут еліптичності chi [-45..45] */
    double two_tau = atan2(res.s2, res.s1);
    res.tilt_deg = rad_to_deg(two_tau / 2.0);

    /* sin(2*chi) = s3 / s0 */
    double sin_two_chi = res.s3_norm;
    if (sin_two_chi > 1.0) sin_two_chi = 1.0;
    if (sin_two_chi < -1.0) sin_two_chi = -1.0;
    double two_chi = asin(sin_two_chi);
    res.ellipticity_deg = rad_to_deg(two_chi / 2.0);

    /* 4. Обчислення великої та малої півосей еліпса */
    double tan_chi = tan(two_chi / 2.0);
    double abs_tan_chi = fabs(tan_chi);
    
    double e_total = sqrt(res.s0);
    /* a = E_total * cos(chi), b = E_total * |sin(chi)| */
    res.major_axis = e_total * cos(two_chi / 2.0);
    res.minor_axis = e_total * fabs(sin(two_chi / 2.0));

    /* 5. Осьове відношення (Axial Ratio) */
    if (abs_tan_chi < 1e-6) {
        res.ar_linear = 1e6; /* Нескінченність для лінійної */
        res.ar_db = 99.9;
    } else {
        res.ar_linear = 1.0 / abs_tan_chi;
        res.ar_db = 20.0 * log10(res.ar_linear);
    }

    /* 6. Класифікація стану поляризації */
    if (res.ar_db > 20.0) {
        res.pol_class = POL_LINEAR;
    } else if (res.ar_db < 0.5) {
        res.pol_class = (res.s3 > 0) ? POL_CIRCULAR_RHCP : POL_CIRCULAR_LHCP;
    } else {
        res.pol_class = (res.s3 > 0) ? POL_ELLIPTICAL_RHCP : POL_ELLIPTICAL_LHCP;
    }

    /* 7. Розрахунок PLF для приймача */
    /* Для горизонтальної лінійної антени вектор s_r = (1, 0, 0) */
    res.plf_linear_h = 0.5 * (1.0 + res.s1_norm);
    /* Для ідеальної RHCP антени вектор s_r = (0, 0, +1) */
    res.plf_rhcp = 0.5 * (1.0 + res.s3_norm);

    return res;
}

const char* get_pol_class_name(PolarizationClass c) {
    switch (c) {
        case POL_LINEAR:          return "Лінійна (Linear)";
        case POL_CIRCULAR_RHCP:   return "Чиста колова RHCP";
        case POL_CIRCULAR_LHCP:   return "Чиста колова LHCP";
        case POL_ELLIPTICAL_RHCP: return "Еліптична (Праве обертання / RHCP)";
        case POL_ELLIPTICAL_LHCP: return "Еліптична (Ліве обертання / LHCP)";
    }
    return "Невідома";
}

int main(void) {
    FieldInput in = { .ex0 = 1.0, .ey0 = 0.8, .delta_deg = 80.0 };
    PolarizationAnalysis res = analyze_polarization(in);

    printf("=== Результати аналізу поляризаційного еліпса ===\n");
    printf("Вхідні дані: Ex0=%.2f, Ey0=%.2f, delta=%.1f deg\n", in.ex0, in.ey0, in.delta_deg);
    printf("Нормований вектор Стокса: s1=%.3f, s2=%.3f, s3=%.3f\n",
           res.s1_norm, res.s2_norm, res.s3_norm);
    printf("Кут нахилу (tau): %.2f deg\n", res.tilt_deg);
    printf("Кут еліптичності (chi): %.2f deg\n", res.ellipticity_deg);
    printf("Осьове відношення (AR): %.3f (%.2f дБ)\n", res.ar_linear, res.ar_db);
    printf("Класифікація стану: %s\n", get_pol_class_name(res.pol_class));
    printf("PLF при прийомі H-антеною: %.4f (%.2f дБ)\n", 
           res.plf_linear_h, 10.0 * log10(res.plf_linear_h));
    printf("PLF при прийомі RHCP-антеною: %.4f (%.2f дБ)\n", 
           res.plf_rhcp, 10.0 * log10(res.plf_rhcp));

    return 0;
}
