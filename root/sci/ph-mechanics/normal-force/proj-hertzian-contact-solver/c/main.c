#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Тип геометрії контакту */
typedef enum {
    HERTZ_POINT_SPHERE,  /* Точковий контакт (сфери, кулі, кругова пляма) */
    HERTZ_LINE_CYLINDER  /* Лінійний контакт (циліндри, ролики, прямокутна смуга) */
} HertzContactType;

/* Вхідні геометричні та механічні параметри */
typedef struct {
    HertzContactType type;
    double R1, R2;         /* Радіуси кривини тіл, м (для площини R2 = 1.0e12) */
    double length;         /* Довжина контакту для циліндра, м (для сфери = 0) */
    double E1, E2;         /* Модулі пружності Юнга, Па */
    double nu1, nu2;       /* Коефіцієнти Пуассона матеріалів */
    double yield_strength; /* Границя текучості слабшого матеріалу, Па */
} HertzInput;

/* Вихідні результати повного аналізу контакту */
typedef struct {
    double a_or_b;         /* Радіус кругової плями a або півширина смуги b, м */
    double delta;          /* Пружне нормальне зближення центрів тіл, м */
    double p0;             /* Максимальний контактний тиск у центрі, Па */
    double p_mean;         /* Середній контактний тиск по площі, Па */
    double tau_max;        /* Максимальне підповерхневе зсувне напруження, Па */
    double z_crit;         /* Глибина залягання піка зсувних напружень, м */
    double sigma_tensile;  /* Радіальне напруження розтягу на контурі контакту, Па */
    double safety_factor;  /* Коефіцієнт запасу міцності за критерієм Треска */
    bool is_purely_elastic;/* Чи перебуває з'єднання в суто пружному стані */
} HertzOutput;

/* Точка профілю напружень під центром контакту */
typedef struct {
    double depth_z;        /* Глибина заглиблення z, м */
    double zeta;           /* Безрозмірна глибина z / a */
    double sigma_z;        /* Вертикальне напруження стиснення, Па */
    double sigma_r;        /* Радіальне горизонтальне напруження, Па */
    double tau_max;        /* Максимальне зсувне напруження на глибині z, Па */
    double von_mises;      /* Еквівалентне напруження за фон Мізесом, Па */
} HertzStressPoint;

/* Обчислення приведеного контактного модуля пружності E* */
static inline double hertz_calc_e_star(double E1, double nu1, double E2, double nu2) {
    double inv_E = (1.0 - nu1 * nu1) / E1 + (1.0 - nu2 * nu2) / E2;
    return 1.0 / inv_E;
}

/* Обчислення еквівалентного радіуса кривини R */
static inline double hertz_calc_r_eq(double R1, double R2) {
    return (R1 * R2) / (R1 + R2);
}

/* Розв'язання прямої контактної задачі Герца */
bool hertz_solve(const HertzInput *in, double normal_force, HertzOutput *out) {
    if (!in || !out || normal_force <= 0.0 || in->R1 <= 0.0 || in->R2 <= 0.0) {
        return false;
    }
    if (in->E1 <= 0.0 || in->E2 <= 0.0 || in->yield_strength <= 0.0) {
        return false;
    }

    double R = hertz_calc_r_eq(in->R1, in->R2);
    double E_star = hertz_calc_e_star(in->E1, in->nu1, in->E2, in->nu2);

    if (in->type == HERTZ_POINT_SPHERE) {
        /* Точковий контакт сфер */
        out->a_or_b = cbrt((3.0 * normal_force * R) / (4.0 * E_star));
        out->delta = (out->a_or_b * out->a_or_b) / R;
        out->p0 = (3.0 * normal_force) / (2.0 * M_PI * out->a_or_b * out->a_or_b);
        out->p_mean = (2.0 / 3.0) * out->p0;

        /* Підповерхневий зсув та крайовий розтяг */
        out->tau_max = 0.3105 * out->p0;
        out->z_crit = 0.481 * out->a_or_b;
        out->sigma_tensile = out->p0 * (1.0 - 2.0 * in->nu1) / 3.0;
    } else {
        /* Лінійний контакт циліндрів */
        if (in->length <= 0.0) return false;

        out->a_or_b = sqrt((4.0 * normal_force * R) / (M_PI * in->length * E_star));
        out->delta = (out->a_or_b * out->a_or_b) / R;
        out->p0 = (2.0 * normal_force) / (M_PI * out->a_or_b * in->length);
        out->p_mean = (M_PI / 4.0) * out->p0;

        out->tau_max = 0.300 * out->p0;
        out->z_crit = 0.786 * out->a_or_b;
        out->sigma_tensile = 0.0;
    }

    /* Запас за критерієм текучості Треска: tau_max <= 0.5 * sigma_yield */
    double allowable_tau = 0.5 * in->yield_strength;
    out->safety_factor = allowable_tau / out->tau_max;
    out->is_purely_elastic = (out->safety_factor >= 1.0);

    return true;
}

/* Обчислення напруженого стану на заданій глибині z під центром точкового контакту */
bool hertz_point_stress_at_depth(const HertzInput *in, const HertzOutput *out, 
                                 double z, HertzStressPoint *pt) {
    if (!in || !out || !pt || z < 0.0 || out->a_or_b <= 0.0) {
        return false;
    }

    double a = out->a_or_b;
    double p0 = out->p0;
    double nu = in->nu1;
    double zeta = z / a;

    pt->depth_z = z;
    pt->zeta = zeta;
    pt->sigma_z = -p0 / (1.0 + zeta * zeta);

    if (zeta < 1.0e-7) {
        pt->sigma_r = -p0 * (1.0 + 2.0 * nu) / 2.0;
    } else {
        pt->sigma_r = -p0 * ((1.0 + nu) * (1.0 - zeta * atan(1.0 / zeta)) - 
                             0.5 / (1.0 + zeta * zeta));
    }

    pt->tau_max = 0.5 * fabs(pt->sigma_z - pt->sigma_r);
    pt->von_mises = fabs(pt->sigma_z - pt->sigma_r);

    return true;
}

int main(void) {
    /* Приклад 1: сталева кулька підшипника ШХ15 (R1 = 12 мм) на сталевій плоскій доріжці */
    HertzInput input = {
        .type = HERTZ_POINT_SPHERE,
        .R1 = 0.012,               /* 12 мм */
        .R2 = 1.0e12,              /* площина */
        .length = 0.0,
        .E1 = 210.0e9,             /* 210 ГПа */
        .E2 = 210.0e9,
        .nu1 = 0.30,
        .nu2 = 0.30,
        .yield_strength = 1900.0e6 /* 1900 МПа */
    };

    double normal_force = 2500.0; /* 2500 Н (~255 кг) */
    HertzOutput out;

    if (!hertz_solve(&input, normal_force, &out)) {
        fprintf(stderr, "Помилка розрахунку параметрів контакту!\n");
        return 1;
    }

    printf("================ РЕЗУЛЬТАТИ РОЗРАХУНКУ КОНТАКТУ ГЕРЦА (C99) ================\n");
    printf("Нормальне навантаження N:          %.1f Н\n", normal_force);
    printf("Радіус контактної плями a:         %.4f мм\n", out.a_or_b * 1e3);
    printf("Пружне зближення центрів delta:    %.3f мкм\n", out.delta * 1e6);
    printf("Піковий контактний тиск p0:        %.2f МПа\n", out.p0 / 1e6);
    printf("Середній контактний тиск p_mean:   %.2f МПа\n", out.p_mean / 1e6);
    printf("Макс. зсувне напруження tau_max:   %.2f МПа\n", out.tau_max / 1e6);
    printf("Глибина залягання піка z_crit:     %.4f мм (%.1f %% від a)\n", 
           out.z_crit * 1e3, (out.z_crit / out.a_or_b) * 100.0);
    printf("Крайовий розтяг sigma_tensile:     %.2f МПа\n", out.sigma_tensile / 1e6);
    printf("Коефіцієнт запасу за Треска:       %.2f (%s)\n\n", 
           out.safety_factor, out.is_purely_elastic ? "ПРУЖНИЙ СТАН" : "ПЛАСТИЧНА ТЕКУЧІСТЬ");

    /* Розрахунок та вивід епюри напружень по глибині під центром контакту */
    printf("--- Епюра напруженого стану по осі глибини z під центром контакту ---\n");
    printf(" z/a   | z (мкм) | sigma_z (МПа) | sigma_r (МПа) | tau_max (МПа) | sigma_vM (МПа)\n");
    printf("-------+---------+---------------+---------------+---------------+---------------\n");

    for (int step = 0; step <= 10; ++step) {
        double z = (step * 0.2) * out.a_or_b;
        HertzStressPoint pt;
        hertz_point_stress_at_depth(&input, &out, z, &pt);
        printf(" %4.2f  | %7.1f | %13.1f | %13.1f | %13.1f | %14.1f\n",
               pt.zeta, pt.depth_z * 1e6, 
               pt.sigma_z / 1e6, pt.sigma_r / 1e6, pt.tau_max / 1e6, pt.von_mises / 1e6);
    }

    return 0;
}
