#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Модуль обчислення бароклінного моменту мовою C99 */
void compute_baroclinic_c(
    const double* p, const double* rho, const double* T,
    double* tau_z, double* du_g_dz, double* dv_g_dz,
    int Nx, int Ny, int Nz,
    double dx, double dy, double f_coriolis, double g)
{
    for (int k = 0; k < Nz; ++k) {
        for (int j = 1; j < Ny - 1; ++j) {
            for (int i = 1; i < Nx - 1; ++i) {
                int idx = k * (Ny * Nx) + j * Nx + i;
                int idx_px = idx + 1;
                int idx_mx = idx - 1;
                int idx_py = idx + Nx;
                int idx_my = idx - Nx;

                double dp_dx = (p[idx_px] - p[idx_mx]) / (2.0 * dx);
                double dp_dy = (p[idx_py] - p[idx_my]) / (2.0 * dy);

                double drho_dx = (rho[idx_px] - rho[idx_mx]) / (2.0 * dx);
                double drho_dy = (rho[idx_py] - rho[idx_my]) / (2.0 * dy);

                double dT_dx = (T[idx_px] - T[idx_mx]) / (2.0 * dx);
                double dT_dy = (T[idx_py] - T[idx_my]) / (2.0 * dy);

                double r = rho[idx];
                tau_z[idx] = (drho_dx * dp_dy - drho_dy * dp_dx) / (r * r);

                double Temp = T[idx];
                du_g_dz[idx] = - (g / (f_coriolis * Temp)) * dT_dy;
                dv_g_dz[idx] =   (g / (f_coriolis * Temp)) * dT_dx;
            }
        }
    }
}
