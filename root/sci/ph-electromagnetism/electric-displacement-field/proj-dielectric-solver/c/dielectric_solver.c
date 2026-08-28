/* dielectric_solver.c — Чисельний 2D розв'язувач полів D, E, P методом FDM/SOR на C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define NX 100
#define NY 100
#define EPS0 8.854187817e-12

typedef struct {
    int nx;
    int ny;
    double h;
    double *phi;
    double *eps_r;
    double *rho_free;
    bool *is_boundary;
    double *Ex;
    double *Ey;
    double *Dx;
    double *Dy;
    double *Px;
    double *Py;
} Solver2D;

Solver2D* solver_create(int nx, int ny, double domain_size) {
    Solver2D *s = (Solver2D*)calloc(1, sizeof(Solver2D));
    if (!s) return NULL;

    s->nx = nx;
    s->ny = ny;
    s->h = domain_size / (nx - 1);
    size_t sz = (size_t)nx * ny;

    s->phi = (double*)calloc(sz, sizeof(double));
    s->eps_r = (double*)calloc(sz, sizeof(double));
    s->rho_free = (double*)calloc(sz, sizeof(double));
    s->is_boundary = (bool*)calloc(sz, sizeof(bool));
    s->Ex = (double*)calloc(sz, sizeof(double));
    s->Ey = (double*)calloc(sz, sizeof(double));
    s->Dx = (double*)calloc(sz, sizeof(double));
    s->Dy = (double*)calloc(sz, sizeof(double));
    s->Px = (double*)calloc(sz, sizeof(double));
    s->Py = (double*)calloc(sz, sizeof(double));

    /* Ініціалізація за замовчуванням: вакуум (eps_r = 1.0) */
    for (size_t i = 0; i < sz; i++) {
        s->eps_r[i] = 1.0;
    }
    return s;
}

void solver_destroy(Solver2D *s) {
    if (!s) return;
    free(s->phi);
    free(s->eps_r);
    free(s->rho_free);
    free(s->is_boundary);
    free(s->Ex);
    free(s->Ey);
    free(s->Dx);
    free(s->Dy);
    free(s->Px);
    free(s->Py);
    free(s);
}

static inline int idx(Solver2D *s, int i, int j) {
    return i * s->ny + j;
}

void solver_setup_microstrip(Solver2D *s, double eps_substrate) {
    int nx = s->nx;
    int ny = s->ny;

    /* Нижня половина (j < ny/2): підкладка з проникністю eps_substrate */
    for (int i = 0; i < nx; i++) {
        for (int j = 0; j < ny / 2; j++) {
            s->eps_r[idx(s, i, j)] = eps_substrate;
        }
    }

    /* Заземлена нижня границя (y = 0) */
    for (int i = 0; i < nx; i++) {
        int id = idx(s, i, 0);
        s->phi[id] = 0.0;
        s->is_boundary[id] = true;
    }

    /* Верхня границя (y = NY-1): 0 В */
    for (int i = 0; i < nx; i++) {
        int id = idx(s, i, ny - 1);
        s->phi[id] = 0.0;
        s->is_boundary[id] = true;
    }

    /* Сигнальна смужка на межі діелектриків (j = ny/2, від i = nx/4 до 3*nx/4): +100 В */
    int j_strip = ny / 2;
    for (int i = nx / 4; i <= 3 * nx / 4; i++) {
        int id = idx(s, i, j_strip);
        s->phi[id] = 100.0;
        s->is_boundary[id] = true;
    }
}

double solver_step_sor(Solver2D *s, double omega) {
    double max_diff = 0.0;
    int nx = s->nx;
    int ny = s->ny;
    double h2 = s->h * s->h;

    for (int i = 1; i < nx - 1; i++) {
        for (int j = 1; j < ny - 1; j++) {
            int id = idx(s, i, j);
            if (s->is_boundary[id]) continue;

            double eps_e = 0.5 * (s->eps_r[id] + s->eps_r[idx(s, i + 1, j)]);
            double eps_w = 0.5 * (s->eps_r[id] + s->eps_r[idx(s, i - 1, j)]);
            double eps_n = 0.5 * (s->eps_r[id] + s->eps_r[idx(s, i, j + 1)]);
            double eps_s = 0.5 * (s->eps_r[id] + s->eps_r[idx(s, i, j - 1)]);

            double num = eps_e * s->phi[idx(s, i + 1, j)] +
                         eps_w * s->phi[idx(s, i - 1, j)] +
                         eps_n * s->phi[idx(s, i, j + 1)] +
                         eps_s * s->phi[idx(s, i, j - 1)] +
                         (h2 * s->rho_free[id] / EPS0);
            double den = eps_e + eps_w + eps_n + eps_s;
            double phi_target = num / den;

            double diff = fabs(phi_target - s->phi[id]);
            if (diff > max_diff) max_diff = diff;

            s->phi[id] += omega * (phi_target - s->phi[id]);
        }
    }
    return max_diff;
}

void solver_compute_vector_fields(Solver2D *s) {
    int nx = s->nx;
    int ny = s->ny;
    double h2 = 2.0 * s->h;

    for (int i = 1; i < nx - 1; i++) {
        for (int j = 1; j < ny - 1; j++) {
            int id = idx(s, i, j);
            double ex = -(s->phi[idx(s, i + 1, j)] - s->phi[idx(s, i - 1, j)]) / h2;
            double ey = -(s->phi[idx(s, i, j + 1)] - s->phi[idx(s, i, j - 1)]) / h2;

            s->Ex[id] = ex;
            s->Ey[id] = ey;

            double eps = s->eps_r[id];
            s->Dx[id] = EPS0 * eps * ex;
            s->Dy[id] = EPS0 * eps * ey;

            s->Px[id] = s->Dx[id] - EPS0 * ex;
            s->Py[id] = s->Dy[id] - EPS0 * ey;
        }
    }
}

int main(void) {
    Solver2D *s = solver_create(NX, NY, 0.1);
    if (!s) return 1;

    solver_setup_microstrip(s, 4.4); /* FR-4 склотекстоліт eps_r = 4.4 */

    double omega = 1.90;
    int iter;
    for (iter = 0; iter < 5000; iter++) {
        double diff = solver_step_sor(s, omega);
        if (diff < 1e-6) break;
    }

    solver_compute_vector_fields(s);

    int test_i = NX / 2;
    int test_j_sub = NY / 4;     /* Точка в підкладці */
    int test_j_air = 3 * NY / 4; /* Точка в повітрі */

    int id_sub = idx(s, test_i, test_j_sub);
    int id_air = idx(s, test_i, test_j_air);

    printf("Розв'язок збігся за %d ітерацій.\n", iter);
    printf("Точка підкладки FR-4 (eps=4.4): Ey = %.2f В/м, Dy = %.3e Кл/м²\n",
           s->Ey[id_sub], s->Dy[id_sub]);
    printf("Точка повітря (eps=1.0):        Ey = %.2f В/м, Dy = %.3e Кл/м²\n",
           s->Ey[id_air], s->Dy[id_air]);

    solver_destroy(s);
    return 0;
}
