/* synth.h — канали сузір'я і синтез квадратурних вибірок для передавача SDR. */
#ifndef SYNTH_H
#define SYNTH_H

#include <stddef.h>
#include <stdint.h>

#include "l1ca.h"
#include "propagation.h"

#define MAX_CHANNELS 12

typedef struct {
    int      prn;
    bool     active;
    uint8_t  code[CA_CODE_LEN];
    nav_frame_t frame;
    bool     frame_valid;

    double code_phase_chips;
    double code_rate_cps;       /* 1.023 Мчип/с, стиснуті доплером */
    double carrier_phase_rad;   /* фаза на нульовій проміжній частоті */
    double doppler_hz;
    double data_phase_bits;     /* дробовий номер біта від початку кадру */
    double amplitude;           /* лінійна, відносно опорного рівня */

    /* Відбитий промінь. */
    bool   mp_active;
    double mp_delay_chips, mp_amplitude, mp_phase_offset;

    /* Для журналу стенда. */
    double pseudorange_m, elevation_rad, power_dbm;
} channel_t;

typedef struct {
    channel_t     ch[MAX_CHANNELS];
    int           n;
    double        sample_rate;
    double        scale;        /* сума каналів → одиниці ЦАП */
    unsigned long clipped;      /* скільки вибірок довелося обрізати */
} synth_t;

void       synth_init(synth_t *s, double sample_rate, double scale);
channel_t *synth_acquire(synth_t *s, int prn);   /* знайти або завести канал */
void       synth_release(synth_t *s, int prn);
void       synth_generate(synth_t *s, int16_t *iq, size_t nsamples);

/* Прив'язує канал до нової геометрії: фаза коду й несучої задається часом
 * випромінювання, тож псевдовідстань відтворюється буквально. */
void channel_update(channel_t *ch, gps_time_t t_tx, double pseudorange_m,
                    double doppler_hz, double power_dbm, double elevation_rad,
                    const multipath_t *mp);

void channel_ensure_frame(channel_t *ch, const ephemeris_t *e,
                          const nav_context_t *ctx, gps_time_t t_tx);

#endif /* SYNTH_H */
