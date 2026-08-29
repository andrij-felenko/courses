#include "ephemeris.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SEC_PER_WEEK 604800.0

gps_time_t gps_time_add(gps_time_t t, double dt)
{
    t.tow += dt;
    while (t.tow >= SEC_PER_WEEK) { t.tow -= SEC_PER_WEEK; t.week++; }
    while (t.tow < 0.0)           { t.tow += SEC_PER_WEEK; t.week--; }
    return t;
}

double gps_time_diff(gps_time_t a, gps_time_t b)
{
    return (double)(a.week - b.week) * SEC_PER_WEEK + (a.tow - b.tow);
}

int gps_week10(int week_full)
{
    /* У кадр іде лише молодші 10 біт — саме це переповнення раз на 1024 тижні
     * і перевіряє стенд (розділ «крайові часові події»). */
    return week_full & 0x3FF;
}

/* ---- читання RINEX ------------------------------------------------------ */

/* Поле фіксованої ширини у форматі Фортрана: показник степеня буває 'D'. */
static double rnx_num(const char *line, int col, int width)
{
    char buf[32];
    size_t len = strlen(line);
    if ((size_t)col >= len) return 0.0;
    size_t n = len - (size_t)col;
    if (n > (size_t)width)   n = (size_t)width;
    if (n >= sizeof buf)     n = sizeof buf - 1;
    memcpy(buf, line + col, n);
    buf[n] = '\0';
    for (char *p = buf; *p; ++p) if (*p == 'D' || *p == 'd') *p = 'E';
    return strtod(buf, NULL);
}

/* Дні від 1970-01-01 (алгоритм Гінанта, працює й для дат до епохи). */
static long days_from_civil(int y, int m, int d)
{
    y -= (m <= 2);
    long era = (y >= 0 ? y : y - 399) / 400;
    unsigned yoe = (unsigned)(y - era * 400);
    unsigned doy = (unsigned)((153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1);
    unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return era * 146097 + (long)doe - 719468;
}

/* Дата епохи в навігаційному запису GPS подана вже у шкалі GPS — секунд
 * координації віднімати не треба. */
static gps_time_t calendar_to_gps(int y, int mo, int d, int h, int mi, double s)
{
    const long gps_epoch_day = 3657;   /* 1980-01-06 у днях від 1970-01-01 */
    long days = days_from_civil(y, mo, d) - gps_epoch_day;
    gps_time_t t;
    t.week = (int)(days / 7);
    t.tow  = (double)(days % 7) * 86400.0 + h * 3600.0 + mi * 60.0 + s;
    return t;
}

static bool label_is(const char *line, const char *label)
{
    size_t len = strlen(line);
    if (len < 61) return false;
    return strncmp(line + 60, label, strlen(label)) == 0;
}

/* Скільки рядків «BROADCAST ORBIT» має запис системи sys. */
static int record_lines(char sys)
{
    switch (sys) {
    case 'G': case 'E': case 'C': case 'J': case 'I': return 7;
    case 'R': case 'S':                               return 3;
    default:                                          return -1;
    }
}

int rinex_load(const char *path, ephemeris_t *out, size_t max, nav_header_t *hdr)
{
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); return -1; }

    memset(hdr, 0, sizeof *hdr);
    char line[256];
    bool in_header = true;
    double version = 0.0;

    while (in_header && fgets(line, sizeof line, f)) {
        if (label_is(line, "RINEX VERSION / TYPE")) {
            version = rnx_num(line, 0, 9);
        } else if (label_is(line, "IONOSPHERIC CORR")) {
            double v[4] = {0};
            for (int i = 0; i < 4; ++i) v[i] = rnx_num(line, 5 + i * 12, 12);
            if (strncmp(line, "GPSA", 4) == 0) {
                memcpy(hdr->alpha, v, sizeof v);
                hdr->have_iono = true;
            } else if (strncmp(line, "GPSB", 4) == 0) {
                memcpy(hdr->beta, v, sizeof v);
            }
        } else if (label_is(line, "LEAP SECONDS")) {
            hdr->leap_seconds = (int)rnx_num(line, 0, 6);
            hdr->have_leap = true;
        } else if (label_is(line, "END OF HEADER")) {
            in_header = false;
        }
    }

    if (in_header) {
        fprintf(stderr, "%s: шапка обірвана, END OF HEADER не знайдено\n", path);
        fclose(f);
        return -1;
    }
    if (version < 3.0) {
        fprintf(stderr, "%s: версія %.2f — потрібен RINEX 3 (у v2 інша розкладка колонок)\n",
                path, version);
        fclose(f);
        return -1;
    }

    size_t count = 0;
    while (fgets(line, sizeof line, f)) {
        if (strlen(line) < 20) continue;          /* порожній хвіст файлу */

        int nlines = record_lines(line[0]);
        if (nlines < 0) {
            fprintf(stderr, "%s: невідома система '%c', запис пропущено\n", path, line[0]);
            continue;
        }

        char body[8][256];
        bool truncated = false;
        for (int i = 0; i < nlines; ++i) {
            if (!fgets(body[i], sizeof body[i], f)) { truncated = true; break; }
        }
        if (truncated) {
            fprintf(stderr, "%s: запис обірвано посеред BROADCAST ORBIT\n", path);
            break;
        }
        if (line[0] != 'G') continue;             /* стенд синтезує лише GPS L1 C/A */

        if (count == max) {
            fprintf(stderr, "%s: більше ніж %zu наборів ефемерид, решту відкинуто\n", path, max);
            break;
        }

        ephemeris_t *e = &out[count];
        memset(e, 0, sizeof *e);
        e->prn = (int)rnx_num(line, 1, 2);
        if (e->prn < 1 || e->prn > 32) {
            fprintf(stderr, "%s: PRN %d поза межами GPS, запис пропущено\n", path, e->prn);
            continue;
        }

        gps_time_t toc = calendar_to_gps((int)rnx_num(line, 4, 4), (int)rnx_num(line, 9, 2),
                                         (int)rnx_num(line, 12, 2), (int)rnx_num(line, 15, 2),
                                         (int)rnx_num(line, 18, 2), rnx_num(line, 21, 2));
        e->toc = toc.tow;
        e->af0 = rnx_num(line, 23, 19);
        e->af1 = rnx_num(line, 42, 19);
        e->af2 = rnx_num(line, 61, 19);

        double o[7][4];
        for (int i = 0; i < 7; ++i)
            for (int j = 0; j < 4; ++j)
                o[i][j] = rnx_num(body[i], 4 + j * 19, 19);

        e->iode      = (int)o[0][0];
        e->crs       = o[0][1];
        e->delta_n   = o[0][2] * M_PI;      /* напівоберти/с → рад/с */
        e->m0        = o[0][3] * M_PI;
        e->cuc       = o[1][0];
        e->ecc       = o[1][1];
        e->cus       = o[1][2];
        e->sqrt_a    = o[1][3];
        e->toe       = o[2][0];
        e->cic       = o[2][1];
        e->omega0    = o[2][2] * M_PI;
        e->cis       = o[2][3];
        e->i0        = o[3][0] * M_PI;
        e->crc       = o[3][1];
        e->omega_arg = o[3][2] * M_PI;
        e->omega_dot = o[3][3] * M_PI;
        e->idot      = o[4][0] * M_PI;
        e->week      = (int)o[4][2];
        e->accuracy  = o[5][0];
        e->health    = (int)o[5][1];
        e->tgd       = o[5][2];
        e->iodc      = (int)o[5][3];

        if (e->sqrt_a < 1000.0 || e->ecc < 0.0 || e->ecc > 0.1) {
            fprintf(stderr, "PRN %02d: неправдоподібна орбіта (√A=%.1f e=%.4f), запис відкинуто\n",
                    e->prn, e->sqrt_a, e->ecc);
            continue;
        }
        count++;
    }

    fclose(f);
    if (count == 0) {
        fprintf(stderr, "%s: жодного придатного запису GPS\n", path);
        return -1;
    }
    return (int)count;
}

const ephemeris_t *eph_select(const ephemeris_t *set, size_t n, int prn, gps_time_t t)
{
    const ephemeris_t *best = NULL;
    double best_age = 0.0;

    for (size_t i = 0; i < n; ++i) {
        if (set[i].prn != prn) continue;
        if (set[i].health != 0) continue;      /* нездоровий апарат у сузір'я не йде */

        gps_time_t toe = { set[i].week, set[i].toe };
        double age = fabs(gps_time_diff(t, toe));
        if (age > 7200.0) continue;            /* поза інтервалом придатності 4 год */
        if (!best || age < best_age) { best = &set[i]; best_age = age; }
    }
    return best;
}

bool eph_sat_state(const ephemeris_t *e, gps_time_t t, sat_state_t *st)
{
    if (!e || !st) return false;

    gps_time_t toe = { e->week, e->toe };
    double tk = gps_time_diff(t, toe);
    if (fabs(tk) > 7200.0) return false;

    const double a  = e->sqrt_a * e->sqrt_a;
    const double n0 = sqrt(GPS_MU / (a * a * a));
    const double n  = n0 + e->delta_n;
    const double mk = e->m0 + n * tk;

    /* Рівняння Кеплера: M = E − e·sin E, метод Ньютона. */
    double ek = mk;
    int it;
    for (it = 0; it < 20; ++it) {
        double f  = ek - e->ecc * sin(ek) - mk;
        double fp = 1.0 - e->ecc * cos(ek);
        double dek = f / fp;
        ek -= dek;
        if (fabs(dek) < 1e-13) break;
    }
    if (it == 20) {
        fprintf(stderr, "PRN %02d: рівняння Кеплера не зійшлося\n", e->prn);
        return false;
    }

    const double sin_ek = sin(ek), cos_ek = cos(ek);
    const double one_e2 = sqrt(1.0 - e->ecc * e->ecc);
    const double vk   = atan2(one_e2 * sin_ek, cos_ek - e->ecc);
    const double phik = vk + e->omega_arg;
    const double s2 = sin(2.0 * phik), c2 = cos(2.0 * phik);

    const double duk = e->cus * s2 + e->cuc * c2;
    const double drk = e->crs * s2 + e->crc * c2;
    const double dik = e->cis * s2 + e->cic * c2;

    const double uk = phik + duk;
    const double rk = a * (1.0 - e->ecc * cos_ek) + drk;
    const double ik = e->i0 + dik + e->idot * tk;

    const double xp = rk * cos(uk), yp = rk * sin(uk);
    const double omk = e->omega0 + (e->omega_dot - GPS_OMEGA_E) * tk - GPS_OMEGA_E * e->toe;
    const double sin_om = sin(omk), cos_om = cos(omk);
    const double sin_ik = sin(ik),  cos_ik = cos(ik);

    st->pos.x = xp * cos_om - yp * cos_ik * sin_om;
    st->pos.y = xp * sin_om + yp * cos_ik * cos_om;
    st->pos.z = yp * sin_ik;

    /* Швидкість — аналітичні похідні тих самих виразів: числове диференціювання
     * дало б шум у доплері, а доплер тут і є предметом. */
    const double ek_dot = n / (1.0 - e->ecc * cos_ek);
    const double vk_dot = ek_dot * one_e2 / (1.0 - e->ecc * cos_ek);
    const double uk_dot = vk_dot * (1.0 + 2.0 * (e->cus * c2 - e->cuc * s2));
    const double rk_dot = a * e->ecc * sin_ek * ek_dot + 2.0 * vk_dot * (e->crs * c2 - e->crc * s2);
    const double ik_dot = e->idot + 2.0 * vk_dot * (e->cis * c2 - e->cic * s2);
    const double om_dot = e->omega_dot - GPS_OMEGA_E;

    const double xp_dot = rk_dot * cos(uk) - rk * uk_dot * sin(uk);
    const double yp_dot = rk_dot * sin(uk) + rk * uk_dot * cos(uk);

    st->vel.x = xp_dot * cos_om - yp_dot * cos_ik * sin_om
              + yp * sin_ik * sin_om * ik_dot - st->pos.y * om_dot;
    st->vel.y = xp_dot * sin_om + yp_dot * cos_ik * cos_om
              - yp * sin_ik * cos_om * ik_dot + st->pos.x * om_dot;
    st->vel.z = yp_dot * sin_ik + yp * cos_ik * ik_dot;

    /* Поліном годинника плюс релятивістська поправка від еліптичності орбіти. */
    double dtc = t.tow - e->toc;
    if (dtc >  302400.0) dtc -= SEC_PER_WEEK;
    if (dtc < -302400.0) dtc += SEC_PER_WEEK;

    const double dtr = GPS_F_REL * e->ecc * e->sqrt_a * sin_ek;
    st->clock_bias  = e->af0 + e->af1 * dtc + e->af2 * dtc * dtc + dtr - e->tgd;
    st->clock_drift = e->af1 + 2.0 * e->af2 * dtc
                    + GPS_F_REL * e->ecc * e->sqrt_a * cos_ek * ek_dot;
    return true;
}
