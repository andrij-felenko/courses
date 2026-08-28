#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PVU_SCALE 1e6

typedef struct {
    int nx, ny, nz;
    double dx, dy, dz;
    double f0; /* Параметр Коріоліса на опорній широті */
} grid3d_t;

typedef struct {
    double *u;
    double *v;
    double *w;
    double *theta;
    double *rho;
} flow_fields_t;

/* Пласке індексування 3D масиву в порядку C (Row-Major: i -> j -> k) */
static inline size_t idx3d(int i, int j, int k, int ny, int nz) {
    return ((size_t)i * (size_t)ny + (size_t)j) * (size_t)nz + (size_t)k;
}

int compute_ertel_pv_c(const grid3d_t *g, const flow_fields_t *f, double *pv_out) {
    if (!g || !f || !pv_out) return -1;
    if (!f->u || !f->v || !f->w || !f->theta || !f->rho) return -2;

    int nx = g->nx, ny = g->ny, nz = g->nz;
    double dx2 = 2.0 * g->dx;
    double dy2 = 2.0 * g->dy;
    double dz2 = 2.0 * g->dz;

    /* Послідовний обхід з внутрішнім найшвидшим циклом за k */
    for (int i = 1; i < nx - 1; ++i) {
        for (int j = 1; j < ny - 1; ++j) {
            for (int k = 1; k < nz - 1; ++k) {
                size_t c = idx3d(i, j, k, ny, nz);

                /* Сусідні вузли за x */
                size_t ip = idx3d(i + 1, j, k, ny, nz);
                size_t im = idx3d(i - 1, j, k, ny, nz);

                /* Сусідні вузли за y */
                size_t jp = idx3d(i, j + 1, k, ny, nz);
                size_t jm = idx3d(i, j - 1, k, ny, nz);

                /* Сусідні вузли за z */
                size_t kp = idx3d(i, j, k + 1, ny, nz);
                size_t km = idx3d(i, j, k - 1, ny, nz);

                /* Відносна вихореність (ротор швидкості u) */
                double dw_dy = (f->w[jp] - f->w[jm]) / dy2;
                double dv_dz = (f->v[kp] - f->v[km]) / dz2;
                double rel_wx = dw_dy - dv_dz;

                double du_dz = (f->u[kp] - f->u[km]) / dz2;
                double dw_dx = (f->w[ip] - f->w[im]) / dx2;
                double rel_wy = du_dz - dw_dx;

                double dv_dx = (f->v[ip] - f->v[im]) / dx2;
                double du_dy = (f->u[jp] - f->u[jm]) / dy2;
                double rel_wz = dv_dx - du_dy;

                /* Градієнт потенціальної температури */
                double dth_dx = (f->theta[ip] - f->theta[im]) / dx2;
                double dth_dy = (f->theta[jp] - f->theta[jm]) / dy2;
                double dth_dz = (f->theta[kp] - f->theta[km]) / dz2;

                /* Абсолютна вихореність (з додаванням f0 до вертикальної компоненти) */
                double abs_wx = rel_wx;
                double abs_wy = rel_wy;
                double abs_wz = rel_wz + g->f0;

                /* Скалярний добуток та нормування на густину */
                double dot = abs_wx * dth_dx + abs_wy * dth_dy + abs_wz * dth_dz;
                double r = f->rho[c];

                /* Захист від ділення на нуль при нефізичній густині */
                pv_out[c] = (r > 1e-6) ? (dot / r) * PVU_SCALE : 0.0;
            }
        }
    }
    return 0;
}
