#include <stdio.h>
#include <math.h>

/* метрів на градус широти для WGS-84 */
static double metres_per_deg_lat(double phi_deg) {
    const double a = 6378137.0, f = 1.0 / 298.257223563;
    const double e2 = f * (2.0 - f);
    double s = sin(phi_deg * M_PI / 180.0);
    double M = a * (1.0 - e2) / pow(1.0 - e2 * s * s, 1.5);
    return M * M_PI / 180.0;
}

int main(void) {
    const double lat[] = { 10.0, 30.0, 50.0, 70.0 };

    for (int i = 0; i < 4; i++) {
        double phi = lat[i];
        int    e   = (int)floor(log2(phi));
        double u32 = ldexp(1.0, e - 23);   /* 2^(e-23) */
        double u64 = ldexp(1.0, e - 52);   /* 2^(e-52) */
        double L   = metres_per_deg_lat(phi);

        printf("%3.0f  e=%d  ulp32=%.7e = %.4f м   ulp64=%.7e = %.2e м\n",
               phi, e, u32, u32 * L, u64, u64 * L);
    }
    return 0;
}
