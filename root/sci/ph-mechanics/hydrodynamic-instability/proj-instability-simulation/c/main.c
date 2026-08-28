#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    int nx, ny;
    double lx, ly, dx, dy;
    double nu, dt;
    double *w;   /* Вихровість (Flattened 1D array) */
    double *psi; /* Функція струменю */
    double *u;   /* Подовжня швидкість */
    double *v;   /* Поперечна швидкість */
} kh_solver_c_t;

kh_solver_c_t* kh_create(int nx, int ny, double lx, double ly, double nu, double dt) {
    kh_solver_c_t *s = (kh_solver_c_t*)malloc(sizeof(kh_solver_c_t));
    if (!s) return NULL;
    s->nx = nx; s->ny = ny;
    s->lx = lx; s->ly = ly;
    s->dx = lx / nx; s->dy = ly / ny;
    s->nu = nu; s->dt = dt;
    
    size_t sz = (size_t)nx * ny * sizeof(double);
    s->w   = (double*)calloc((size_t)nx * ny, sizeof(double));
    s->psi = (double*)calloc((size_t)nx * ny, sizeof(double));
    s->u   = (double*)calloc((size_t)nx * ny, sizeof(double));
    s->v   = (double*)calloc((size_t)nx * ny, sizeof(double));
    
    if (!s->w || !s->psi || !s->u || !s->v) {
        free(s->w); free(s->psi); free(s->u); free(s->v);
        free(s);
        return NULL;
    }
    return s;
}

void kh_free(kh_solver_c_t *s) {
    if (!s) return;
    free(s->w);
    free(s->psi);
    free(s->u);
    free(s->v);
    free(s);
}

void kh_init_shear(kh_solver_c_t *s, double u0, double delta, double eps) {
    for (int j = 0; j < s->ny; j++) {
        double y = -s->ly / 2.0 + j * s->dy;
        for (int i = 0; i < s->nx; i++) {
            double x = i * s->dx;
            int idx = j * s->nx + i;
            
            s->u[idx] = u0 * tanh(y / delta);
            s->v[idx] = eps * u0 * sin(2.0 * M_PI * x / s->lx) * exp(-(y / delta) * (y / delta));
        }
    }
    
    /* Обчислення початкової вихровості w = dv/dx - du/dy */
    for (int j = 1; j < s->ny - 1; j++) {
        for (int i = 1; i < s->nx - 1; i++) {
            int idx = j * s->nx + i;
            double du_dy = (s->u[(j+1)*s->nx + i] - s->u[(j-1)*s->nx + i]) / (2.0 * s->dy);
            double dv_dx = (s->v[j*s->nx + (i+1)] - s->v[j*s->nx + (i-1)]) / (2.0 * s->dx);
            s->w[idx] = dv_dx - du_dy;
        }
    }
}

void kh_step(kh_solver_c_t *s) {
    int nx = s->nx, ny = s->ny;
    double dx2 = s->dx * s->dx, dy2 = s->dy * s->dy;
    double factor = 0.5 * (dx2 * dy2) / (dx2 + dy2);
    
    /* Ітерації Якобі для ∇²ψ = -w */
    for (int iter = 0; iter < 100; iter++) {
        for (int j = 1; j < ny - 1; j++) {
            for (int i = 1; i < nx - 1; i++) {
                int idx = j * nx + i;
                s->psi[idx] = factor * (
                    (s->psi[j*nx + (i+1)] + s->psi[j*nx + (i-1)]) / dx2 +
                    (s->psi[(j+1)*nx + i] + s->psi[(j-1)*nx + i]) / dy2 +
                    s->w[idx]
                );
            }
        }
    }
    
    /* Оновлення швидкостей u = dψ/dy, v = -dψ/dx */
    for (int j = 1; j < ny - 1; j++) {
        for (int i = 1; i < nx - 1; i++) {
            int idx = j * nx + i;
            s->u[idx] =  (s->psi[(j+1)*nx + i] - s->psi[(j-1)*nx + i]) / (2.0 * s->dy);
            s->v[idx] = -(s->psi[j*nx + (i+1)] - s->psi[j*nx + (i-1)]) / (2.0 * s->dx);
        }
    }
    
    /* Крок переносу вихровості */
    for (int j = 1; j < ny - 1; j++) {
        for (int i = 1; i < nx - 1; i++) {
            int idx = j * nx + i;
            double dw_dx = (s->w[j*nx + (i+1)] - s->w[j*nx + (i-1)]) / (2.0 * s->dx);
            double dw_dy = (s->w[(j+1)*nx + i] - s->w[(j-1)*nx + i]) / (2.0 * s->dy);
            double d2w_dx2 = (s->w[j*nx + (i+1)] - 2.0*s->w[idx] + s->w[j*nx + (i-1)]) / dx2;
            double d2w_dy2 = (s->w[(j+1)*nx + i] - 2.0*s->w[idx] + s->w[(j-1)*nx + i]) / dy2;
            
            double conv = s->u[idx] * dw_dx + s->v[idx] * dw_dy;
            double diff = s->nu * (d2w_dx2 + d2w_dy2);
            
            s->w[idx] += s->dt * (-conv + diff);
        }
    }
}

int main(void) {
    kh_solver_c_t *s = kh_create(64, 64, 1.0, 1.0, 1e-4, 1e-3);
    if (!s) return 1;
    kh_init_shear(s, 1.0, 0.05, 0.05);
    for (int step = 0; step < 50; step++) {
        kh_step(s);
    }
    printf("C solver finished successfully.\n");
    kh_free(s);
    return 0;
}
