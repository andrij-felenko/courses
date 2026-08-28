#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define SPEED_OF_LIGHT_MM_NS 299.792458
#define ETA0 376.7303135

typedef struct {
    double er;        /* відносна діелектрична проникність */
    double h_mm;      /* товщина діелектрика, мм */
    double t_mm;      /* товщина металізації фольги, мм */
    double tan_delta; /* тангенс кута діелектричних втрат */
} Substrate;

typedef struct {
    double w_mm;          /* фізична ширина смужки, мм */
    double u;             /* нормована ширина w/h */
    double z0_ohms;       /* хвильовий опір, Ом */
    double eps_eff_0;     /* статична проникність (f=0) */
    double eps_eff_f;     /* дисперсійна проникність на частоті f */
    double lambda_g_mm;   /* довжина хвилі у мікросмужці, мм */
    double vp_mm_ns;      /* фазова швидкість, мм/нс */
    double delta_l_mm;    /* крайове подовження шлейфа, мм */
    double length_qtr_mm; /* скоригована чвертьхвильова довжина, мм */
} MicrostripResult;

typedef struct {
    double dist_to_load_mm; /* відстань d від навантаження до шлейфа */
    double stub_length_mm;  /* довжина розімкненого шлейфа з компенсацією delta_l */
    double stub_width_mm;   /* ширина шлейфа */
    double stub_z0_ohms;    /* хвильовий опір шлейфа */
} SingleStubMatch;

/* Розрахунок статичної ефективної проникності за Гаммерстадом-Єнсеном */
static double calc_eps_eff_static(double u, double er) {
    double a_u = 1.0 + (1.0 / 49.0) * log((pow(u, 4) + pow(u / 52.0, 2)) / (pow(u, 4) + 0.432))
                 + (1.0 / 18.7) * log(1.0 + pow(u / 18.1, 3));
    double b_er = 0.564 * pow((er - 0.9) / (er + 3.0), 0.05);
    double factor = pow(1.0 + 10.0 / u, -a_u * b_er);
    return ((er + 1.0) / 2.0) + ((er - 1.0) / 2.0) * factor;
}

/* Обчислення хвильового опору за нормованою шириною u = w/h */
static double calc_z0_from_u(double u, double er) {
    double eps_eff = calc_eps_eff_static(u, er);
    if (u <= 1.0) {
        double f_u = 6.0 + (2.0 * M_PI - 6.0) * exp(-pow(30.666 / u, 0.752));
        return (ETA0 / (2.0 * M_PI * sqrt(eps_eff))) * log(f_u / u + sqrt(1.0 + pow(2.0 / u, 2)));
    } else {
        return (ETA0 / sqrt(eps_eff)) * (1.0 / (u + 1.393 + 0.667 * log(u + 1.444)));
    }
}

/* Інверсія Z0 -> u методом дихотомії (чисельної бісекції) */
static double solve_u_for_z0(double target_z0, double er) {
    double u_min = 0.001;
    double u_max = 100.0;
    for (int iter = 0; iter < 100; ++iter) {
        double u_mid = 0.5 * (u_min + u_max);
        double z_mid = calc_z0_from_u(u_mid, er);
        if (fabs(z_mid - target_z0) < 1e-6) {
            return u_mid;
        }
        if (z_mid > target_z0) {
            u_min = u_mid; /* ширша доріжка має нижчий опір */
        } else {
            u_max = u_mid;
        }
    }
    return 0.5 * (u_min + u_max);
}

/* Модель частотної дисперсії Кіршнінга-Янсена */
static double calc_eps_eff_dispersion(double u, double er, double h_mm, double f_ghz, double eps_eff_0) {
    double h_cm = h_mm * 0.1;
    double fn = f_ghz * h_cm;
    double p1 = 0.27488 + (0.6315 + 0.525 / pow(1.0 + 0.0157 * fn, 20.0)) * u
                - 0.065683 * exp(-8.7513 * u);
    double p2 = 0.33622 * (1.0 - exp(-0.03442 * er));
    double p3 = 0.0363 * exp(-4.6 * u) * (1.0 - exp(-pow(fn / 3.87, 4.97)));
    double p4 = 1.0 + 2.751 * (1.0 - exp(-pow(er / 15.916, 8.0)));
    double p_f = p1 * p2 * pow((0.1844 + p3 * p4) * 10.0 * fn, 1.5763);

    return er - ((er - eps_eff_0) / (1.0 + p_f));
}

/* Крайове подовження розімкненого кінця за Гаммерстадом */
static double calc_delta_l_mm(double u, double eps_eff, double h_mm) {
    double factor = 0.412 * ((eps_eff + 0.3) / (eps_eff - 0.258)) * ((u + 0.264) / (u + 0.8));
    return factor * h_mm;
}

MicrostripResult synthesize_microstrip(const Substrate *sub, double target_z0, double f_ghz) {
    MicrostripResult res;
    res.u = solve_u_for_z0(target_z0, sub->er);
    res.w_mm = res.u * sub->h_mm;
    res.z0_ohms = calc_z0_from_u(res.u, sub->er);
    res.eps_eff_0 = calc_eps_eff_static(res.u, sub->er);
    res.eps_eff_f = calc_eps_eff_dispersion(res.u, sub->er, sub->h_mm, f_ghz, res.eps_eff_0);

    double lambda_0 = SPEED_OF_LIGHT_MM_NS / f_ghz;
    res.lambda_g_mm = lambda_0 / sqrt(res.eps_eff_f);
    res.vp_mm_ns = SPEED_OF_LIGHT_MM_NS / sqrt(res.eps_eff_f);
    res.delta_l_mm = calc_delta_l_mm(res.u, res.eps_eff_f, sub->h_mm);
    res.length_qtr_mm = (res.lambda_g_mm * 0.25) - res.delta_l_mm;

    return res;
}

/* Синтез одношлейфового узгоджувача для навантаження Z_L = R_L + j*X_L */
SingleStubMatch synthesize_single_stub(const Substrate *sub, double z0_feed,
                                       double r_load, double x_load, double f_ghz) {
    SingleStubMatch match;
    MicrostripResult feed_line = synthesize_microstrip(sub, z0_feed, f_ghz);
    match.stub_width_mm = feed_line.w_mm;
    match.stub_z0_ohms = z0_feed;

    /* Нормований імпеданс та адмітанс */
    double z_mag2 = r_load * r_load + x_load * x_load;
    double g_load = (r_load / z_mag2) * z0_feed;
    double b_load = (-x_load / z_mag2) * z0_feed;

    /* Відстань d до шлейфа (де g = 1) */
    double t;
    if (fabs(g_load - 1.0) < 1e-5) {
        t = 0.0;
    } else {
        t = (b_load + sqrt(g_load * (pow(1.0 - g_load, 2) + b_load * b_load))) / (g_load - 1.0);
    }
    double theta_d = atan(t);
    if (theta_d < 0.0) theta_d += M_PI;
    match.dist_to_load_mm = (theta_d / (2.0 * M_PI)) * feed_line.lambda_g_mm;

    /* Сусептанс шлейфа B_stub = -B_in */
    double b_in = (b_load + g_load * g_load * t + b_load * b_load * t - t) / (pow(1.0 - b_load * t, 2) + pow(g_load * t, 2));
    double b_stub = -b_in;

    /* Довжина розімкненого шлейфа (b_stub = tan(theta_stub)) */
    double theta_stub = atan(b_stub);
    if (theta_stub < 0.0) theta_stub += M_PI;
    double l_stub_ideal = (theta_stub / (2.0 * M_PI)) * feed_line.lambda_g_mm;
    match.stub_length_mm = l_stub_ideal - feed_line.delta_l_mm;

    return match;
}

/* Розрахунок частотної характеристики S11 та КСХ */
void print_frequency_sweep(const Substrate *sub, double z_feed, double z_load,
                           const MicrostripResult *trans, double f_center_ghz) {
    printf("--- Частотна характеристика узгодження (S11 та КСХ) ---\n");
    printf(" Частота (ГГц) | eps_eff(f) |  |S11|  | Return Loss (дБ) |  КСХ  \n");
    printf("---------------+------------+--------+------------------+-------\n");

    for (double f = f_center_ghz - 2.0; f <= f_center_ghz + 2.001; f += 0.5) {
        double eps_f = calc_eps_eff_dispersion(trans->u, sub->er, sub->h_mm, f, trans->eps_eff_0);
        double beta = (2.0 * M_PI * f / SPEED_OF_LIGHT_MM_NS) * sqrt(eps_f);
        double theta = beta * (trans->lambda_g_mm * 0.25);

        double cos_th = cos(theta);
        double sin_th = sin(theta);

        double re_num = z_load * cos_th;
        double im_num = trans->z0_ohms * sin_th;
        double re_den = cos_th;
        double im_den = (z_load / trans->z0_ohms) * sin_th;

        double den_mag2 = re_den * re_den + im_den * im_den;
        double z_in_re = (re_num * re_den + im_num * im_den) / den_mag2;
        double z_in_im = (im_num * re_den - re_num * im_den) / den_mag2;

        double num_re = z_in_re - z_feed;
        double num_im = z_in_im;
        double den_re = z_in_re + z_feed;
        double den_im = z_in_im;

        double gamma_mag = sqrt((num_re * num_re + num_im * num_im) / (den_re * den_re + den_im * den_im));
        double return_loss = (gamma_mag > 1e-5) ? -20.0 * log10(gamma_mag) : 60.0;
        double vswr = (1.0 + gamma_mag) / (1.0 - gamma_mag);

        printf("    %5.2f      |   %6.4f   | %6.4f |      %6.2f      | %5.2f \n",
               f, eps_f, gamma_mag, return_loss, vswr);
    }
    printf("\n");
}

int main(void) {
    Substrate rogers4350 = { .er = 3.66, .h_mm = 0.508, .t_mm = 0.035, .tan_delta = 0.0037 };
    double freq_ghz = 5.80;

    printf("=== СИНТЕЗ МІКРОСМУЖКОВИХ ЕЛЕМЕНТІВ (C99) ===\n");
    printf("Параметри підкладки: Rogers RO4350B (er=%.2f, h=%.3f мм, f=%.2f ГГц)\n\n",
           rogers4350.er, rogers4350.h_mm, freq_ghz);

    /* 1. Магістральна лінія 50 Ом */
    MicrostripResult line50 = synthesize_microstrip(&rogers4350, 50.0, freq_ghz);
    printf("1. Магістральна лінія 50 Ом:\n");
    printf("   Ширина доріжки w: %.3f мм (w/h = %.3f)\n", line50.w_mm, line50.u);
    printf("   Ефективна проникність: статична = %.4f -> з дисперсією = %.4f (+%.2f%%)\n",
           line50.eps_eff_0, line50.eps_eff_f,
           ((line50.eps_eff_f - line50.eps_eff_0) / line50.eps_eff_0) * 100.0);
    printf("   Довжина хвилі lambda_g: %.3f мм (у вакуумі lambda_0 = %.3f мм)\n",
           line50.lambda_g_mm, SPEED_OF_LIGHT_MM_NS / freq_ghz);
    printf("   Фазова швидкість v_p: %.2f мм/нс (VF = %.3f)\n\n",
           line50.vp_mm_ns, line50.vp_mm_ns / SPEED_OF_LIGHT_MM_NS);

    /* 2. Чвертьхвильовий трансформатор 50 Ом -> 100 Ом */
    double z_load = 100.0;
    double z_trans = sqrt(50.0 * z_load); /* 70.71 Ом */
    MicrostripResult trans = synthesize_microstrip(&rogers4350, z_trans, freq_ghz);
    printf("2. Трансформатор lambda/4 (50 Ом -> 100 Ом, Z_T = %.2f Ом):\n", z_trans);
    printf("   Ширина секції w_T: %.3f мм (w/h = %.3f)\n", trans.w_mm, trans.u);
    printf("   eps_eff(5.8 ГГц): %.4f\n", trans.eps_eff_f);
    printf("   Фізична довжина трансформатора L_T: %.3f мм\n\n", trans.lambda_g_mm * 0.25);

    /* 3. Розімкнений шлейф 50 Ом */
    printf("3. Розімкнений узгоджувальний шлейф lambda/4 (50 Ом):\n");
    printf("   Крайове подовження розриву delta_l: %.3f мм\n", line50.delta_l_mm);
    printf("   Скоригована фізична довжина L_stub: %.3f мм (замість %.3f мм)\n\n",
           line50.length_qtr_mm, line50.lambda_g_mm * 0.25);

    /* 4. Одношлейфовий узгоджувач для комплексного навантаження Z_L = 25 - j*35 Ом */
    SingleStubMatch stub_match = synthesize_single_stub(&rogers4350, 50.0, 25.0, -35.0, freq_ghz);
    printf("4. Синтез одношлейфового узгоджувача для Z_L = 25 - j*35 Ом:\n");
    printf("   Відстань d від навантаження: %.3f мм\n", stub_match.dist_to_load_mm);
    printf("   Фізична довжина розімкненого шлейфа: %.3f мм (ширина w = %.3f мм)\n\n",
           stub_match.stub_length_mm, stub_match.stub_width_mm);

    /* 5. Частотна характеристика */
    print_frequency_sweep(&rogers4350, 50.0, z_load, &trans, freq_ghz);

    return 0;
}
