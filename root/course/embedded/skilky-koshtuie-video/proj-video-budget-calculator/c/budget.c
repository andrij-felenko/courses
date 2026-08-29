#include "budget.h"

#include <stddef.h>

#define MEGA 1000000.0

/* Питомий бітрейт зміряний на сцені відеоспостереження (статичний фон,
 * рух у частині кадру). Для H.264 це 0.052 біт/піксель — тобто стиснення
 * приблизно 12 / 0.052 ≈ 230 разів відносно сирого YUV420. */
double codec_bits_per_pixel(video_codec_t codec, uint8_t bpp_raw)
{
    switch (codec) {
        case CODEC_RAW_BAYER: return (double)bpp_raw; /* без стиснення взагалі */
        case CODEC_MJPEG:     return 0.750;           /* лише внутрішньокадрове, ~16x */
        case CODEC_H264_AVC:  return 0.052;
        case CODEC_H265_HEVC: return 0.026;           /* удвічі краще за AVC на тій самій якості */
    }
    return 0.0;
}

const char *codec_name(video_codec_t codec)
{
    switch (codec) {
        case CODEC_RAW_BAYER: return "RAW Bayer";
        case CODEC_MJPEG:     return "MJPEG";
        case CODEC_H264_AVC:  return "H.264 (AVC)";
        case CODEC_H265_HEVC: return "H.265 (HEVC)";
    }
    return "?";
}

const char *budget_status_text(budget_status_t status)
{
    switch (status) {
        case BUDGET_OK:               return "гаразд";
        case BUDGET_ERR_NULL:         return "порожній вказівник на конфігурацію чи результат";
        case BUDGET_ERR_GEOMETRY:     return "роздільність нульова або непарна (YUV420 вимагає парних сторін)";
        case BUDGET_ERR_FPS:          return "частота кадрів поза 1..240 к/с";
        case BUDGET_ERR_RAW_DEPTH:    return "розрядність матриці поза 8..16 біт";
        case BUDGET_ERR_REF_FRAMES:   return "глибина DPB поза 1..16 кадрів";
        case BUDGET_ERR_IR_EFFICIENCY:return "ККД ІЧ-світлодіода поза 0.05..1.0";
        case BUDGET_ERR_POWER:        return "від'ємна потужність або нульове споживання в черговому режимі";
        case BUDGET_ERR_BATTERY:      return "ємність акумулятора має бути додатною";
        case BUDGET_ERR_DUTY_CYCLE:   return "коефіцієнт заповнення Edge AI поза (0..1]";
    }
    return "невідома помилка";
}

static int uses_reference_frames(video_codec_t codec)
{
    return codec == CODEC_H264_AVC || codec == CODEC_H265_HEVC;
}

/* Валідація окремо від математики: далі в розрахунку немає жодної перевірки,
 * бо всі ділення тут уже захищені. */
static budget_status_t validate(const video_config_t *cfg)
{
    if (cfg->width == 0 || cfg->height == 0 ||
        (cfg->width % 2) != 0 || (cfg->height % 2) != 0)
        return BUDGET_ERR_GEOMETRY;

    if (cfg->fps == 0 || cfg->fps > 240)
        return BUDGET_ERR_FPS;

    if (cfg->bpp_raw < 8 || cfg->bpp_raw > 16)
        return BUDGET_ERR_RAW_DEPTH;

    if (uses_reference_frames(cfg->codec) && (cfg->ref_frames == 0 || cfg->ref_frames > 16))
        return BUDGET_ERR_REF_FRAMES;

    /* ККД питаємо лише тоді, коли підсвічування справді стоїть: інакше
     * конфігурація денної камери спотикалася б об поле, якого не заповнили. */
    if (cfg->ir_optical_w < 0.0)
        return BUDGET_ERR_POWER;
    if (cfg->ir_optical_w > 0.0 &&
        (cfg->ir_led_efficiency < 0.05 || cfg->ir_led_efficiency > 1.0))
        return BUDGET_ERR_IR_EFFICIENCY;

    if (cfg->soc_base_w < 0.0 || cfg->vpu_w < 0.0 || cfg->sensor_w < 0.0 ||
        cfg->radio_tx_w < 0.0 || cfg->standby_w <= 0.0)
        return BUDGET_ERR_POWER;

    if (cfg->battery_wh <= 0.0)
        return BUDGET_ERR_BATTERY;

    if (cfg->edge_duty_cycle <= 0.0 || cfg->edge_duty_cycle > 1.0)
        return BUDGET_ERR_DUTY_CYCLE;

    return BUDGET_OK;
}

budget_status_t video_budget_eval(const video_config_t *cfg, video_budget_t *out)
{
    if (cfg == NULL || out == NULL)
        return BUDGET_ERR_NULL;

    budget_status_t status = validate(cfg);
    if (status != BUDGET_OK)
        return status;

    const double pixels_per_sec = (double)cfg->width * (double)cfg->height * (double)cfg->fps;
    const double raw_frame_bytes = (double)cfg->width * (double)cfg->height * cfg->bpp_raw / 8.0;
    const double yuv_frame_bytes = (double)cfg->width * (double)cfg->height * 3.0 / 2.0;
    const int    dpb = uses_reference_frames(cfg->codec);

    /* 1. Піксельний потік із матриці та розмір кадру після ISP. */
    out->raw_sensor_mbps  = pixels_per_sec * cfg->bpp_raw / MEGA;
    out->yuv420_frame_mb  = yuv_frame_bytes / MEGA;
    out->codec_mbps       = pixels_per_sec * codec_bits_per_pixel(cfg->codec, cfg->bpp_raw) / MEGA;

    /* 2. Трафік системної шини. Кадр перетинає її стільки разів, скільки
     *    блоків його чіпає, і саме цей множник вбиває платформу, а не бітрейт. */
    const double bitstream_bytes_s = out->codec_mbps * MEGA / 8.0;
    if (cfg->codec == CODEC_RAW_BAYER) {
        /* Сирий тракт: DMA пише кадр, споживач його читає — два проходи. */
        out->dram_mbytes_s = 2.0 * raw_frame_bytes * cfg->fps / MEGA;
    } else {
        const double yuv_bytes_s = yuv_frame_bytes * cfg->fps;
        const double bus_bytes_s =
              yuv_bytes_s                          /* ISP пише кадр YUV420          */
            + yuv_bytes_s                          /* VPU читає його на кодування   */
            + (dpb ? 2.0 * yuv_bytes_s : 0.0)      /* читання-запис опорних кадрів  */
            + bitstream_bytes_s;                   /* кодер пише бітстрім           */
        out->dram_mbytes_s = bus_bytes_s / MEGA;
    }

    /* 3. Пул кадрових буферів: подвійна буферизація захоплення + DPB (або один
     *    робочий кадр для внутрішньокадрових кодеків) + кадр на віддачу. */
    const double buffer_bytes = (cfg->codec == CODEC_RAW_BAYER) ? raw_frame_bytes : yuv_frame_bytes;
    out->frame_buffers = 2u + (dpb ? (uint32_t)cfg->ref_frames : 1u) + 1u;
    out->ram_pool_mb   = out->frame_buffers * buffer_bytes / MEGA;

    /* 4. Електрика. ІЧ-підсвічування рахуємо від оптичної потужності через ККД:
     *    від розетки воно бере втричі більше, ніж світить. */
    out->ir_electrical_w = (cfg->ir_optical_w > 0.0)
                         ? cfg->ir_optical_w / cfg->ir_led_efficiency
                         : 0.0;

    const double active_w = cfg->soc_base_w + cfg->vpu_w + cfg->sensor_w;
    out->power_day_w   = active_w + cfg->radio_tx_w;
    out->power_night_w = out->power_day_w + out->ir_electrical_w;

    /* 5. Автономність. Стрімінг: половину доби день, половину ніч. */
    out->power_stream_w    = (out->power_day_w + out->power_night_w) / 2.0;
    out->autonomy_stream_h = cfg->battery_wh / out->power_stream_w;

    /* Edge AI: більшість часу спимо на черговій схемі, зрідка прокидаємось
     * на інференс і коротку передачу метаданих. */
    out->power_edge_w = cfg->edge_duty_cycle * out->power_day_w
                      + (1.0 - cfg->edge_duty_cycle) * cfg->standby_w;
    out->autonomy_edge_days = cfg->battery_wh / out->power_edge_w / 24.0;

    return BUDGET_OK;
}
