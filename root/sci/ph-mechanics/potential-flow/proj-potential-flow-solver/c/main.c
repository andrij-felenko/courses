#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x1, y1;
    double x2, y2;
    double xc, yc;
    double len;
    double beta;
    double nx, ny;
    double tx, ty;
    double q;
    double vt;
    double cp;
} Panel;

void generate_cylinder_panels(Panel* panels, int n, double radius) {
    for (int i = 0; i < n; i++) {
        double theta1 = 2.0 * M_PI * i / n;
        double theta2 = 2.0 * M_PI * (i + 1) / n;

        panels[i].x1 = radius * cos(theta1);
        panels[i].y1 = radius * sin(theta1);
        panels[i].x2 = radius * cos(theta2);
        panels[i].y2 = radius * sin(theta2);

        panels[i].xc = 0.5 * (panels[i].x1 + panels[i].x2);
        panels[i].yc = 0.5 * (panels[i].y1 + panels[i].y2);

        double dx = panels[i].x2 - panels[i].x1;
        double dy = panels[i].y2 - panels[i].y1;
        panels[i].len = hypot(dx, dy);
        panels[i].beta = atan2(dy, dx);

        panels[i].tx = dx / panels[i].len;
        panels[i].ty = dy / panels[i].len;
        panels[i].nx = -panels[i].ty;
        panels[i].ny =  panels[i].tx;
    }
}

void solve_linear_system(double** A, double* b, double* x, int n) {
    for (int i = 0; i < n; i++) {
        int max_row = i;
        for (int k = i + 1; k < n; k++) {
            if (fabs(A[k][i]) > fabs(A[max_row][i])) {
                max_row = k;
            }
        }
        for (int k = i; k < n; k++) {
            double tmp = A[i][k];
            A[i][k] = A[max_row][k];
            A[max_row][k] = tmp;
        }
        double tmp_b = b[i];
        b[i] = b[max_row];
        b[max_row] = tmp_b;

        for (int k = i + 1; k < n; k++) {
            double c = -A[k][i] / A[i][i];
            for (int j = i; j < n; j++) {
                if (i == j) {
                    A[k][j] = 0;
                } else {
                    A[k][j] += c * A[i][j];
                }
            }
            b[k] += c * b[i];
        }
    }

    for (int i = n - 1; i >= 0; i--) {
        x[i] = b[i] / A[i][i];
        for (int k = i - 1; k >= 0; k--) {
            b[k] -= A[k][i] * x[i];
        }
    }
}

int main(void) {
    int n = 36;
    double radius = 1.0;
    double u_inf = 10.0;

    Panel* panels = (Panel*)malloc(n * sizeof(Panel));
    if (!panels) return 1;

    generate_cylinder_panels(panels, n, radius);

    double** A = (double**)malloc(n * sizeof(double*));
    double* b = (double*)malloc(n * sizeof(double));
    double* q = (double*)malloc(n * sizeof(double));
    for (int i = 0; i < n; i++) {
        A[i] = (double*)malloc(n * sizeof(double));
    }

    for (int i = 0; i < n; i++) {
        b[i] = -u_inf * panels[i].nx;
        for (int j = 0; j < n; j++) {
            if (i == j) {
                A[i][j] = 0.5;
            } else {
                double dx = panels[i].xc - panels[j].xc;
                double dy = panels[i].yc - panels[j].yc;
                double r2 = dx * dx + dy * dy;
                double vn = (dx * panels[i].nx + dy * panels[i].ny) / (2.0 * M_PI * r2);
                A[i][j] = vn * panels[j].len;
            }
        }
    }

    solve_linear_system(A, b, q, n);

    for (int i = 0; i < n; i++) {
        panels[i].q = q[i];
        double vt = u_inf * panels[i].tx;
        for (int j = 0; j < n; j++) {
            if (i != j) {
                double dx = panels[i].xc - panels[j].xc;
                double dy = panels[i].yc - panels[j].yc;
                double r2 = dx * dx + dy * dy;
                double vt_ind = (dx * panels[i].tx + dy * panels[i].ty) / (2.0 * M_PI * r2);
                vt += q[j] * vt_ind * panels[j].len;
            }
        }
        panels[i].vt = vt;
        panels[i].cp = 1.0 - (vt / u_inf) * (vt / u_inf);
    }

    printf("Результати розрахунку потенціального обтікання циліндра:\n");
    printf("Панель |     Xc     |     Yc     |    Cp (чисельний) | Cp (аналітичний)\n");
    printf("-----------------------------------------------------------------------\n");
    for (int i = 0; i < n; i += 4) {
        double theta = atan2(panels[i].yc, panels[i].xc);
        double cp_exact = 1.0 - 4.0 * sin(theta) * sin(theta);
        printf("%6d | %10.4f | %10.4f | %17.4f | %17.4f\n",
               i, panels[i].xc, panels[i].yc, panels[i].cp, cp_exact);
    }

    for (int i = 0; i < n; i++) free(A[i]);
    free(A);
    free(b);
    free(q);
    free(panels);

    return 0;
}
