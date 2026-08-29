/* propagation.h — геометрія «супутник ↔ приймач», атмосферні затримки,
 * доплер, бюджет потужності та відбитий промінь. */
#ifndef PROPAGATION_H
#define PROPAGATION_H

#include "ephemeris.h"

typedef struct { double lat, lon, height; } geodetic_t;   /* рад, рад, м */

vec3_t     geodetic_to_ecef(geodetic_t g);
geodetic_t ecef_to_geodetic(vec3_t p);
vec3_t     enu_to_ecef_vec(geodetic_t ref, double e, double n, double u);

typedef struct {
    vec3_t unit;      /* одиничний вектор прямої видимості від приймача до КА */
    double range;     /* геометрична дистанція, м */
    double el, az;    /* кут підвищення та азимут, рад */
} los_t;

los_t  line_of_sight(vec3_t user_ecef, geodetic_t user_llh, vec3_t sat_ecef);
double doppler_shift_hz(los_t los, vec3_t user_vel, vec3_t sat_vel, double f0);

double klobuchar_delay_s(const double a[4], const double b[4],
                         geodetic_t user, los_t los, double tow);
double saastamoinen_delay_s(geodetic_t user, double el, double humidity);

double free_space_loss_db(double range_m, double f_hz);
double rx_antenna_gain_db(double el);

/* Відбитий промінь: додатковий хід ΔL = 2·h·sin(θ) і коефіцієнт відбиття. */
typedef struct {
    double delay_s;    /* запізнення відносно прямого променя */
    double gamma;      /* амплітудний коефіцієнт відбиття */
    double xpol_db;    /* втрати на прийомі оберненої поляризації (RHCP→LHCP) */
} multipath_t;

multipath_t multipath_from_geometry(double antenna_height_m, double el, double reflectivity);

#endif /* PROPAGATION_H */
