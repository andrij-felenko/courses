#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_LAYERS 32
#define DEG_TO_RAD (3.14159265358979323846 / 180.0)

/* Фізичні константи ортотропного моношару */
typedef struct {
    double E1;      /* Па: поздовжній модуль пружності вздовж волокна */
    double E2;      /* Па: поперечний модуль пружності перпендикулярно волокну */
    double G12;     /* Па: модуль зсуву в площині шару */
    double nu12;    /* безрозмірний: коефіцієнт Пуассона */
    double Xt;      /* Па: межа міцності на поздовжній розтяг */
    double Xc;      /* Па: межа міцності на поздовжній стиск */
    double Yt;      /* Па: межа міцності на поперечний розтяг */
    double Yc;      /* Па: межа міцності на поперечний стиск */
    double S;       /* Па: межа міцності на зсув у площині */
    double t_layer; /* м: товщина одного шару */
} PlyProperties;

/* Опис шаруватого пакета ламінату */
typedef struct {
    int num_layers;
    double angles[MAX_LAYERS];  /* кути укладки шарів у градусах */
} LaminateLayup;

/* Геометрія трубчастого променя дрона */
typedef struct {
    double length;          /* м: довжина консолі від центру рами до мотора */
    double outer_radius;    /* м: зовнішній радіус трубки */
    double inner_radius;    /* м: внутрішній радіус трубки */
} BeamGeometry;

/* Результати розрахунку */
typedef struct {
    double total_thickness; /* м: сумарна товщина стінки */
    double Ex_eff;          /* Па: ефективний поздовжній модуль */
    double Gxy_eff;         /* Па: ефективний модуль зсуву */
    double I_xx;            /* м⁴: осьовий момент інерції перерізу */
    double max_deflection;  /* м: прогин на кінці променя */
    double min_safety_factor;/* мінімальний коефіцієнт запасу міцності Цая-Ву */
    int critical_layer_idx;  /* індекс критичного шару */
} CalculationResult;

/* Обчислення матриці пружності шару Q */
static void calc_ply_Q(const PlyProperties* p, double Q[3][3]) {
    double nu21 = (p->nu12 * p->E2) / p->E1;
    double denom = 1.0 - p->nu12 * nu21;

    Q[0][0] = p->E1 / denom;
    Q[0][1] = (p->nu12 * p->E2) / denom;
    Q[0][2] = 0.0;

    Q[1][0] = Q[0][1];
    Q[1][1] = p->E2 / denom;
    Q[1][2] = 0.0;

    Q[2][0] = 0.0;
    Q[2][1] = 0.0;
    Q[2][2] = p->G12;
}

/* Трансформація матриці жорсткості під кутом theta (Q-bar) */
static void transform_Q(const double Q[3][3], double theta_deg, double Qbar[3][3]) {
    double rad = theta_deg * DEG_TO_RAD;
    double m = cos(rad);
    double n = sin(rad);
    double m2 = m * m;
    double n2 = n * n;
    double m4 = m2 * m2;
    double n4 = n2 * n2;
    double m2n2 = m2 * n2;

    double Q11 = Q[0][0], Q12 = Q[0][1], Q22 = Q[1][1], Q66 = Q[2][2];

    Qbar[0][0] = Q11 * m4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * n4;
    Qbar[1][1] = Q11 * n4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * m4;
    Qbar[0][1] = (Q11 + Q22 - 4.0 * Q66) * m2n2 + Q12 * (m4 + n4);
    Qbar[1][0] = Qbar[0][1];
    Qbar[2][2] = (Q11 + Q22 - 2.0 * Q12 - 2.0 * Q66) * m2n2 + Q66 * (m4 + n4);
    Qbar[0][2] = (Q11 - Q12 - 2.0 * Q66) * m * m2 * n + (Q12 - Q22 + 2.0 * Q66) * m * n * n2;
    Qbar[2][0] = Qbar[0][2];
    Qbar[1][2] = (Q11 - Q12 - 2.0 * Q66) * m * n * n2 + (Q12 - Q22 + 2.0 * Q66) * m * m2 * n;
    Qbar[2][1] = Qbar[1][2];
}

/* Оцінка коефіцієнта запасу за Цаєм-Ву для одного шару */
static double eval_tsai_wu_sf(const PlyProperties* p, double sigma1, double sigma2, double tau12) {
    double F1 = (1.0 / p->Xt) - (1.0 / p->Xc);
    double F2 = (1.0 / p->Yt) - (1.0 / p->Yc);
    double F11 = 1.0 / (p->Xt * p->Xc);
    double F22 = 1.0 / (p->Yt * p->Yc);
    double F66 = 1.0 / (p->S * p->S);
    double F12 = -0.5 * sqrt(F11 * F22);

    /* Рівняння: A * SF^2 + B * SF - 1 = 0 */
    double A_coef = F11 * sigma1 * sigma1 + F22 * sigma2 * sigma2 +
                    F66 * tau12 * tau12 + 2.0 * F12 * sigma1 * sigma2;
    double B_coef = F1 * sigma1 + F2 * sigma2;

    if (A_coef <= 1e-20) {
        if (B_coef <= 1e-20) return 999.0;
        return 1.0 / B_coef;
    }

    double discr = B_coef * B_coef + 4.0 * A_coef;
    if (discr < 0.0) return 0.0;

    return (-B_coef + sqrt(discr)) / (2.0 * A_coef);
}

/* Головна функція аналізу композитної консольної трубки */
bool analyze_composite_beam(
    const PlyProperties* mat,
    const LaminateLayup* layup,
    const BeamGeometry* geom,
    double thrust_force_n,
    CalculationResult* out
) {
    if (!mat || !layup || !geom || !out || layup->num_layers <= 0) {
        return false;
    }

    double Q[3][3];
    calc_ply_Q(mat, Q);

    double A[3][3] = {0};
    double H = layup->num_layers * mat->t_layer;

    for (int k = 0; k < layup->num_layers; ++k) {
        double Qbar[3][3];
        transform_Q(Q, layup->angles[k], Qbar);
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                A[i][j] += Qbar[i][j] * mat->t_layer;
            }
        }
    }

    /* Ефективні інженерні модулі */
    double Ex_eff = (A[0][0] * A[1][1] - A[0][1] * A[0][1]) / (H * A[1][1]);
    double Gxy_eff = A[2][2] / H;

    /* Геометричний момент інерції круглої трубки: I = pi/4 * (R_out^4 - R_in^4) */
    double Ro = geom->outer_radius;
    double Ri = geom->inner_radius;
    double I_xx = (3.14159265358979323846 / 4.0) * (pow(Ro, 4.0) - pow(Ri, 4.0));

    /* Максимальний прогин консолі w = F * L^3 / (3 * E * I) */
    double L = geom->length;
    double w_max = (thrust_force_n * pow(L, 3.0)) / (3.0 * Ex_eff * I_xx);

    /* Максимальний згинальний момент у защемленні */
    double M_bend = thrust_force_n * L;

    /* Оцінка напружень у шарах стінки трубки на зовнішньому радіусі */
    double eps_x_max = (M_bend * Ro) / (Ex_eff * I_xx);

    double min_sf = 1e9;
    int crit_layer = -1;

    for (int k = 0; k < layup->num_layers; ++k) {
        double rad = layup->angles[k] * DEG_TO_RAD;
        double m = cos(rad);
        double n = sin(rad);

        /* Деформації в осях волокна: розтяг/стиск від поздовжньої деформації eps_x */
        double eps1 = eps_x_max * m * m;
        double eps2 = eps_x_max * n * n;
        double gamma12 = -2.0 * eps_x_max * m * n;

        /* Напруження в осях волокна */
        double sigma1 = Q[0][0] * eps1 + Q[0][1] * eps2;
        double sigma2 = Q[1][0] * eps1 + Q[1][1] * eps2;
        double tau12  = Q[2][2] * gamma12;

        double sf = eval_tsai_wu_sf(mat, sigma1, sigma2, tau12);
        if (sf < min_sf) {
            min_sf = sf;
            crit_layer = k;
        }
    }

    out->total_thickness = H;
    out->Ex_eff = Ex_eff;
    out->Gxy_eff = Gxy_eff;
    out->I_xx = I_xx;
    out->max_deflection = w_max;
    out->min_safety_factor = min_sf;
    out->critical_layer_idx = crit_layer;

    return true;
}

int main(void) {
    /* Параметри односпрямованого вуглепластику Toray T700 / Epoxy */
    PlyProperties t700 = {
        .E1 = 135.0e9,       /* 135 ГПа */
        .E2 = 9.0e9,         /* 9.0 ГПа */
        .G12 = 4.8e9,        /* 4.8 ГПа */
        .nu12 = 0.30,
        .Xt = 2100.0e6,      /* 2100 МПа */
        .Xc = 1200.0e6,      /* 1200 МПа */
        .Yt = 50.0e6,        /* 50 МПа */
        .Yc = 180.0e6,       /* 180 МПа */
        .S = 75.0e6,         /* 75 МПа */
        .t_layer = 0.125e-3  /* 0.125 мм на шар (8 шарів = 1.0 мм) */
    };

    /* Квазіізотропний симетричний пакет [0 / 45 / -45 / 90]_s */
    LaminateLayup layup_quasi = {
        .num_layers = 8,
        .angles = {0.0, 45.0, -45.0, 90.0, 90.0, -45.0, 45.0, 0.0}
    };

    /* Геометрія променя квадрокоптера: трубка довжиною 350 мм, діаметр 25 мм, стінка 1 мм */
    BeamGeometry arm = {
        .length = 0.35,
        .outer_radius = 0.0125,
        .inner_radius = 0.0115
    };

    double thrust = 45.0; /* 45 Н (тяга мотора ~4.6 кгс) */
    CalculationResult res;

    if (analyze_composite_beam(&t700, &layup_quasi, &arm, thrust, &res)) {
        printf("--- Результати розрахунку композитного променя ---\n");
        printf("Товщина стінки: %.3f мм\n", res.total_thickness * 1e3);
        printf("Ефективний поздовжній модуль E_x: %.2f ГПа\n", res.Ex_eff / 1e9);
        printf("Ефективний модуль зсуву G_xy:   %.2f ГПа\n", res.Gxy_eff / 1e9);
        printf("Момент інерції перерізу I_xx:    %.4e м^4\n", res.I_xx);
        printf("Максимальний прогин під тягою:   %.3f мм\n", res.max_deflection * 1e3);
        printf("Мінімальний запас міцності (SF): %.2f (шар #%d)\n",
               res.min_safety_factor, res.critical_layer_idx + 1);
    }

    return 0;
}
