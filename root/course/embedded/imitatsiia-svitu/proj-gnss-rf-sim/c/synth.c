#include "synth.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

/* Опорний рівень: сигнал з C/N₀ = 45 дБГц має одиничну амплітуду. */
#define REF_POWER_DBM (-130.0)

void synth_init(synth_t *s, double sample_rate, double scale)
{
    memset(s, 0, sizeof *s);
    s->sample_rate = sample_rate;
    s->scale = scale;
}

channel_t *synth_acquire(synth_t *s, int prn)
{
    for (int i = 0; i < MAX_CHANNELS; ++i)
        if (s->ch[i].active && s->ch[i].prn == prn) return &s->ch[i];

    for (int i = 0; i < MAX_CHANNELS; ++i) {
        if (s->ch[i].active) continue;
        channel_t *ch = &s->ch[i];
        memset(ch, 0, sizeof *ch);
        if (!ca_code_generate(prn, ch->code)) return NULL;
        ch->prn = prn;
        ch->active = true;
        ch->code_rate_cps = CA_CHIP_RATE_HZ;
        s->n++;
        return ch;
    }
    fprintf(stderr, "усі %d каналів зайнято, PRN %02d не додано\n", MAX_CHANNELS, prn);
    return NULL;
}

void synth_release(synth_t *s, int prn)
{
    for (int i = 0; i < MAX_CHANNELS; ++i) {
        if (s->ch[i].active && s->ch[i].prn == prn) {
            s->ch[i].active = false;
            s->n--;
            return;
        }
    }
}

void channel_ensure_frame(channel_t *ch, const ephemeris_t *e,
                          const nav_context_t *ctx, gps_time_t t_tx)
{
    if (!ch->frame_valid || nav_bit_index(&ch->frame, t_tx) < 0) {
        nav_frame_build(&ch->frame, e, ctx, t_tx);
        ch->frame_valid = true;
    }
}

void channel_update(channel_t *ch, gps_time_t t_tx, double pseudorange_m,
                    double doppler_hz, double power_dbm, double elevation_rad,
                    const multipath_t *mp)
{
    ch->doppler_hz    = doppler_hz;
    ch->pseudorange_m = pseudorange_m;
    ch->elevation_rad = elevation_rad;
    ch->power_dbm     = power_dbm;
    ch->amplitude     = pow(10.0, (power_dbm - REF_POWER_DBM) / 20.0);

    /* Доплер стискає й шкалу коду — інакше кореляційний пік поповз би. */
    ch->code_rate_cps = CA_CHIP_RATE_HZ * (1.0 + doppler_hz / GPS_L1_HZ);

    /* Фаза коду й номер біта — прямо з часу випромінювання. */
    double chips = fmod(t_tx.tow * CA_CHIP_RATE_HZ, (double)CA_CODE_LEN);
    if (chips < 0.0) chips += CA_CODE_LEN;
    ch->code_phase_chips = chips;

    int bit0 = nav_bit_index(&ch->frame, t_tx);
    if (bit0 >= 0) {
        ch->data_phase_bits = gps_time_diff(t_tx, ch->frame.start) * NAV_BIT_RATE_HZ;
    }

    /* Фаза несучої — це затримка поширення, узята за модулем 2π. */
    double carrier = -2.0 * M_PI * fmod(GPS_L1_HZ * pseudorange_m / C_LIGHT, 1.0);
    ch->carrier_phase_rad = carrier;

    if (mp && mp->gamma > 0.0 && elevation_rad > 0.0) {
        ch->mp_active       = true;
        ch->mp_delay_chips  = mp->delay_s * CA_CHIP_RATE_HZ;
        ch->mp_amplitude    = ch->amplitude * mp->gamma * pow(10.0, mp->xpol_db / 20.0);
        /* Зайвий хід променя дає свій набіг фази, а дзеркало обертає
         * поляризацію — звідси додаткові π. */
        ch->mp_phase_offset = -2.0 * M_PI * fmod(GPS_L1_HZ * mp->delay_s, 1.0) + M_PI;
    } else {
        ch->mp_active = false;
    }
}

static inline int chip_at(const channel_t *ch, double phase_chips)
{
    double p = fmod(phase_chips, (double)CA_CODE_LEN);
    if (p < 0.0) p += CA_CODE_LEN;
    return ch->code[(int)p];
}

void synth_generate(synth_t *s, int16_t *iq, size_t nsamples)
{
    const double dt = 1.0 / s->sample_rate;

    for (size_t n = 0; n < nsamples; ++n) {
        double acc_i = 0.0, acc_q = 0.0;

        for (int c = 0; c < MAX_CHANNELS; ++c) {
            channel_t *ch = &s->ch[c];
            if (!ch->active || !ch->frame_valid) continue;

            int data = nav_bit(&ch->frame, (long)ch->data_phase_bits);
            /* BPSK: чип і біт даних задають знак, решта — амплітуда й фаза. */
            double sign = (1 - 2 * chip_at(ch, ch->code_phase_chips)) * (1 - 2 * data);
            double a = ch->amplitude * sign;
            acc_i += a * cos(ch->carrier_phase_rad);
            acc_q += a * sin(ch->carrier_phase_rad);

            if (ch->mp_active) {
                double mp_sign = (1 - 2 * chip_at(ch, ch->code_phase_chips - ch->mp_delay_chips))
                               * (1 - 2 * data);
                double am = ch->mp_amplitude * mp_sign;
                double ph = ch->carrier_phase_rad + ch->mp_phase_offset;
                acc_i += am * cos(ph);
                acc_q += am * sin(ph);
            }

            ch->carrier_phase_rad += 2.0 * M_PI * ch->doppler_hz * dt;
            if (ch->carrier_phase_rad >  M_PI) ch->carrier_phase_rad -= 2.0 * M_PI;
            if (ch->carrier_phase_rad < -M_PI) ch->carrier_phase_rad += 2.0 * M_PI;

            ch->code_phase_chips += ch->code_rate_cps * dt;
            if (ch->code_phase_chips >= CA_CODE_LEN) ch->code_phase_chips -= CA_CODE_LEN;

            ch->data_phase_bits += NAV_BIT_RATE_HZ * dt;
            if (ch->data_phase_bits >= NAV_FRAME_BITS) ch->data_phase_bits -= NAV_FRAME_BITS;
        }

        double vi = acc_i * s->scale;
        double vq = acc_q * s->scale;

        /* Насичення ЦАП псує спектр гармоніками, тож рахуємо кожен випадок:
         * якщо лічильник росте — масштаб треба зменшувати. */
        if (vi >  32767.0) { vi =  32767.0; s->clipped++; }
        if (vi < -32768.0) { vi = -32768.0; s->clipped++; }
        if (vq >  32767.0) { vq =  32767.0; s->clipped++; }
        if (vq < -32768.0) { vq = -32768.0; s->clipped++; }

        iq[2 * n]     = (int16_t)lrint(vi);
        iq[2 * n + 1] = (int16_t)lrint(vq);
    }
}
