#include "acoustic_detector.h"
#include <string.h>

// Симетричні коефіцієнти вікна Хеммінга у форматі Q15
static const int16_t HAMMING_Q15[AUDIO_FRAME_SAMPLES] = {
    2621, 2640, 2697, 2791, 2923, 3091, 3296, 3537,
    3814, 4125, 4470, 4849, 5259, 5700, 6171, 6671,
    7199, 7752, 8330, 8931, 9554, 10196, 10857, 11534,
    12226, 12931, 13647, 14373, 15106, 15844, 16586, 17330,
    18073, 18813, 19549, 20277, 20996, 21704, 22398, 23077,
    23739, 24381, 25002, 25600, 26173, 26719, 27236, 27723,
    28178, 28599, 28985, 29334, 29645, 29916, 30147, 30336,
    30483, 30586, 30645, 30659, 30628, 30552, 30430, 30263,
    30050, 29792, 29489, 29141, 28749, 28313, 27834, 27313,
    26750, 26147, 25505, 24824, 24107, 23354, 22567, 21748,
    20897, 20017, 19110, 18177, 17220, 16242, 15245, 14230,
    13201, 12160, 11109, 10051, 8989, 7924, 6861, 5801,
    4749, 3707, 2678, 1665, 670, 0, 670, 1665
};

// Заздалегідь квантовані ваги моделі DS-CNN (INT8)
static const int8_t DS_CONV_WEIGHTS[32 * 9] = {
    12, -45, 88, 3, -15, 62, -4, 19, -33,
    54, -22, 10, -89, 45, 12, 77, -30, 4,
    -12, 90, -65, 34, 11, -8, -55, 72, 18,
    41, -19, 82, -3, 17, 60, -28, 9, -51
};

static const int32_t DS_CONV_BIAS[NUM_EVENT_CLASSES] = {
    124, -850, 420, -15
};

void detector_init(detector_context_t *ctx) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(detector_context_t));
    ctx->energy_threshold = 120000;
    ctx->background_noise = 40000;
}

static uint32_t compute_frame_energy(const int16_t *frame, size_t len) {
    uint32_t sum = 0;
    for (size_t i = 0; i < len; ++i) {
        int32_t val = frame[i] >> 4; // зменшуємо розрядність для захисту від переповнення
        sum += (uint32_t)(val * val);
    }
    return len ? (sum / (uint32_t)len) : 0;
}

// Преакцентний фільтр та накладання вікна Хеммінга
static void prepare_fft_window(detector_context_t *ctx, const int16_t *in, int16_t *out, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        // y[n] = in[n] - 0.95 * in[n-1]
        int32_t pre = (int32_t)in[i] - (((int32_t)ctx->pre_emphasis_prev * 31130) >> 15);
        ctx->pre_emphasis_prev = in[i];

        // Зважування вікном Хеммінга
        int32_t win = (pre * (int32_t)HAMMING_Q15[i % AUDIO_FRAME_SAMPLES]) >> 15;
        if (win > 32767) win = 32767;
        if (win < -32768) win = -32768;
        out[i] = (int16_t)win;
    }
}

// Емуляція згортки CMSIS-NN Depthwise Separable над 2D матрицею ознак
static void run_ds_cnn_inference(const int8_t features[AUDIO_NUM_FRAMES][AUDIO_MEL_BINS],
                                 int32_t *out_logits) {
    for (size_t c = 0; c < NUM_EVENT_CLASSES; ++c) {
        int32_t acc = DS_CONV_BIAS[c];
        for (size_t f = 0; f < AUDIO_NUM_FRAMES; f += 2) {
            for (size_t b = 0; b < AUDIO_MEL_BINS; b += 2) {
                int32_t in_val = (int32_t)features[f][b];
                int32_t wt_val = (int32_t)DS_CONV_WEIGHTS[(c * 32 + b) % (32 * 9)];
                acc += in_val * wt_val;
            }
        }
        out_logits[c] = acc;
    }
}

void detector_process_half_buffer(detector_context_t *ctx, const int16_t *raw_audio, size_t len) {
    if (!ctx || !raw_audio || len < AUDIO_FRAME_SAMPLES) return;

    uint32_t energy = compute_frame_energy(raw_audio, len);

    // Автоматичне підстроювання порогу фонового шуму
    if (energy < ctx->energy_threshold) {
        ctx->background_noise = ((ctx->background_noise * 31) + energy) >> 5;
        ctx->energy_threshold = ctx->background_noise * 3 + 20000;

        if (ctx->event_in_progress) {
            ctx->frames_recorded = 0;
            ctx->event_in_progress = false;
        }
        return;
    }

    ctx->event_in_progress = true;

    int16_t windowed_buf[AUDIO_FRAME_SAMPLES];
    prepare_fft_window(ctx, raw_audio, windowed_buf, len);

    // Розрахунок енергій у 32 мел-каналах (квантованих у формат int8_t)
    if (ctx->frames_recorded < AUDIO_NUM_FRAMES) {
        for (size_t bin = 0; bin < AUDIO_MEL_BINS; ++bin) {
            int32_t bin_energy = 0;
            size_t start = bin * (AUDIO_FRAME_SAMPLES / AUDIO_MEL_BINS);
            size_t end = start + (AUDIO_FRAME_SAMPLES / AUDIO_MEL_BINS);

            for (size_t s = start; s < end && s < len; ++s) {
                int32_t v = windowed_buf[s] >> 7;
                bin_energy += v * v;
            }

            int32_t log_val = (bin_energy > 0) ? (31 - __builtin_clz((unsigned int)bin_energy)) * 8 - 64 : -128;
            if (log_val > 127) log_val = 127;
            if (log_val < -128) log_val = -128;

            ctx->feature_matrix[ctx->frames_recorded][bin] = (int8_t)log_val;
        }
        ctx->frames_recorded++;
    }
}

bool detector_poll_event(detector_context_t *ctx, acoustic_event_t *out_event, float *out_confidence) {
    if (!ctx || ctx->frames_recorded < AUDIO_NUM_FRAMES) {
        return false;
    }

    int32_t logits[NUM_EVENT_CLASSES];
    run_ds_cnn_inference((const int8_t (*)[AUDIO_MEL_BINS])ctx->feature_matrix, logits);

    size_t best_class = 0;
    int32_t max_logit = logits[0];
    for (size_t i = 1; i < NUM_EVENT_CLASSES; ++i) {
        if (logits[i] > max_logit) {
            max_logit = logits[i];
            best_class = i;
        }
    }

    if (out_event) *out_event = (acoustic_event_t)best_class;
    if (out_confidence) *out_confidence = (max_logit > 0) ? ((float)max_logit / 10000.0f) : 0.0f;

    ctx->frames_recorded = 0;
    ctx->event_in_progress = false;
    return (best_class != EVENT_CLASS_BACKGROUND);
}
