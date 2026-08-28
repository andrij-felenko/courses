#include <math.h>
#include <stddef.h>
#include <stdlib.h>

#define M_PI_F 3.14159265358979323846f
#define HILBERT_TAPS 31

/* Коефіцієнти КІХ-фільтра Гільберта (-90 градусів) */
static float hilbert_coeffs[HILBERT_TAPS];

void init_hilbert_filter(void) {
    int center = HILBERT_TAPS / 2;
    for (int i = 0; i < HILBERT_TAPS; i++) {
        int n = i - center;
        if (n % 2 != 0) {
            /* Непарні коефіцієнти КІХ-фільтра Гільберта */
            float w = 0.54f - 0.46f * cosf(2.0f * M_PI_F * i / (HILBERT_TAPS - 1)); /* Вікно Геммінга */
            hilbert_coeffs[i] = (2.0f / (M_PI_F * (float)n)) * w;
        } else {
            hilbert_coeffs[i] = 0.0f;
        }
    }
}

/* Структура цифрового SSB модулятора */
typedef struct {
    float audio_buffer[HILBERT_TAPS];
    size_t buf_idx;
    float phase_acc;
    float phase_inc; /* 2 * PI * f_carrier / f_sample */
} ssb_modulator_t;

void ssb_modulator_init(ssb_modulator_t *mod, float f_carrier, float f_sample) {
    for (size_t i = 0; i < HILBERT_TAPS; i++) {
        mod->audio_buffer[i] = 0.0f;
    }
    mod->buf_idx = 0;
    mod->phase_acc = 0.0f;
    mod->phase_inc = 2.0f * M_PI_F * f_carrier / f_sample;
}

/* Обробка одного відліку звуку: повертає значення SSB сигналу (USB або LSB) */
float ssb_modulate_sample(ssb_modulator_t *mod, float audio_sample, int is_usb) {
    /* Запис у кільцевий буфер */
    mod->audio_buffer[mod->buf_idx] = audio_sample;
    
    /* Сгортка для отримання Гільбертового образа (канал Q) */
    float q_audio = 0.0f;
    for (size_t i = 0; i < HILBERT_TAPS; i++) {
        size_t idx = (mod->buf_idx + HILBERT_TAPS - i) % HILBERT_TAPS;
        q_audio += mod->audio_buffer[idx] * hilbert_coeffs[i];
    }
    
    /* Затримка каналу I для компенсації групової затримки КІХ-фільтра */
    size_t delay_idx = (mod->buf_idx + HILBERT_TAPS - (HILBERT_TAPS / 2)) % HILBERT_TAPS;
    float i_audio = mod->audio_buffer[delay_idx];
    
    mod->buf_idx = (mod->buf_idx + 1) % HILBERT_TAPS;
    
    /* Квадратурний перенос на радіочастоту */
    float cos_c = cosf(mod->phase_acc);
    float sin_c = sinf(mod->phase_acc);
    
    mod->phase_acc += mod->phase_inc;
    if (mod->phase_acc >= 2.0f * M_PI_F) {
        mod->phase_acc -= 2.0f * M_PI_F;
    }
    
    /* Формування SSB: USB = I*cos - Q*sin, LSB = I*cos + Q*sin */
    if (is_usb) {
        return i_audio * cos_c - q_audio * sin_c;
    } else {
        return i_audio * cos_c + q_audio * sin_c;
    }
}
