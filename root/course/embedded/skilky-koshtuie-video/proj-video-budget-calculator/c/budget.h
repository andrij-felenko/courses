#ifndef VIDEO_BUDGET_H
#define VIDEO_BUDGET_H

#include <stdint.h>

/* Модель бюджету відеотракту: піксельний потік, трафік шини, пам'ять під
 * кадрові буфери, електрична потужність і автономність від акумулятора.
 *
 * Усі «мега» тут десяткові (10^6): даташити шин, кодеків і радіо рахують
 * саме так, і змішувати їх з двійковими МіБ у одному звіті — найкоротший
 * шлях до похибки у 5 % там, де ми сперечаємось за 10 %. */

typedef enum {
    CODEC_RAW_BAYER = 0, /* без стиснення: сирий Bayer прямо в пам'ять */
    CODEC_MJPEG,         /* лише внутрішньокадрове стиснення, без опорних кадрів */
    CODEC_H264_AVC,      /* міжкадрове передбачення, потрібен DPB */
    CODEC_H265_HEVC
} video_codec_t;

typedef struct {
    uint32_t width;          /* активні пікселі по горизонталі */
    uint32_t height;         /* активні пікселі по вертикалі */
    uint32_t fps;            /* частота кадрів, к/с */
    uint8_t  bpp_raw;        /* розрядність АЦП матриці, біт/піксель (8..16) */
    video_codec_t codec;     /* обраний кодек */
    uint8_t  ref_frames;     /* глибина DPB для міжкадрових кодеків */

    double ir_optical_w;     /* потрібна ОПТИЧНА потужність ІЧ-підсвічування, Вт (0 — немає) */
    double ir_led_efficiency;/* електрооптичний ККД світлодіода, 0.05..1.0 */

    double soc_base_w;       /* ядро SoC разом з контролером пам'яті, Вт */
    double vpu_w;            /* апаратний кодек (VPU) або NPU під час роботи, Вт */
    double sensor_w;         /* матриця з аналоговим трактом, Вт */
    double radio_tx_w;       /* радіо в режимі передачі, Вт */
    double standby_w;        /* чергова схема під час сну (PIR, RTC, домен утримання), Вт */

    double battery_wh;       /* енергоємність акумулятора, Вт·год */
    double edge_duty_cycle;  /* частка часу активності в режимі Edge AI, 0..1 */
} video_config_t;

typedef struct {
    double   raw_sensor_mbps;    /* сирий потік із матриці, Мбіт/с */
    double   yuv420_frame_mb;    /* один кадр YUV420, МБ */
    double   codec_mbps;         /* бітрейт після кодека, Мбіт/с */
    double   dram_mbytes_s;      /* сумарний трафік системної шини, МБ/с */
    uint32_t frame_buffers;      /* скільки кадрових буферів тримаємо одночасно */
    double   ram_pool_mb;        /* пул під ці буфери, МБ */

    double ir_electrical_w;      /* що ІЧ-підсвічування бере від джерела живлення, Вт */
    double power_day_w;          /* повне споживання вдень, Вт */
    double power_night_w;        /* повне споживання вночі з ІЧ, Вт */
    double power_stream_w;       /* середнє за добу при безперервному стрімінгу, Вт */
    double autonomy_stream_h;    /* автономність у режимі стрімінгу, годин */
    double power_edge_w;         /* середнє за добу в режимі Edge AI, Вт */
    double autonomy_edge_days;   /* автономність у режимі Edge AI, діб */
} video_budget_t;

typedef enum {
    BUDGET_OK = 0,
    BUDGET_ERR_NULL,
    BUDGET_ERR_GEOMETRY,      /* нульова або непарна роздільність */
    BUDGET_ERR_FPS,
    BUDGET_ERR_RAW_DEPTH,
    BUDGET_ERR_REF_FRAMES,
    BUDGET_ERR_IR_EFFICIENCY, /* ККД поза 0.05..1.0 при наявному підсвічуванні */
    BUDGET_ERR_POWER,         /* від'ємна потужність або нульовий черговий струм */
    BUDGET_ERR_BATTERY,
    BUDGET_ERR_DUTY_CYCLE
} budget_status_t;

/* Питомий бітрейт кодека для типової сцени відеоспостереження, біт/піксель. */
double      codec_bits_per_pixel(video_codec_t codec, uint8_t bpp_raw);
const char *codec_name(video_codec_t codec);
const char *budget_status_text(budget_status_t status);

/* Головний розрахунок. Повертає BUDGET_OK і заповнює out, або код помилки
 * валідації — і тоді out лишається незайманим. */
budget_status_t video_budget_eval(const video_config_t *cfg, video_budget_t *out);

#endif /* VIDEO_BUDGET_H */
