#ifndef ACOUSTIC_DETECTOR_H
#define ACOUSTIC_DETECTOR_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define AUDIO_SAMPLE_RATE     16000
#define AUDIO_FRAME_SAMPLES   256
#define AUDIO_FFT_SIZE        512
#define AUDIO_MEL_BINS        32
#define AUDIO_NUM_FRAMES      40
#define NUM_EVENT_CLASSES     4

typedef enum {
    EVENT_CLASS_BACKGROUND = 0,
    EVENT_CLASS_GLASS_BREAK = 1,
    EVENT_CLASS_GUNSHOT     = 2,
    EVENT_CLASS_ALARM_SIREN = 3
} acoustic_event_t;

typedef struct {
    uint32_t energy_threshold;
    uint32_t background_noise;
    uint8_t  frames_recorded;
    bool     event_in_progress;
    int8_t   feature_matrix[AUDIO_NUM_FRAMES][AUDIO_MEL_BINS];
    int16_t  pre_emphasis_prev;
} detector_context_t;

void detector_init(detector_context_t *ctx);
void detector_process_half_buffer(detector_context_t *ctx, const int16_t *raw_audio, size_t len);
bool detector_poll_event(detector_context_t *ctx, acoustic_event_t *out_event, float *out_confidence);

#endif // ACOUSTIC_DETECTOR_H
