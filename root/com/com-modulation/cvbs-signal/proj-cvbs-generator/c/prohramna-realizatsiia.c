#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CVBS_NTSC_SAMPLES_PER_LINE  910
#define CVBS_NTSC_TOTAL_LINES       525

typedef enum {
    CVBS_LINE_PRE_EQUALIZING,
    CVBS_LINE_VSYNC_SERRATED,
    CVBS_LINE_POST_EQUALIZING,
    CVBS_LINE_BLANK,
    CVBS_LINE_ACTIVE
} cvbs_line_type_t;

typedef struct {
    uint16_t current_line;
    uint8_t  current_field;
    uint8_t  burst_phase;
    uint8_t  dac_lut[141]; /* Таблиця перетворення IRE (-40..+100) -> DAC (0..255) */
} cvbs_generator_t;

/* Обчислення коду ЦАП з рівня IRE */
static inline uint8_t cvbs_ire_to_dac(int16_t ire) {
    int32_t val = ((ire + 40) * 255) / 140;
    if (val < 0) return 0;
    if (val > 255) return 255;
    return (uint8_t)val;
}

/* Ініціалізація генератора та LUT */
void cvbs_init(cvbs_generator_t *gen) {
    gen->current_line = 1;
    gen->current_field = 1;
    gen->burst_phase = 0;

    for (int i = -40; i <= 100; i++) {
        gen->dac_lut[i + 40] = cvbs_ire_to_dac((int16_t)i);
    }
}

/* Визначення типу рядка NTSC */
static cvbs_line_type_t get_line_type(uint16_t line) {
    if ((line >= 1 && line <= 3) || (line >= 264 && line <= 266)) {
        return CVBS_LINE_PRE_EQUALIZING;
    } else if ((line >= 4 && line <= 6) || (line >= 267 && line <= 269)) {
        return CVBS_LINE_VSYNC_SERRATED;
    } else if ((line >= 7 && line <= 9) || (line >= 270 && line <= 272)) {
        return CVBS_LINE_POST_EQUALIZING;
    } else if ((line >= 10 && line <= 21) || (line >= 273 && line <= 284)) {
        return CVBS_LINE_BLANK;
    }
    return CVBS_LINE_ACTIVE;
}

/* Синтез одного рядка кадру у буфер DMA */
void cvbs_render_line(cvbs_generator_t *gen, uint8_t *buffer, const uint8_t *active_pixels) {
    uint8_t sync_dac  = gen->dac_lut[-40 + 40]; /* 0 IRE setup / -40 sync = 0 */
    uint8_t blank_dac = gen->dac_lut[0 + 40];   /* 0 IRE = 73 */
    cvbs_line_type_t type = get_line_type(gen->current_line);

    if (type == CVBS_LINE_PRE_EQUALIZING || type == CVBS_LINE_POST_EQUALIZING) {
        /* Короткі зрівняльні імпульси (2.3 мкс = 33 відліки) */
        for (uint16_t i = 0; i < CVBS_NTSC_SAMPLES_PER_LINE; i++) {
            buffer[i] = ((i < 33) || (i >= 455 && i < 488)) ? sync_dac : blank_dac;
        }
    } else if (type == CVBS_LINE_VSYNC_SERRATED) {
        /* Кадровий синхро з прорізами 4.7 мкс (67 відліків) */
        for (uint16_t i = 0; i < CVBS_NTSC_SAMPLES_PER_LINE; i++) {
            buffer[i] = ((i < 388) || (i >= 455 && i < 843)) ? sync_dac : blank_dac;
        }
    } else if (type == CVBS_LINE_BLANK) {
        /* Рядки гасіння VBI без колірного спалаху */
        for (uint16_t i = 0; i < CVBS_NTSC_SAMPLES_PER_LINE; i++) {
            if (i < 21) buffer[i] = blank_dac;
            else if (i < 88) buffer[i] = sync_dac;
            else buffer[i] = blank_dac;
        }
    } else {
        /* Активний відеорядок з піднесучою Color Burst */
        uint8_t phase_shift = (gen->current_line % 2 == 0) ? 2 : 0;

        for (uint16_t i = 0; i < CVBS_NTSC_SAMPLES_PER_LINE; i++) {
            if (i < 21) {
                buffer[i] = blank_dac; /* Front porch */
            } else if (i < 88) {
                buffer[i] = sync_dac;  /* Sync Tip */
            } else if (i < 105) {
                buffer[i] = blank_dac; /* Breezeway */
            } else if (i < 141) {
                /* Color burst (9 періодів по 4 відліки = 36 відліків) */
                uint8_t p = (gen->burst_phase + phase_shift) % 4;
                int16_t burst_ire = (p == 1) ? 20 : ((p == 3) ? -20 : 0);
                buffer[i] = gen->dac_lut[burst_ire + 40];
                gen->burst_phase++;
            } else if (i < 171) {
                buffer[i] = blank_dac; /* Back porch end */
            } else {
                /* Активне відео (739 відліків) */
                uint16_t px = i - 171;
                uint8_t luma = (active_pixels != NULL) ? active_pixels[px] : 50;
                buffer[i] = gen->dac_lut[(int16_t)luma + 40];
            }
        }
    }

    gen->current_line++;
    if (gen->current_line > CVBS_NTSC_TOTAL_LINES) {
        gen->current_line = 1;
        gen->current_field = (gen->current_field == 1) ? 2 : 1;
    }
}
