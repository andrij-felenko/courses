/* ephemeris.h — ефемериди GPS з навігаційного файлу RINEX 3
 * і положення/швидкість супутника в ECEF за алгоритмом IS-GPS-200. */
#ifndef EPHEMERIS_H
#define EPHEMERIS_H

#include <stdbool.h>
#include <stddef.h>

#define MAX_EPHEMERIS   128

#define GPS_MU          3.986005e14      /* гравітаційний параметр WGS-84, м³/с² */
#define GPS_OMEGA_E     7.2921151467e-5  /* кутова швидкість обертання Землі, рад/с */
#define GPS_F_REL       (-4.442807633e-10)
#define GPS_L1_HZ       1575420000.0
#define C_LIGHT         299792458.0

typedef struct { double x, y, z; } vec3_t;

/* Час у шкалі GPS: повний номер тижня (лічильник НЕ обрізаний до 10 біт)
 * і секунди від початку тижня. */
typedef struct { int week; double tow; } gps_time_t;

gps_time_t gps_time_add(gps_time_t t, double dt);
double     gps_time_diff(gps_time_t a, gps_time_t b);
int        gps_week10(int week_full);   /* те, що реально їде в навігаційний кадр */

typedef struct {
    int    prn, health, iode, iodc;
    int    week;              /* повний тиждень з рядка BROADCAST ORBIT 5 */
    double toc, toe;          /* секунди тижня */
    double af0, af1, af2;     /* поліном годинника, с · с/с · с/с² */
    double tgd, accuracy;
    /* кеплерові елементи; кути вже переведено в радіани */
    double sqrt_a, ecc, m0, delta_n, omega0, i0, omega_arg, omega_dot, idot;
    double cuc, cus, crc, crs, cic, cis;
} ephemeris_t;

typedef struct {
    double alpha[4], beta[4];   /* коефіцієнти Клобучара з шапки файлу */
    int    leap_seconds;        /* поточна різниця UTC↔GPS */
    bool   have_iono, have_leap;
} nav_header_t;

typedef struct {
    vec3_t pos, vel;            /* ECEF, м та м/с */
    double clock_bias;          /* похибка бортового стандарту частоти, с */
    double clock_drift;         /* її похідна, с/с */
} sat_state_t;

/* Повертає кількість прочитаних наборів або -1 (причина — у stderr). */
int rinex_load(const char *path, ephemeris_t *out, size_t max, nav_header_t *hdr);

/* Найсвіжіший придатний набір для PRN на момент t; NULL, якщо такого немає. */
const ephemeris_t *eph_select(const ephemeris_t *set, size_t n, int prn, gps_time_t t);

bool eph_sat_state(const ephemeris_t *e, gps_time_t t, sat_state_t *st);

#endif /* EPHEMERIS_H */
