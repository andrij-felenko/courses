/* Акустичний детектор подій для Cortex-M: контракт модуля.
 *
 * Увесь стан детектора живе в одній структурі, яку викликач передає вказівником.
 * Глобальних змінних усередині немає навмисно: на чипі з двома мікрофонами
 * (наприклад, для грубого визначення напрямку) заводять два незалежні контексти.
 */
#ifndef ACOUSTIC_DETECTOR_H
#define ACOUSTIC_DETECTOR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Частота дискретизації, Гц. Кадр 256 відліків = рівно 16.0 мс. */
#define AED_SAMPLE_RATE     16000
#define AED_FRAME_SAMPLES   256

/* FFT удвічі довша за кадр: 256 відліків із вікном, решта — нулі.
 * Доповнення нулями не додає інформації, але дає вдвічі щільнішу сітку
 * частот (31.25 Гц на комірку), і трикутники мел-банку на низьких
 * частотах перестають вироджуватися в одну комірку. */
#define AED_FFT_SIZE        512
#define AED_FFT_BINS        (AED_FFT_SIZE / 2 + 1)

/* Матриця ознак: 40 кадрів × 32 мел-смуги = 640 мс звуку. */
#define AED_MEL_BINS        32
#define AED_NUM_FRAMES      40
#define AED_NUM_CLASSES     4

typedef enum {
    AED_EVENT_BACKGROUND  = 0,
    AED_EVENT_GLASS_BREAK = 1,
    AED_EVENT_GUNSHOT     = 2,
    AED_EVENT_ALARM_SIREN = 3
} aed_event_t;

/* Стан детектора. Поля відкриті лише щоб структуру можна було покласти
 * статично й побачити її розмір; ззовні їх ніхто не чіпає. */
typedef struct {
    /* Фільтр постійної складової (DC blocker), стан у Q8. */
    int32_t  dc_x_prev;
    int32_t  dc_y_prev;

    /* Преакцентний фільтр першого порядку — стан кадрового фронтенду. */
    int16_t  pre_emphasis_prev;

    /* Ковзна оцінка фонового шуму та поріг спрацювання VAD. */
    uint32_t noise_floor;
    bool     noise_primed;      /* перші кадри йдуть лише на калібрування */
    uint16_t primer_frames;

    /* Стан машини захоплення. */
    bool     capturing;
    uint8_t  frames_recorded;
    uint16_t refractory;        /* скільки кадрів мовчати після інференсу */

    /* Готовий результат чекає, поки його заберуть. */
    bool        result_ready;
    aed_event_t result_event;
    float       result_confidence;

    /* Матриця мел-ознак, квантована в int8_t. */
    int8_t   features[AED_NUM_FRAMES][AED_MEL_BINS];
} aed_detector_t;

/* Приводить контекст у робочий стан. Викликати до першого кадру. */
void aed_init(aed_detector_t *ctx);

/* Згодовує детектору один напівбуфер DMA — рівно AED_FRAME_SAMPLES відліків.
 * Викликається із задачі, не з переривання: усередині і FFT, і згортка. */
void aed_push_frame(aed_detector_t *ctx, const int16_t *frame);

/* Забирає готовий результат, якщо він є. Повертає false, поки детектор
 * набирає кадри або поки в матриці лише фон. */
bool aed_poll(aed_detector_t *ctx, aed_event_t *out_event, float *out_confidence);

/* Назва класу для журналу. */
const char *aed_event_name(aed_event_t event);

#endif /* ACOUSTIC_DETECTOR_H */
