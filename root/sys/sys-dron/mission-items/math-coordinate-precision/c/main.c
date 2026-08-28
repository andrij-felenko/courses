#include <stdio.h>
#include <math.h>

static const double PI = 3.14159265358979323846;
static const double A  = 6378137.0;                /* велика піввісь WGS-84 */
static const double FL = 1.0 / 298.257223563;      /* стиснення             */

static double mpd_lat(double phi_deg) {            /* метрів на градус широти */
    double e2 = FL * (2.0 - FL);
    double s  = sin(phi_deg * PI / 180.0);
    return A * (1.0 - e2) / pow(1.0 - e2 * s * s, 1.5) * PI / 180.0;
}

static double mpd_lon(double phi_deg) {            /* метрів на градус довготи */
    double e2 = FL * (2.0 - FL);
    double s  = sin(phi_deg * PI / 180.0);
    return A / sqrt(1.0 - e2 * s * s) * cos(phi_deg * PI / 180.0) * PI / 180.0;
}

static double ulp32(double x) {                    /* крок сітки float32 біля x */
    int e = (int)floor(log2(fabs(x)));
    return ldexp(1.0, e - 23);                     /* 2^(e−23) */
}

int main(void) {
    struct { const char *name; double lat, lon; } p[] = {
        { "Цюрих",    47.3977419,   8.5455940 },
        { "Найробі",  -1.2921000,  36.8219000 },
        { "Сідней",  -33.8688000, 151.2093000 },
    };

    for (int i = 0; i < 3; i++) {
        double ml = mpd_lat(p[i].lat);             /* метрів на градус, обидві осі */
        double mo = mpd_lon(p[i].lat);
        printf("%s\n", p[i].name);
        printf("  широта  %11.7f°  ulp32 = %.3e°  -> %7.2f см     int32: %5.2f см\n",
               p[i].lat, ulp32(p[i].lat), ulp32(p[i].lat) * ml * 100, 1e-7 * ml * 100);
        printf("  довгота %11.7f°  ulp32 = %.3e°  -> %7.2f см     int32: %5.2f см\n",
               p[i].lon, ulp32(p[i].lon), ulp32(p[i].lon) * mo * 100, 1e-7 * mo * 100);
    }
    return 0;
}
