#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define EPS_0 8.8541878128e-12  // Ф / м (електрична стала)
#define MU_0  1.2566370614e-6   // Гн / м (магнітна стала)
#define C_LIGHT 299792458.0     // м / с (швидкість світла)

typedef struct {
    double w_mm;        // Ширина провідника (мм)
    double s_mm;        // Зазор між провідниками (мм)
    double t_mm;        // Товщина фольги (мм)
    double h_mm;        // Висота діелектрика до землі (мм)
    double er_sub;      // Проникність діелектрика підкладки
    double t_mask_mm;   // Товщина паяльної маски (мм)
    double er_mask;     // Проникність паяльної маски
    double g_coplanar;  // Зазор до бічної землі CPWG (0 якщо без бічної землі)
} PcbGeometry_t;

typedef struct {
    double z_diff_ohm;     // Диференційний імпеданс (Ом)
    double z_comm_ohm;     // Синфазний імпеданс (Ом)
    double z_odd_ohm;      // Непарний імпеданс (Ом)
    double z_even_ohm;     // Парний імпеданс (Ом)
    double c_odd_pf_m;     // Непарна ємність (пФ/м)
    double c_even_pf_m;    // Парна ємність (пФ/м)
    double l_odd_nh_m;     // Непарна індуктивність (нГн/м)
    double l_even_nh_m;    // Парна індуктивність (нГн/м)
    double er_eff_odd;     // Ефективна діелектрична проникність (непарна)
    double er_eff_even;    // Ефективна діелектрична проникність (парна)
    double v_prop_odd_mm_ps;  // Фазова швидкість непарної моди (мм/пс)
    double v_prop_even_mm_ps; // Фазова швидкість парної моди (мм/пс)
    double fext_ps_m;      // Різниця затримок FEXT на метр траси (пс/м)
} SolverResult_t;

typedef struct {
    int nx;
    int ny;
    double dx;
    double dy;
    double* v;     // Масив потенціалів розміром nx * ny
    double* er;    // Масив проникностей розміром nx * ny
    bool* is_fixed;// Масив фіксованих граничних умов
} Grid2D_t;

Grid2D_t* grid_create(int nx, int ny, double dx, double dy) {
    Grid2D_t* g = (Grid2D_t*)malloc(sizeof(Grid2D_t));
    g->nx = nx;
    g->ny = ny;
    g->dx = dx;
    g->dy = dy;
    int size = nx * ny;
    g->v = (double*)calloc(size, sizeof(double));
    g->er = (double*)malloc(size * sizeof(double));
    g->is_fixed = (bool*)calloc(size, sizeof(bool));
    for (int i = 0; i < size; ++i) {
        g->er[i] = 1.0;
    }
    return g;
}

void grid_free(Grid2D_t* g) {
    if (g) {
        free(g->v);
        free(g->er);
        free(g->is_fixed);
        free(g);
    }
}

static inline int idx(const Grid2D_t* g, int i, int j) {
    return j * g->nx + i;
}

double grid_iterate_sor(Grid2D_t* g, double omega) {
    double max_diff = 0.0;
    int nx = g->nx;
    int ny = g->ny;

    for (int j = 1; j < ny - 1; ++j) {
        for (int i = 1; i < nx - 1; ++i) {
            int c = idx(g, i, j);
            if (g->is_fixed[c]) continue;

            double er_c = g->er[c];
            double er_r = 0.5 * (er_c + g->er[idx(g, i + 1, j)]);
            double er_l = 0.5 * (er_c + g->er[idx(g, i - 1, j)]);
            double er_t = 0.5 * (er_c + g->er[idx(g, i, j + 1)]);
            double er_b = 0.5 * (er_c + g->er[idx(g, i, j - 1)]);

            double sum_er = er_r + er_l + er_t + er_b;
            double v_gs = (er_r * g->v[idx(g, i + 1, j)] +
                           er_l * g->v[idx(g, i - 1, j)] +
                           er_t * g->v[idx(g, i, j + 1)] +
                           er_b * g->v[idx(g, i, j - 1)]) / sum_er;

            double v_new = (1.0 - omega) * g->v[c] + omega * v_gs;
            double diff = fabs(v_new - g->v[c]);
            if (diff > max_diff) {
                max_diff = diff;
            }
            g->v[c] = v_new;
        }
    }
    return max_diff;
}

double grid_compute_charge(const Grid2D_t* g, int x1, int x2, int y1, int y2) {
    double total_q = 0.0;
    double dx = g->dx;
    double dy = g->dy;

    for (int i = x1; i <= x2; ++i) {
        double er_mid = 0.5 * (g->er[idx(g, i, y1)] + g->er[idx(g, i, y1 - 1)]);
        double e_y = (g->v[idx(g, i, y1)] - g->v[idx(g, i, y1 - 1)]) / dy;
        total_q += EPS_0 * er_mid * e_y * dx;
    }
    for (int i = x1; i <= x2; ++i) {
        double er_mid = 0.5 * (g->er[idx(g, i, y2)] + g->er[idx(g, i, y2 + 1)]);
        double e_y = (g->v[idx(g, i, y2)] - g->v[idx(g, i, y2 + 1)]) / dy;
        total_q += EPS_0 * er_mid * e_y * dx;
    }
    for (int j = y1; j <= y2; ++j) {
        double er_mid = 0.5 * (g->er[idx(g, x1, j)] + g->er[idx(g, x1 - 1, j)]);
        double e_x = (g->v[idx(g, x1, j)] - g->v[idx(g, x1 - 1, j)]) / dx;
        total_q += EPS_0 * er_mid * e_x * dy;
    }
    for (int j = y1; j <= y2; ++j) {
        double er_mid = 0.5 * (g->er[idx(g, x2, j)] + g->er[idx(g, x2 + 1, j)]);
        double e_x = (g->v[idx(g, x2, j)] - g->v[idx(g, x2 + 1, j)]) / dx;
        total_q += EPS_0 * er_mid * e_x * dy;
    }

    return total_q;
}

SolverResult_t solve_diff_pair_fdm(const PcbGeometry_t* geo) {
    SolverResult_t res = { 0 };

    double total_width_mm = 6.0 * geo->h_mm + 2.0 * geo->w_mm + geo->s_mm;
    double total_height_mm = 5.0 * geo->h_mm;

    int nx = 240;
    int ny = 160;
    double dx = (total_width_mm * 1e-3) / (nx - 1);
    double dy = (total_height_mm * 1e-3) / (ny - 1);

    int gnd_j = 0;
    int sub_top_j = (int)round((geo->h_mm * 1e-3) / dy);
    int foil_top_j = sub_top_j + (int)round((geo->t_mm * 1e-3) / dy);
    int mask_top_j = foil_top_j + (int)round((geo->t_mask_mm * 1e-3) / dy);

    int mid_i = nx / 2;
    int s_half_nodes = (int)round(((geo->s_mm * 0.5) * 1e-3) / dx);
    int w_nodes = (int)round((geo->w_mm * 1e-3) / dx);

    int trace1_x1 = mid_i - s_half_nodes - w_nodes;
    int trace1_x2 = mid_i - s_half_nodes;
    int trace2_x1 = mid_i + s_half_nodes;
    int trace2_x2 = mid_i + s_half_nodes + w_nodes;

    double mu = 0.5 * (cos(M_PI / nx) + cos(M_PI / ny));
    double omega = 2.0 / (1.0 + sqrt(1.0 - mu * mu));

    double c_odd = 0.0, c_odd_0 = 0.0;
    double c_even = 0.0, c_even_0 = 0.0;

    for (int pass = 0; pass < 2; ++pass) {
        for (int mode = 0; mode < 2; ++mode) {
            Grid2D_t* g = grid_create(nx, ny, dx, dy);

            for (int j = 0; j < ny; ++j) {
                for (int i = 0; i < nx; ++i) {
                    if (pass == 0) {
                        if (j <= sub_top_j) {
                            g->er[idx(g, i, j)] = geo->er_sub;
                        } else if (j <= mask_top_j && geo->t_mask_mm > 0.0) {
                            g->er[idx(g, i, j)] = geo->er_mask;
                        } else {
                            g->er[idx(g, i, j)] = 1.0;
                        }
                    } else {
                        g->er[idx(g, i, j)] = 1.0;
                    }
                }
            }

            for (int i = 0; i < nx; ++i) {
                int c = idx(g, i, gnd_j);
                g->v[c] = 0.0;
                g->is_fixed[c] = true;
            }

            double v1 = 1.0;
            double v2 = (mode == 0) ? -1.0 : 1.0;

            for (int j = sub_top_j; j <= foil_top_j; ++j) {
                for (int i = trace1_x1; i <= trace1_x2; ++i) {
                    int c = idx(g, i, j);
                    g->v[c] = v1;
                    g->is_fixed[c] = true;
                }
                for (int i = trace2_x1; i <= trace2_x2; ++i) {
                    int c = idx(g, i, j);
                    g->v[c] = v2;
                    g->is_fixed[c] = true;
                }
            }

            for (int iter = 0; iter < 1200; ++iter) {
                double diff = grid_iterate_sor(g, omega);
                if (diff < 1e-6) break;
            }

            int bx1 = trace1_x1 - 4;
            int bx2 = trace1_x2 + 2;
            int by1 = sub_top_j - 4;
            int by2 = foil_top_j + 4;
            if (bx1 < 1) bx1 = 1;
            if (by1 < 1) by1 = 1;

            double q = grid_compute_charge(g, bx1, bx2, by1, by2);

            if (pass == 0 && mode == 0) c_odd = q / 1.0;
            if (pass == 0 && mode == 1) c_even = q / 1.0;
            if (pass == 1 && mode == 0) c_odd_0 = q / 1.0;
            if (pass == 1 && mode == 1) c_even_0 = q / 1.0;

            grid_free(g);
        }
    }

    res.c_odd_pf_m = c_odd * 1e12;
    res.c_even_pf_m = c_even * 1e12;

    res.l_odd_nh_m = (1.0 / (C_LIGHT * C_LIGHT * c_odd_0)) * 1e9;
    res.l_even_nh_m = (1.0 / (C_LIGHT * C_LIGHT * c_even_0)) * 1e9;

    res.er_eff_odd = c_odd / c_odd_0;
    res.er_eff_even = c_even / c_even_0;

    res.z_odd_ohm = 1.0 / (C_LIGHT * sqrt(c_odd * c_odd_0));
    res.z_even_ohm = 1.0 / (C_LIGHT * sqrt(c_even * c_even_0));

    res.z_diff_ohm = 2.0 * res.z_odd_ohm;
    res.z_comm_ohm = 0.5 * res.z_even_ohm;

    res.v_prop_odd_mm_ps = (C_LIGHT / sqrt(res.er_eff_odd)) * 1e-9;
    res.v_prop_even_mm_ps = (C_LIGHT / sqrt(res.er_eff_even)) * 1e-9;

    double t_odd_ps_m = (1.0e12 / (res.v_prop_odd_mm_ps * 1e12)) * 1e3;
    double t_even_ps_m = (1.0e12 / (res.v_prop_even_mm_ps * 1e12)) * 1e3;
    res.fext_ps_m = fabs(t_even_ps_m - t_odd_ps_m);

    return res;
}

SolverResult_t solve_diff_pair_wadell(const PcbGeometry_t* geo) {
    SolverResult_t res = { 0 };

    double w = geo->w_mm;
    double h = geo->h_mm;
    double t = geo->t_mm;
    double s = geo->s_mm;
    double er = geo->er_sub;

    double dw = (t / M_PI) * (1.0 + log(2.0 * h / t));
    double w_eff = w + dw;

    double u = w_eff / h;
    double er_eff_single = 0.5 * (er + 1.0) + 0.5 * (er - 1.0) * pow(1.0 + 12.0 / u, -0.5);
    double z0 = (376.73 / sqrt(er_eff_single)) / (u + 1.393 + 0.667 * log(u + 1.444));

    res.z_diff_ohm = 2.0 * z0 * (1.0 - 0.48 * exp(-0.96 * (s / h)));
    res.z_comm_ohm = 0.5 * z0 * (1.0 + 0.86 * exp(-1.15 * (s / h)));

    if (geo->t_mask_mm > 0.0) {
        res.z_diff_ohm *= 0.965;
        res.z_comm_ohm *= 0.970;
    }

    res.z_odd_ohm = res.z_diff_ohm * 0.5;
    res.z_even_ohm = res.z_comm_ohm * 2.0;

    res.er_eff_odd = er_eff_single * 0.95;
    res.er_eff_even = er_eff_single * 1.05;

    res.v_prop_odd_mm_ps = (C_LIGHT / sqrt(res.er_eff_odd)) * 1e-9;
    res.v_prop_even_mm_ps = (C_LIGHT / sqrt(res.er_eff_even)) * 1e-9;

    return res;
}

void print_solver_report(const char* title, const PcbGeometry_t* geo, const SolverResult_t* res) {
    printf("=================================================================\n");
    printf("  %s\n", title);
    printf("=================================================================\n");
    printf(" Геометрія: w=%.3f мм, s=%.3f мм, h=%.3f мм, t=%.3f мм, er=%.2f\n",
           geo->w_mm, geo->s_mm, geo->h_mm, geo->t_mm, geo->er_sub);
    if (geo->t_mask_mm > 0.0) {
        printf(" Маска    : t_mask=%.3f мм, er_mask=%.2f\n", geo->t_mask_mm, geo->er_mask);
    }
    printf("-----------------------------------------------------------------\n");
    printf(" Диференційний імпеданс Z_diff : %.2f Ом\n", res->z_diff_ohm);
    printf(" Синфазний імпеданс     Z_comm : %.2f Ом\n", res->z_comm_ohm);
    printf(" Модальні опори (Odd / Even)   : %.2f Ом / %.2f Ом\n", res->z_odd_ohm, res->z_even_ohm);
    printf(" Погонна ємність C_odd         : %.2f пФ/м (C_even = %.2f пФ/м)\n", res->c_odd_pf_m, res->c_even_pf_m);
    printf(" Погонна індуктивність L_odd   : %.2f нГн/м (L_even = %.2f нГн/м)\n", res->l_odd_nh_m, res->l_even_nh_m);
    printf(" Ефективна діелектрична ε_eff  : Odd=%.3f, Even=%.3f\n", res->er_eff_odd, res->er_eff_even);
    printf(" Фазова швидкість v_prop       : Odd=%.4f мм/пс, Even=%.4f мм/пс\n", 
           res->v_prop_odd_mm_ps, res->v_prop_even_mm_ps);
    if (res->fext_ps_m > 0.0) {
        printf(" Фазовий перекіс FEXT          : %.2f пс / метр\n", res->fext_ps_m);
    }
    printf("=================================================================\n\n");
}
