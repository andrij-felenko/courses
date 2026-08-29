#include "acoustic_detector.h"

#include <math.h>
#include <string.h>

#include "dscnn.h"
#include "mel_frontend.h"

/* Коефіцієнт фільтра постійної складової, 0.995 у Q15. Мікрофонний тракт
 * завжди має зсув нуля — від нього енергія кадру росте на порожньому місці,
 * а перший коефіцієнт спектра затуляє сусідні мел-смуги. */
#define DC_POLE_Q15         32604

/* Скільки кадрів на старті йде лише на калібрування шуму (32 × 16 мс ≈ 0.5 с). */
#define NOISE_PRIMER_FRAMES 32

/* Поріг спрацювання: утричі над фоном плюс постійна добавка, яка не дає
 * детектору зриватися в цілковитій тиші, коли фон падає до одиниць. */
#define VAD_FACTOR          3u
#define VAD_MARGIN          64u

/* Пауза після інференсу, щоб хвіст тієї самої події не запустив другий
 * набір кадрів (16 × 16 мс ≈ 0.25 с). */
#define REFRACTORY_FRAMES   16

void aed_init(aed_detector_t *ctx)
{
    if (ctx == NULL) {
        return;
    }

    memset(ctx, 0, sizeof(*ctx));
    ctx->noise_floor = VAD_MARGIN;
    ctx->primer_frames = NOISE_PRIMER_FRAMES;
}

/* Фільтр постійної складової: y[n] = x[n] − x[n−1] + 0.995·y[n−1].
 * Стан тримаємо в Q8, інакше округлення саме створює той зсув, який ми
 * прибираємо. */
static void dc_block(aed_detector_t *ctx, const int16_t *in, int16_t *out)
{
    for (unsigned i = 0; i < AED_FRAME_SAMPLES; ++i) {
        const int32_t x = in[i];
        int32_t y = ((x - ctx->dc_x_prev) << 8) + ((ctx->dc_y_prev * DC_POLE_Q15) >> 15);

        ctx->dc_x_prev = x;
        ctx->dc_y_prev = y;

        y >>= 8;
        if (y > 32767) {
            y = 32767;
        } else if (y < -32768) {
            y = -32768;
        }
        out[i] = (int16_t)y;
    }
}

/* Середня потужність кадру. Кожен доданок стиснуто на 8 бітів, тож сума
 * 256 квадратів гарантовано лишається в uint32 навіть на повній шкалі. */
static uint32_t frame_energy(const int16_t *frame)
{
    uint32_t sum = 0;

    for (unsigned i = 0; i < AED_FRAME_SAMPLES; ++i) {
        const int32_t v = frame[i];
        sum += (uint32_t)((v * v) >> 8);
    }

    return sum / AED_FRAME_SAMPLES;
}

/* Найімовірніший клас і його ймовірність за softmax.
 * Це єдина операція з рухомою комою в усьому конвеєрі, і виконується вона
 * раз на 40 кадрів (640 мс) — у кадровий бюджет 16 мс вона не входить. */
static aed_event_t argmax_softmax(const float *logits, float *out_confidence)
{
    unsigned best = 0;
    float max_logit = logits[0];

    for (unsigned i = 1; i < AED_NUM_CLASSES; ++i) {
        if (logits[i] > max_logit) {
            max_logit = logits[i];
            best = i;
        }
    }

    float sum = 0.0f;
    for (unsigned i = 0; i < AED_NUM_CLASSES; ++i) {
        sum += expf(logits[i] - max_logit);
    }

    *out_confidence = 1.0f / sum;   /* expf(0) / sum для найбільшого логіта */
    return (aed_event_t)best;
}

void aed_push_frame(aed_detector_t *ctx, const int16_t *frame)
{
    if (ctx == NULL || frame == NULL) {
        return;
    }

    int16_t clean[AED_FRAME_SAMPLES];
    dc_block(ctx, frame, clean);

    const uint32_t energy = frame_energy(clean);

    if (ctx->refractory > 0) {
        --ctx->refractory;
        return;
    }

    if (!ctx->capturing) {
        /* Ковзне експоненційне середнє фону: (31·фон + енергія) / 32.
         * Стала часу близько півсекунди — кондиціонер чи дощ детектор
         * «забуде», а удар на 50–200 мс поріг підняти не встигне. */
        ctx->noise_floor = ((ctx->noise_floor * 31u) + energy) >> 5;

        if (ctx->primer_frames > 0) {
            --ctx->primer_frames;
            return;
        }

        const uint32_t threshold = ctx->noise_floor * VAD_FACTOR + VAD_MARGIN;
        if (energy <= threshold) {
            return;             /* тиша: ядро може засинати до наступного кадру */
        }

        /* Подія почалася — набираємо рівно 40 кадрів, скільки б вона не
         * тривала насправді. Хвіст і луна теж несуть ознаки класу. */
        ctx->capturing = true;
        ctx->frames_recorded = 0;
    }

    mel_frontend_frame(&ctx->pre_emphasis_prev, clean, ctx->features[ctx->frames_recorded]);
    ++ctx->frames_recorded;

    if (ctx->frames_recorded < AED_NUM_FRAMES) {
        return;
    }

    float logits[AED_NUM_CLASSES];
    dscnn_run((const int8_t (*)[AED_MEL_BINS])ctx->features, logits);

    ctx->result_event = argmax_softmax(logits, &ctx->result_confidence);
    ctx->result_ready = true;

    ctx->capturing = false;
    ctx->frames_recorded = 0;
    ctx->refractory = REFRACTORY_FRAMES;
}

bool aed_poll(aed_detector_t *ctx, aed_event_t *out_event, float *out_confidence)
{
    if (ctx == NULL || !ctx->result_ready) {
        return false;
    }

    ctx->result_ready = false;

    if (ctx->result_event == AED_EVENT_BACKGROUND) {
        return false;           /* спрацював VAD, але мережа не впізнала події */
    }

    if (out_event != NULL) {
        *out_event = ctx->result_event;
    }
    if (out_confidence != NULL) {
        *out_confidence = ctx->result_confidence;
    }

    return true;
}

const char *aed_event_name(aed_event_t event)
{
    switch (event) {
    case AED_EVENT_GLASS_BREAK: return "скло";
    case AED_EVENT_GUNSHOT:     return "постріл";
    case AED_EVENT_ALARM_SIREN: return "сирена";
    case AED_EVENT_BACKGROUND:  return "фон";
    default:                    return "?";
    }
}
