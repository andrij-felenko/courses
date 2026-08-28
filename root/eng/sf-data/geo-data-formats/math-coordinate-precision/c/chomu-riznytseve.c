#include <stdio.h>
#include <math.h>

#define N     10000                /* параметр квантування */
#define K     5
#define L_LAT 111229.064           /* м на градус широти  @50° */
#define L_LON  71695.754           /* м на градус довготи @50° */

int main(void) {
    const double lon[K] = {30.523400, 30.524150, 30.525900, 30.527310, 30.528000};
    const double lat[K] = {50.450100, 50.450620, 50.451080, 50.450940, 50.452250};
    const double x0 = 30.2, x1 = 30.8, y0 = 50.2, y1 = 50.6;   /* обмежувальний прямокутник */

    double kx = (N - 1) / (x1 - x0), ky = (N - 1) / (y1 - y0);
    double qx = 1.0 / kx,            qy = 1.0 / ky;
    printf("q_x = %.10f° = %.4f м   q_y = %.10f° = %.4f м\n",
           qx, qx * L_LON, qy, qy * L_LAT);

    long ix[K], iy[K];
    for (int k = 0; k < K; k++) {                 /* 1. на цілочислову сітку */
        ix[k] = lround((lon[k] - x0) * kx);
        iy[k] = lround((lat[k] - y0) * ky);
    }

    long dx[K], dy[K];                            /* 2. різниці — цілі */
    dx[0] = ix[0]; dy[0] = iy[0];
    for (int k = 1; k < K; k++) { dx[k] = ix[k] - ix[k-1]; dy[k] = iy[k] - iy[k-1]; }

    long ax = 0, ay = 0;                          /* 3. відновлення — часткові суми */
    double mx = 0, my = 0;
    for (int k = 0; k < K; k++) {
        ax += dx[k]; ay += dy[k];
        double ex = (ax * qx + x0 - lon[k]) * L_LON;
        double ey = (ay * qy + y0 - lat[k]) * L_LAT;
        if (fabs(ex) > mx) mx = fabs(ex);
        if (fabs(ey) > my) my = fabs(ey);
        printf("  k=%d  Δ=(%+3ld,%+3ld)  індекс=(%ld,%ld)  похибка=(%+.3f, %+.3f) м\n",
               k, dx[k], dy[k], ax, ay, ex, ey);
    }
    printf("макс |Δx| = %.3f м (межа %.3f)   макс |Δy| = %.3f м (межа %.3f)\n",
           mx, qx * L_LON / 2, my, qy * L_LAT / 2);
    return 0;
}
