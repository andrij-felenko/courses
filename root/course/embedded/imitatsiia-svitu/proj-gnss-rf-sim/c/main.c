/* main.c — стенд імітації сузір'я GPS L1 C/A:
 * ефемериди → геометрія → I/Q для SDR, і синхронне керування атенюатором. */
#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "attenuator.h"
#include "ephemeris.h"
#include "l1ca.h"
#include "propagation.h"
#include "synth.h"

#define SAMPLE_RATE_SPS   2600000.0
#define EPOCH_MS          1.0                        /* один кодовий період */
#define SAMPLES_PER_EPOCH ((size_t)(SAMPLE_RATE_SPS * EPOCH_MS / 1000.0))
#define GEOMETRY_EVERY    100                        /* епох між перерахунком геометрії */
#define ATTEN_EVERY       200
#define ELEVATION_MASK    (5.0 * M_PI / 180.0)
#define DAC_SCALE         1500.0

/* Бюджет рівнів: те, що видає SDR, і те, що має дійти до входу приймача. */
#define SDR_OUTPUT_DBM     0.0
#define ZENITH_RX_DBM   (-128.5)   /* штатний рівень L1 C/A на вході антени */

typedef struct {
    const char *rinex, *port, *out;
    double seconds, lat_deg, lon_deg, alt_m, speed_ms, heading_deg;
    double mp_height, mp_gamma, humidity, fixed_pad_db, clock_drift_ppb;
    double leap_at;
    bool   rollover;
} config_t;

static volatile sig_atomic_t stop_requested = 0;
static void on_sigint(int sig) { (void)sig; stop_requested = 1; }

static void usage(const char *argv0)
{
    fprintf(stderr,
        "використання: %s --rinex FILE --port DEV --out FILE [опції]\n"
        "  --sec N          тривалість прогону, с (типово 60)\n"
        "  --lat/--lon/--alt координати старту (градуси, метри)\n"
        "  --speed/--course  швидкість, м/с, і курс, градуси\n"
        "  --mp-height H --mp-gamma G  висота антени й коефіцієнт відбиття\n"
        "  --fixed-pad DB   каскад фіксованих атенюаторів (типово 70)\n"
        "  --leap-at SEC    увести секунду координації на цій секунді прогону\n"
        "  --rollover       почати за 30 с до переповнення лічильника тижнів\n",
        argv0);
}

static bool parse_args(int argc, char **argv, config_t *c)
{
    *c = (config_t){ .out = "-", .seconds = 60.0, .lat_deg = 50.45, .lon_deg = 30.52,
                     .alt_m = 180.0, .speed_ms = 0.0, .heading_deg = 90.0,
                     .mp_height = 1.5, .mp_gamma = 0.5, .humidity = 0.6,
                     .fixed_pad_db = 70.0, .clock_drift_ppb = 5.0, .leap_at = -1.0 };

    for (int i = 1; i < argc; ++i) {
        const char *k = argv[i];
        bool needs_value = strcmp(k, "--rollover") != 0;
        if (needs_value && i + 1 >= argc) {
            fprintf(stderr, "%s: бракує значення\n", k);
            return false;
        }
        const char *v = needs_value ? argv[++i] : NULL;

        if      (!strcmp(k, "--rinex"))     c->rinex = v;
        else if (!strcmp(k, "--port"))      c->port = v;
        else if (!strcmp(k, "--out"))       c->out = v;
        else if (!strcmp(k, "--sec"))       c->seconds = atof(v);
        else if (!strcmp(k, "--lat"))       c->lat_deg = atof(v);
        else if (!strcmp(k, "--lon"))       c->lon_deg = atof(v);
        else if (!strcmp(k, "--alt"))       c->alt_m = atof(v);
        else if (!strcmp(k, "--speed"))     c->speed_ms = atof(v);
        else if (!strcmp(k, "--course"))    c->heading_deg = atof(v);
        else if (!strcmp(k, "--mp-height")) c->mp_height = atof(v);
        else if (!strcmp(k, "--mp-gamma"))  c->mp_gamma = atof(v);
        else if (!strcmp(k, "--fixed-pad")) c->fixed_pad_db = atof(v);
        else if (!strcmp(k, "--leap-at"))   c->leap_at = atof(v);
        else if (!strcmp(k, "--rollover"))  c->rollover = true;
        else { fprintf(stderr, "невідомий ключ %s\n", k); return false; }
    }

    if (!c->rinex || !c->port) { usage(argv[0]); return false; }
    if (c->mp_gamma < 0.0 || c->mp_gamma > 1.0) {
        fprintf(stderr, "коефіцієнт відбиття має бути в межах 0..1\n");
        return false;
    }
    return true;
}

/* Час випромінювання шукається ітераційно: затримка залежить від дистанції,
 * а дистанція — від того, де супутник був у момент випромінювання. */
static bool solve_transmit(const ephemeris_t *e, gps_time_t t_rx, vec3_t user,
                           sat_state_t *st, double *range_out)
{
    double tau = 0.075;                       /* грубе перше наближення, ~70 мс */

    for (int k = 0; k < 4; ++k) {
        gps_time_t t_tx = gps_time_add(t_rx, -tau);
        sat_state_t raw;
        if (!eph_sat_state(e, t_tx, &raw)) return false;

        /* Поправка Саньяка: поки хвиля летіла, система координат оберталася. */
        double a = GPS_OMEGA_E * tau, ca = cos(a), sa = sin(a);
        sat_state_t rot = raw;
        rot.pos.x =  raw.pos.x * ca + raw.pos.y * sa;
        rot.pos.y = -raw.pos.x * sa + raw.pos.y * ca;
        rot.vel.x =  raw.vel.x * ca + raw.vel.y * sa;
        rot.vel.y = -raw.vel.x * sa + raw.vel.y * ca;

        double dx = rot.pos.x - user.x, dy = rot.pos.y - user.y, dz = rot.pos.z - user.z;
        double range = sqrt(dx * dx + dy * dy + dz * dz);
        double tau_new = range / C_LIGHT - raw.clock_bias;

        *st = rot;
        *range_out = range;
        if (fabs(tau_new - tau) < 1e-12) return true;
        tau = tau_new;
    }
    return true;      /* чотирьох проходів вистачає з великим запасом */
}

int main(int argc, char **argv)
{
    config_t cfg;
    if (!parse_args(argc, argv, &cfg)) return 2;

    signal(SIGINT, on_sigint);

    static ephemeris_t eph[MAX_EPHEMERIS];
    nav_header_t hdr;
    int neph = rinex_load(cfg.rinex, eph, MAX_EPHEMERIS, &hdr);
    if (neph < 0) return 1;
    if (!hdr.have_iono)
        fprintf(stderr, "у шапці немає GPSA/GPSB — іоносферу моделювати нічим, буде нуль\n");

    /* Старт: перша ефемерида задає й тиждень, і момент. */
    gps_time_t t = { eph[0].week, eph[0].toe };
    if (cfg.rollover) {
        t.week = (t.week / 1024) * 1024 + 1023;
        t.tow  = 604800.0 - 30.0;
        fprintf(stderr, "сценарій переповнення: старт на тижні %d (у кадрі %d)\n",
                t.week, gps_week10(t.week));
        /* Ефемериди переносимо на той самий тиждень, інакше вони «протермінуються». */
        for (int i = 0; i < neph; ++i) { eph[i].week = t.week; eph[i].toe = t.tow + 15.0; }
    }

    nav_context_t ctx = {0};
    ctx.hdr = &hdr;
    ctx.leap.delta_t_ls = hdr.have_leap ? hdr.leap_seconds : 18;
    ctx.leap.delta_t_lsf = ctx.leap.delta_t_ls;
    memset(ctx.sv_health, 0, sizeof ctx.sv_health);

    geodetic_t llh = { cfg.lat_deg * M_PI / 180.0, cfg.lon_deg * M_PI / 180.0, cfg.alt_m };
    vec3_t user_pos = geodetic_to_ecef(llh);
    vec3_t user_vel = enu_to_ecef_vec(llh,
                                      cfg.speed_ms * sin(cfg.heading_deg * M_PI / 180.0),
                                      cfg.speed_ms * cos(cfg.heading_deg * M_PI / 180.0),
                                      0.0);

    attenuator_t att;
    if (!attenuator_open(&att, cfg.port)) return 1;

    FILE *out = (strcmp(cfg.out, "-") == 0) ? stdout : fopen(cfg.out, "wb");
    if (!out) { perror(cfg.out); attenuator_close(&att); return 1; }

    synth_t synth;
    synth_init(&synth, SAMPLE_RATE_SPS, DAC_SCALE);

    static int16_t iq[2 * 2600];
    if (SAMPLES_PER_EPOCH * 2 > sizeof iq / sizeof iq[0]) {
        fprintf(stderr, "буфер вибірок замалий для обраної частоти дискретизації\n");
        return 1;
    }

    const long total_epochs = (long)(cfg.seconds * 1000.0 / EPOCH_MS);
    double user_clock_bias = 0.0;
    bool leap_done = false;
    int last_week10 = gps_week10(t.week);
    double strongest_dbm = ZENITH_RX_DBM;

    for (long epoch = 0; epoch < total_epochs && !stop_requested; ++epoch) {
        const double model_time = epoch * EPOCH_MS / 1000.0;

        if (epoch % GEOMETRY_EVERY == 0) {
            strongest_dbm = -200.0;

            for (int prn = 1; prn <= 32; ++prn) {
                const ephemeris_t *e = eph_select(eph, (size_t)neph, prn, t);
                if (!e) { synth_release(&synth, prn); continue; }

                sat_state_t st;
                double range;
                if (!solve_transmit(e, t, user_pos, &st, &range)) {
                    synth_release(&synth, prn);
                    continue;
                }

                los_t los = line_of_sight(user_pos, llh, st.pos);
                if (los.el < ELEVATION_MASK) { synth_release(&synth, prn); continue; }

                channel_t *ch = synth_acquire(&synth, prn);
                if (!ch) continue;

                double iono = hdr.have_iono
                            ? klobuchar_delay_s(hdr.alpha, hdr.beta, llh, los, t.tow) : 0.0;
                double trop = saastamoinen_delay_s(llh, los.el, cfg.humidity);

                /* Повна псевдовідстань: геометрія, розбіжність годинників, атмосфера. */
                double pr = range + C_LIGHT * (user_clock_bias - st.clock_bias)
                          + C_LIGHT * (iono + trop);

                /* Хід годинників теж зсуває частоту: швидший бортовий стандарт
                 * випромінює вище, повільніший приймач бачить це як зсув. */
                double dopp = doppler_shift_hz(los, user_vel, st.vel, GPS_L1_HZ)
                            + GPS_L1_HZ * (st.clock_drift - cfg.clock_drift_ppb * 1e-9);

                double power = ZENITH_RX_DBM
                             + (rx_antenna_gain_db(los.el) - rx_antenna_gain_db(M_PI_2))
                             - (free_space_loss_db(range, GPS_L1_HZ)
                                - free_space_loss_db(20200000.0, GPS_L1_HZ));
                if (power > strongest_dbm) strongest_dbm = power;

                multipath_t mp = multipath_from_geometry(cfg.mp_height, los.el, cfg.mp_gamma);
                gps_time_t t_tx = gps_time_add(t, -(pr / C_LIGHT));

                channel_ensure_frame(ch, e, &ctx, t_tx);
                channel_update(ch, t_tx, pr, dopp, power, los.el, &mp);
            }

            if (synth.n < 4)
                fprintf(stderr, "t=%.1f с: над горизонтом лише %d апаратів — рішення не буде\n",
                        model_time, synth.n);
        }

        /* Крайова подія: уведення секунди координації. */
        if (cfg.leap_at >= 0.0 && !leap_done && model_time >= cfg.leap_at) {
            ctx.leap.delta_t_lsf = ctx.leap.delta_t_ls + 1;
            ctx.leap.wn_lsf = gps_week10(t.week) & 0xFF;
            ctx.leap.dn = (int)(t.tow / 86400.0) + 1;
            for (int i = 0; i < MAX_CHANNELS; ++i) synth.ch[i].frame_valid = false;
            fprintf(stderr, "t=%.1f с: у кадр піде ΔtLSF=%d (WNLSF=%d, DN=%d)\n",
                    model_time, ctx.leap.delta_t_lsf, ctx.leap.wn_lsf, ctx.leap.dn);
            leap_done = true;
        }

        if (gps_week10(t.week) != last_week10) {
            fprintf(stderr, "t=%.1f с: лічильник тижнів у кадрі %d → %d (повний %d)\n",
                    model_time, last_week10, gps_week10(t.week), t.week);
            last_week10 = gps_week10(t.week);
            for (int i = 0; i < MAX_CHANNELS; ++i) synth.ch[i].frame_valid = false;
        }

        synth_generate(&synth, iq, SAMPLES_PER_EPOCH);
        if (fwrite(iq, sizeof iq[0], SAMPLES_PER_EPOCH * 2, out) != SAMPLES_PER_EPOCH * 2) {
            perror("запис I/Q");
            break;
        }

        /* Атенюатор ведеться за найсильнішим апаратом: рівень на вході приймача
         * тримаємо штатним, скільки б не змінювалася дистанція. */
        if (epoch % ATTEN_EVERY == 0) {
            double need = SDR_OUTPUT_DBM - strongest_dbm;
            double prog = need - cfg.fixed_pad_db;
            if (prog < 0.0) {
                fprintf(stderr,
                        "потрібно %.1f дБ, а фіксований каскад дає %.1f — доберіть атенюатори!\n",
                        need, cfg.fixed_pad_db);
                prog = 0.0;
            }
            if (prog > ATT_MAX_DB) prog = ATT_MAX_DB;
            attenuator_request(&att, prog);
        }
        attenuator_poll(&att);
        if (att.state == ATT_FAILED) {
            fprintf(stderr, "керування рівнем втрачено — зупиняємось, доки не спалили LNA\n");
            break;
        }

        t = gps_time_add(t, EPOCH_MS / 1000.0);
        user_pos.x += user_vel.x * EPOCH_MS / 1000.0;
        user_pos.y += user_vel.y * EPOCH_MS / 1000.0;
        user_pos.z += user_vel.z * EPOCH_MS / 1000.0;
        llh = ecef_to_geodetic(user_pos);
        user_clock_bias += cfg.clock_drift_ppb * 1e-9 * EPOCH_MS / 1000.0;
    }

    fprintf(stderr, "завершено: каналів %d, обрізаних вибірок %lu, команд SCPI %lu, тайм-аутів %lu\n",
            synth.n, synth.clipped, att.commands, att.timeouts);

    if (out != stdout) fclose(out);
    attenuator_close(&att);
    return 0;
}
