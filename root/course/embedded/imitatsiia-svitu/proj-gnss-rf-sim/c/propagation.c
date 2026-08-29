#include "propagation.h"

#include <math.h>

#define WGS84_A   6378137.0
#define WGS84_F   (1.0 / 298.257223563)
#define WGS84_E2  (WGS84_F * (2.0 - WGS84_F))

vec3_t geodetic_to_ecef(geodetic_t g)
{
    double sp = sin(g.lat), cp = cos(g.lat);
    double sl = sin(g.lon), cl = cos(g.lon);
    double nrad = WGS84_A / sqrt(1.0 - WGS84_E2 * sp * sp);

    vec3_t p;
    p.x = (nrad + g.height) * cp * cl;
    p.y = (nrad + g.height) * cp * sl;
    p.z = (nrad * (1.0 - WGS84_E2) + g.height) * sp;
    return p;
}

geodetic_t ecef_to_geodetic(vec3_t p)
{
    /* Формула Боурінга: одна ітерація дає похибку менш ніж міліметр. */
    const double b = WGS84_A * (1.0 - WGS84_F);
    const double ep2 = (WGS84_A * WGS84_A - b * b) / (b * b);

    double r = sqrt(p.x * p.x + p.y * p.y);
    geodetic_t g;
    g.lon = atan2(p.y, p.x);

    if (r < 1e-6) {                       /* точка на осі обертання */
        g.lat = (p.z >= 0.0) ? M_PI_2 : -M_PI_2;
        g.height = fabs(p.z) - b;
        return g;
    }

    double theta = atan2(p.z * WGS84_A, r * b);
    double st = sin(theta), ct = cos(theta);
    g.lat = atan2(p.z + ep2 * b * st * st * st,
                  r - WGS84_E2 * WGS84_A * ct * ct * ct);

    double sp = sin(g.lat);
    double nrad = WGS84_A / sqrt(1.0 - WGS84_E2 * sp * sp);
    g.height = r / cos(g.lat) - nrad;
    return g;
}

vec3_t enu_to_ecef_vec(geodetic_t ref, double e, double n, double u)
{
    double sp = sin(ref.lat), cp = cos(ref.lat);
    double sl = sin(ref.lon), cl = cos(ref.lon);

    vec3_t v;
    v.x = -sl * e - sp * cl * n + cp * cl * u;
    v.y =  cl * e - sp * sl * n + cp * sl * u;
    v.z =           cp      * n + sp      * u;
    return v;
}

los_t line_of_sight(vec3_t user_ecef, geodetic_t user_llh, vec3_t sat_ecef)
{
    los_t l;
    double dx = sat_ecef.x - user_ecef.x;
    double dy = sat_ecef.y - user_ecef.y;
    double dz = sat_ecef.z - user_ecef.z;

    l.range = sqrt(dx * dx + dy * dy + dz * dz);
    if (l.range < 1.0) {                  /* виродження: приймач у фазовому центрі КА */
        l.unit = (vec3_t){0.0, 0.0, 0.0};
        l.el = l.az = 0.0;
        return l;
    }
    l.unit = (vec3_t){dx / l.range, dy / l.range, dz / l.range};

    /* Той самий вектор у місцевій системі ENU дає кути видимості. */
    double sp = sin(user_llh.lat), cp = cos(user_llh.lat);
    double sl = sin(user_llh.lon), cl = cos(user_llh.lon);
    double east  = -sl * l.unit.x + cl * l.unit.y;
    double north = -sp * cl * l.unit.x - sp * sl * l.unit.y + cp * l.unit.z;
    double up    =  cp * cl * l.unit.x + cp * sl * l.unit.y + sp * l.unit.z;

    l.el = atan2(up, sqrt(east * east + north * north));
    l.az = atan2(east, north);
    if (l.az < 0.0) l.az += 2.0 * M_PI;
    return l;
}

double doppler_shift_hz(los_t los, vec3_t user_vel, vec3_t sat_vel, double f0)
{
    double dvx = sat_vel.x - user_vel.x;
    double dvy = sat_vel.y - user_vel.y;
    double dvz = sat_vel.z - user_vel.z;

    /* Додатна проєкція означає віддалення, отже зсув униз — звідси мінус. */
    double radial = dvx * los.unit.x + dvy * los.unit.y + dvz * los.unit.z;
    return -f0 * radial / C_LIGHT;
}

double klobuchar_delay_s(const double a[4], const double b[4],
                         geodetic_t user, los_t los, double tow)
{
    if (los.el <= 0.0) return 0.0;

    /* Модель працює в напівобертах: кут у радіанах ділимо на π. */
    const double el  = los.el / M_PI;
    const double lat = user.lat / M_PI;
    const double lon = user.lon / M_PI;

    double psi = 0.0137 / (el + 0.11) - 0.022;          /* земний центральний кут */
    double phi_i = lat + psi * cos(los.az);
    if (phi_i >  0.416) phi_i =  0.416;
    if (phi_i < -0.416) phi_i = -0.416;

    double lam_i = lon + psi * sin(los.az) / cos(phi_i * M_PI);
    double phi_m = phi_i + 0.064 * cos((lam_i - 1.617) * M_PI);   /* геомагнітна широта */

    double t = fmod(43200.0 * lam_i + tow, 86400.0);
    if (t < 0.0) t += 86400.0;

    double amp = a[0] + phi_m * (a[1] + phi_m * (a[2] + phi_m * a[3]));
    double per = b[0] + phi_m * (b[1] + phi_m * (b[2] + phi_m * b[3]));
    if (amp < 0.0)      amp = 0.0;
    if (per < 72000.0)  per = 72000.0;

    double x = 2.0 * M_PI * (t - 50400.0) / per;
    double f = 1.0 + 16.0 * pow(0.53 - el, 3.0);          /* нахилений хід променя */

    double zenith = (fabs(x) < 1.57)
                  ? 5e-9 + amp * (1.0 + x * x * (-0.5 + x * x / 24.0))
                  : 5e-9;
    return f * zenith;
}

double saastamoinen_delay_s(geodetic_t user, double el, double humidity)
{
    if (el < 3.0 * M_PI / 180.0) el = 3.0 * M_PI / 180.0;   /* модель нижче не працює */

    double h = user.height;
    if (h < 0.0)      h = 0.0;
    if (h > 12000.0)  h = 12000.0;

    /* Стандартна атмосфера як опорна точка. */
    double pres = 1013.25 * pow(1.0 - 2.2557e-5 * h, 5.2568);       /* гПа */
    double temp = 15.0 - 6.5e-3 * h + 273.16;                        /* К */
    double ewat = 6.108 * humidity * exp((17.15 * temp - 4684.0) / (temp - 38.45));

    double z = M_PI_2 - el;
    double dry = 0.0022768 * pres
               / (1.0 - 0.00266 * cos(2.0 * user.lat) - 0.00028 * h * 1e-3) / cos(z);
    double wet = 0.002277 * (1255.0 / temp + 0.05) * ewat / cos(z);

    return (dry + wet) / C_LIGHT;      /* метри → секунди */
}

double free_space_loss_db(double range_m, double f_hz)
{
    if (range_m < 1.0) range_m = 1.0;
    return 20.0 * log10(4.0 * M_PI * range_m * f_hz / C_LIGHT);
}

double rx_antenna_gain_db(double el)
{
    /* Патч-антена приймача: близько 3 дБі в зеніті, різкий спад до горизонту. */
    if (el <= 0.0) return -20.0;
    double g = 3.0 + 12.0 * log10(sin(el) + 1e-3);
    return (g < -20.0) ? -20.0 : g;
}

multipath_t multipath_from_geometry(double antenna_height_m, double el, double reflectivity)
{
    multipath_t mp;
    double dl = 2.0 * antenna_height_m * sin(el > 0.0 ? el : 0.0);
    mp.delay_s = dl / C_LIGHT;
    mp.gamma   = reflectivity;
    /* Дзеркальне відбиття обертає поляризацію RHCP→LHCP; антена приймача таку
     * хвилю бере з великою втратою — але не з нульовою, і саме залишок псує
     * автокореляційний пік. */
    mp.xpol_db = -10.0;
    return mp;
}
