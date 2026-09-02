#ifndef RC_INPUT_H
#define RC_INPUT_H

#include <stdbool.h>
#include <stdint.h>

/* Декодер радіоканалу: нормалізація стіків, антибрязкіт тумблера режимів
   і виявлення втрати зв'язку за віком останнього кадру. */

#define RC_CHANNELS             8u
#define RC_FRAME_TIMEOUT_MS     300u  /* CRSF 150 Гц — це ~45 пропущених кадрів */
#define RC_MODE_DEBOUNCE_FRAMES 3u    /* 3 кадри ≈ 20 мс на 150 Гц */

/* Позиції триточкового тумблера режимів (канал 5). */
typedef enum {
    RC_MODE_AUTO = 0, /* ~1100 мкс — автономна місія */
    RC_MODE_POSHOLD,  /* ~1500 мкс — напівавтомат з утриманням */
    RC_MODE_MANUAL    /* ~1900 мкс — ручний стабілізований */
} rc_mode_t;

/* Кадр від приймача: тривалості імпульсів і мітка часу прийому. */
typedef struct {
    uint16_t pwm_us[RC_CHANNELS];
    uint32_t timestamp_ms;
} rc_frame_t;

/* Нормалізовані команди пульта. */
typedef struct {
    float roll;     /* -1.0 ... +1.0 */
    float pitch;
    float yaw;
    float throttle; /* 0.0 ... 1.0, важіль без повернення в нейтраль */
    rc_mode_t mode;
    bool link_ok;   /* false → кадри не приходять, значення нижче недійсні */
} rc_command_t;

typedef struct {
    rc_frame_t last;
    uint32_t   last_frame_ms;
    bool       have_frame;
    rc_mode_t  mode;            /* підтверджений антибрязкотом режим */
    rc_mode_t  candidate;       /* кандидат, що набирає кадри */
    uint8_t    candidate_count;
} rc_input_t;

void     rc_input_init(rc_input_t *in);
uint16_t rc_crsf_ticks_to_us(uint16_t ticks);
bool     rc_input_push(rc_input_t *in, const rc_frame_t *frame);
rc_command_t rc_input_poll(const rc_input_t *in, uint32_t now_ms);

#endif /* RC_INPUT_H */
