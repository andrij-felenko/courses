#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_PANELS 120

typedef struct {
    double x, y;
} Point;

typedef struct {
    Point p1, p2;     /* Вузли панелі */
    Point cp;         /* Контрольна точка колокації */
    double length;    /* Довжина панелі S_i */
    double theta;     /* Кут нахилу */
    Point normal;     /* Одинична нормаль n_i (назовні) */
    Point tangent;    /* Одинична дотична t_i */
    double gamma;     /* Розрахована інтенсивність вихорів */
    double cp_val;    /* Коефіцієнт тиску C_p */
} Panel;

/* Генерація контуру NACA 4-значного профілю за годинниковою стрілкою від TE */
int generate_naca4(int m_digit, int p_digit, int t_digit, int num_panels, Panel *panels) {
    if (num_panels % 2 != 0 || num_panels > MAX_PANELS) return 0;
    int half_pts = num_panels / 2;
    double m = m_digit / 100.0;
    double p = p_digit / 10.0;
    double t = t_digit / 100.0;

    Point nodes[MAX_PANELS + 1];
    int n_nodes = 0;

    /* Нижній контур від TE (x=1.0) до LE (x=0.0) */
    for (int i = 0; i <= half_pts; i++) {
        double beta = (M_PI * i) / half_pts;
        double x = 0.5 * (1.0 + cos(beta)); /* 1.0 -> 0.0 */
        double yt = 5.0 * t * (0.2969 * sqrt(x) - 0.1260 * x - 0.3516 * x * x + 0.2843 * x * x * x - 0.1015 * x * x * x * x);
        double yc = 0.0, dy_dx = 0.0;
        if (p > 0.0 && m > 0.0) {
            if (x <= p) {
                yc = (m / (p * p)) * (2.0 * p * x - x * x);
                dy_dx = (2.0 * m / (p * p)) * (p - x);
            } else {
                yc = (m / ((1.0 - p) * (1.0 - p))) * ((1.0 - 2.0 * p) + 2.0 * p * x - x * x);
                dy_dx = (2.0 * m / ((1.0 - p) * (1.0 - p))) * (p - x);
            }
        }
        double th = atan(dy_dx);
        nodes[n_nodes].x = x + yt * sin(th);
        nodes[n_nodes].y = yc - yt * cos(th);
        n_nodes++;
    }

    /* Верхній контур від LE (x=0.0) до TE (x=1.0) */
    for (int i = 1; i <= half_pts; i++) {
        double beta = (M_PI * i) / half_pts;
        double x = 0.5 * (1.0 - cos(beta)); /* 0.0 -> 1.0 */
        double yt = 5.0 * t * (0.2969 * sqrt(x) - 0.1260 * x - 0.3516 * x * x + 0.2843 * x * x * x - 0.1015 * x * x * x * x);
        double yc = 0.0, dy_dx = 0.0;
        if (p > 0.0 && m > 0.0) {
            if (x <= p) {
                yc = (m / (p * p)) * (2.0 * p * x - x * x);
                dy_dx = (2.0 * m / (p * p)) * (p - x);
            } else {
                yc = (m / ((1.0 - p) * (1.0 - p))) * ((1.0 - 2.0 * p) + 2.0 * p * x - x * x);
                dy_dx = (2.0 * m / ((1.0 - p) * (1.0 - p))) * (p - x);
            }
        }
        double th = atan(dy_dx);
        nodes[n_nodes].x = x - yt * sin(th);
        nodes[n_nodes].y = yc + yt * cos(th);
        n_nodes++;
    }

    /* Побудова панелей за списком вузлів */
    for (int i = 0; i < num_panels; i++) {
        panels[i].p1 = nodes[i];
        panels[i].p2 = nodes[i + 1];
        panels[i].cp.x = 0.5 * (panels[i].p1.x + panels[i].p2.x);
        panels[i].cp.y = 0.5 * (panels[i].p1.y + panels[i].p2.y);
        double dx = panels[i].p2.x - panels[i].p1.x;
        double dy = panels[i].p2.y - panels[i].p1.y;
        panels[i].length = sqrt(dx * dx + dy * dy);
        panels[i].theta = atan2(dy, dx);
        panels[i].tangent.x = dx / panels[i].length;
        panels[i].tangent.y = dy / panels[i].length;
        panels[i].normal.x = -panels[i].tangent.y;
        panels[i].normal.y = panels[i].tangent.x;
    }
    return 1;
}

/* Обчислення швидкості, індукованої панеллю j у точці (x, y) */
void panel_velocity(const Panel *p, double x, double y, double *u, double *v) {
    double dx1 = x - p->p1.x;
    double dy1 = y - p->p1.y;
    double ct = cos(p->theta);
    double st = sin(p->theta);

    /* Координати у системі панелі */
    double x_loc = dx1 * ct + dy1 * st;
    double y_loc = -dx1 * st + dy1 * ct;

    if (fabs(y_loc) < 1e-10 && x_loc >= 0.0 && x_loc <= p->length) {
        *u = 0.0;
        *v = 0.0;
        return;
    }

    double r1_sq = x_loc * x_loc + y_loc * y_loc;
    double r2_sq = (x_loc - p->length) * (x_loc - p->length) + y_loc * y_loc;

    double theta1 = atan2(y_loc, x_loc);
    double theta2 = atan2(y_loc, x_loc - p->length);

    double u_loc = -(1.0 / (2.0 * M_PI)) * (theta2 - theta1);
    double v_loc = (1.0 / (4.0 * M_PI)) * log(r2_sq / (r1_sq + 1e-15));

    /* Трансформація у глобальні координати */
    *u = u_loc * ct - v_loc * st;
    *v = u_loc * st + v_loc * ct;
}

/* Розв'язувач лінійної системи A*x = b методом Гаусса з вибором головного елемента */
int solve_gauss(int n, double A[MAX_PANELS][MAX_PANELS], double b[MAX_PANELS], double x[MAX_PANELS]) {
    for (int i = 0; i < n; i++) {
        int max_row = i;
        double max_val = fabs(A[i][i]);
        for (int k = i + 1; k < n; k++) {
            if (fabs(A[k][i]) > max_val) {
                max_val = fabs(A[k][i]);
                max_row = k;
            }
        }
        if (max_val < 1e-12) return 0; /* Вироджена матриця */

        for (int k = i; k < n; k++) {
            double tmp = A[i][k];
            A[i][k] = A[max_row][k];
            A[max_row][k] = tmp;
        }
        double tmp_b = b[i];
        b[i] = b[max_row];
        b[max_row] = tmp_b;

        for (int k = i + 1; k < n; k++) {
            double factor = A[k][i] / A[i][i];
            b[k] -= factor * b[i];
            for (int j = i; j < n; j++) {
                A[k][j] -= factor * A[i][j];
            }
        }
    }

    for (int i = n - 1; i >= 0; i--) {
        double sum = 0.0;
        for (int j = i + 1; j < n; j++) {
            sum += A[i][j] * x[j];
        }
        x[i] = (b[i] - sum) / A[i][i];
    }
    return 1;
}

int main(void) {
    int num_panels = 40;
    Panel panels[MAX_PANELS];
    generate_naca4(2, 4, 12, num_panels, panels); /* NACA 2412 */

    double alpha_deg = 5.0;
    double alpha = alpha_deg * M_PI / 180.0;
    double v_inf_x = cos(alpha);
    double v_inf_y = sin(alpha);

    double A[MAX_PANELS][MAX_PANELS];
    double b[MAX_PANELS];
    double gamma[MAX_PANELS];

    /* Формування матриці впливу */
    for (int i = 0; i < num_panels - 1; i++) {
        b[i] = -(v_inf_x * panels[i].normal.x + v_inf_y * panels[i].normal.y);
        for (int j = 0; j < num_panels; j++) {
            if (i == j) {
                A[i][j] = 0.0;
            } else {
                double u, v;
                panel_velocity(&panels[j], panels[i].cp.x, panels[i].cp.y, &u, &v);
                A[i][j] = u * panels[i].normal.x + v * panels[i].normal.y;
            }
        }
    }

    /* Умова Кутти на останньому рядку: gamma_0 + gamma_{N-1} = 0 */
    for (int j = 0; j < num_panels; j++) {
        A[num_panels - 1][j] = 0.0;
    }
    A[num_panels - 1][0] = 1.0;
    A[num_panels - 1][num_panels - 1] = 1.0;
    b[num_panels - 1] = 0.0;

    solve_gauss(num_panels, A, b, gamma);

    /* Обчислення тангенціальних швидкостей та інтегрування сил */
    double cl = 0.0;
    double cm_c4 = 0.0;

    for (int i = 0; i < num_panels; i++) {
        panels[i].gamma = gamma[i];
        double vt = v_inf_x * panels[i].tangent.x + v_inf_y * panels[i].tangent.y + 0.5 * gamma[i];
        for (int j = 0; j < num_panels; j++) {
            if (i != j) {
                double u, v;
                panel_velocity(&panels[j], panels[i].cp.x, panels[i].cp.y, &u, &v);
                vt += (u * panels[i].tangent.x + v * panels[i].tangent.y) * gamma[j];
            }
        }
        panels[i].cp_val = 1.0 - vt * vt;

        /* Внесок у підіймальну силу (нормаль Y) та поздовжній момент відносно (0.25, 0.0) */
        double cp_ds = -panels[i].cp_val * panels[i].length;
        cl += cp_ds * panels[i].normal.y;
        cm_c4 += cp_ds * (panels[i].normal.y * (panels[i].cp.x - 0.25) - panels[i].normal.x * panels[i].cp.y);
    }

    printf("NACA 2412 | Alpha: %.1f deg | Panels: %d\n", alpha_deg, num_panels);
    printf("Cl: %.4f | Cm(c/4): %.4f\n", cl, cm_c4);
    printf("-----------------------------------------\n");
    printf("Panel   x/c        Cp (Нижня / Верхня)\n");
    for (int i = 0; i < num_panels; i += 4) {
        printf("%3d    %6.3f    %+7.3f\n", i, panels[i].cp.x, panels[i].cp_val);
    }
    return 0;
}
