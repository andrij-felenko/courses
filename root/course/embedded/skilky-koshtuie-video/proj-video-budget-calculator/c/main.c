#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// ── Переліки типів кодеків та режимів роботи ───────────────────────────────
typedef enum {
    CODEC_RAW_BAYER = 0,
    CODEC_MJPEG,
    CODEC_H264_AVC,
    CODEC_H265_HEVC
} video_codec_t;

typedef enum {
    LIGHT_DAY = 0,
    LIGHT_NIGHT_IR
} lighting_mode_t;

// ── Вхідні параметри відеосистеми ──────────────────────────────────────────
typedef struct {
    uint32_t width;             // Горизонтальна роздільність (пікселі)
    uint32_t height;            // Вертикальна роздільність (пікселі)
    uint32_t fps;               // Частота кадрів (к/с)
    uint8_t  bpp_raw;           // Глибина кольору сенсора (10 або 12 біт/піксель)
    video_codec_t codec;        // Обраний кодек стиснення
    uint8_t  ref_frames;        // Кількість опорних кадрів для H.264/H.265 (DPB)
    lighting_mode_t light_mode; // Денний або нічний режим
    double   ir_optical_watts;  // Необхідна оптична потужність ІЧ-підсвічування (Вт)
    double   ir_led_efficiency; // Електрооптичний ККД світлодіода (типово 0.25 - 0.35)
    double   soc_base_power_w;  // Базова потужність SoC у роботі (Вт)
    double   vpu_power_w;       // Потужність апаратного кодека VPU (Вт)
    double   sensor_power_w;    // Потужність сенсора камери (Вт)
    double   radio_tx_power_w;  // Потужність Wi-Fi/LTE у режимі передачі (Вт)
    double   radio_idle_power_w;// Потужність Wi-Fi/LTE у черговому прийомі (Вт)
    double   battery_capacity_wh;// Енергоємність акумулятора (Вт·год, напр. 3.7 В * 10 А·год = 37 Вт·год)
    double   edge_ai_duty_cycle;// Частка часу активної передачі в Edge AI (напр. 0.005 = 0.5%)
} video_system_config_t;

// ── Результати аналізу бюджету ─────────────────────────────────────────────
typedef struct {
    double raw_sensor_mbps;     // Бітрейт із сенсора (Мбіт/с)
    double yuv420_frame_mb;     // Розмір одного YUV420 кадру (МБ)
    double compressed_bitrate_mbps; // Бітрейт стисненого потоку (Мбіт/с)
    double dram_bandwidth_mbytes_sec; // Сумарне навантаження на шину RAM (МБ/с)
    double min_ram_dpb_mb;      // Мінімальна пам'ять під DPB та буферизацію (МБ)
    double total_power_day_w;   // Загальна електрична потужність вдень (Вт)
    double total_power_night_w; // Загальна електрична потужність вночі з ІЧ (Вт)
    double autonomy_streaming_hours; // Автономність при безперервному стрімінгу (годин)
    double autonomy_edge_ai_days;    // Автономність у подійно-орієнтованому Edge AI (діб)
} video_budget_result_t;

// ── Функція розрахунку бюджету ─────────────────────────────────────────────
void calculate_video_budget(const video_system_config_t *cfg, video_budget_result_t *res)
{
    uint64_t total_pixels_sec = (uint64_t)cfg->width * cfg->height * cfg->fps;

    // 1. Сирий піксельний потік із сенсора (RAW Bayer)
    res->raw_sensor_mbps = (double)(total_pixels_sec * cfg->bpp_raw) / 1000000.0;

    // Розмір одного кадру YUV420 (12 біт = 1.5 байти на піксель)
    double frame_bytes = (double)cfg->width * cfg->height * 1.5;
    res->yuv420_frame_mb = frame_bytes / (1024.0 * 1024.0);

    // 2. Розрахунок бітрейту залежно від кодека
    // YUV420 сирий бітрейт = width * height * 12 біт * fps
    double yuv_raw_mbps = (double)(total_pixels_sec * 12) / 1000000.0;
    
    switch (cfg->codec) {
        case CODEC_RAW_BAYER:
            res->compressed_bitrate_mbps = res->raw_sensor_mbps;
            break;
        case CODEC_MJPEG:
            // Коефіцієнт стиснення ~10x
            res->compressed_bitrate_mbps = yuv_raw_mbps / 10.0;
            break;
        case CODEC_H264_AVC:
            // Коефіцієнт стиснення ~80x - 100x для типової сцени
            res->compressed_bitrate_mbps = yuv_raw_mbps / 85.0;
            break;
        case CODEC_H265_HEVC:
            // Коефіцієнт стиснення ~150x - 180x
            res->compressed_bitrate_mbps = yuv_raw_mbps / 160.0;
            break;
    }

    // 3. Трафік шини оперативної пам'яті (DRAM / AXI Bandwidth)
    // - ISP записує YUV420 кадри в DRAM: 1.5 байти/пікс * fps
    // - VPU зчитує поточний YUV420 кадр із DRAM: 1.5 байти/пікс * fps
    // - VPU читає/пише опорні кадри (DPB): приблизно 2x від розміру кадру для пошуку руху
    // - VPU записує стиснений бітстрім: compressed_bitrate_mbps / 8
    double yuv_bytes_per_sec = frame_bytes * cfg->fps;
    double isp_write_mbs = yuv_bytes_per_sec / (1024.0 * 1024.0);
    double vpu_read_mbs = isp_write_mbs;
    double dpb_traffic_mbs = (cfg->codec >= CODEC_H264_AVC) ? (isp_write_mbs * 2.0) : 0.0;
    double bitstream_mbs = (res->compressed_bitrate_mbps * 1000000.0 / 8.0) / (1024.0 * 1024.0);

    res->dram_bandwidth_mbytes_sec = isp_write_mbs + vpu_read_mbs + dpb_traffic_mbs + bitstream_mbs;

    // 4. Пам'ять під буферизацію (DPB + черга ISP + черга кодера)
    // Мінімум 2 буфери на захоплення (double buffering) + ref_frames для кодека + 1 вихідний
    uint32_t total_frame_buffers = 2 + (cfg->codec >= CODEC_H264_AVC ? cfg->ref_frames : 1) + 1;
    res->min_ram_dpb_mb = total_frame_buffers * res->yuv420_frame_mb;

    // 5. Електрична потужність
    double ir_electrical_power_w = (cfg->ir_led_efficiency > 0.05) 
        ? (cfg->ir_optical_watts / cfg->ir_led_efficiency) : 0.0;

    double base_active_power = cfg->soc_base_power_w + cfg->vpu_power_w + cfg->sensor_power_w;
    
    // Денний режим (без ІЧ)
    res->total_power_day_w = base_active_power + cfg->radio_tx_power_w;
    // Нічний режим (з ІЧ)
    res->total_power_night_w = res->total_power_day_w + ir_electrical_power_w;

    // 6. Автономність: Хмарний стрімінг (100% активності радіо) проти Edge AI (duty cycle 0.5%)
    double avg_streaming_power = (res->total_power_day_w + res->total_power_night_w) / 2.0;
    res->autonomy_streaming_hours = cfg->battery_capacity_wh / avg_streaming_power;

    // Для Edge AI: 99.5% часу спимо або крутимо черговий сенсор/PIR (наприклад 0.03 Вт),
    // 0.5% часу прокидаємося на інференс і коротку передачу метаданих
    double edge_ai_active_power = base_active_power + cfg->radio_tx_power_w;
    double edge_ai_sleep_power = 0.030; // 30 мВт у черговому режимі
    double edge_ai_avg_power = (cfg->edge_ai_duty_cycle * edge_ai_active_power) + 
                               ((1.0 - cfg->edge_ai_duty_cycle) * edge_ai_sleep_power);
    
    res->autonomy_edge_ai_days = (cfg->battery_capacity_wh / edge_ai_avg_power) / 24.0;
}

// ── Демонстрація розрахунків ───────────────────────────────────────────────
int main(void)
{
    // Профіль: 1080p @ 30 fps, H.264 кодек, 4 референсні кадри, нічне підсвічування 1 Вт оптичної потужності
    video_system_config_t config_1080p = {
        .width = 1920,
        .height = 1080,
        .fps = 30,
        .bpp_raw = 10,
        .codec = CODEC_H264_AVC,
        .ref_frames = 4,
        .light_mode = LIGHT_NIGHT_IR,
        .ir_optical_watts = 1.0,
        .ir_led_efficiency = 0.30,  // 30% ККД світлодіода
        .soc_base_power_w = 0.50,   // 500 мВт ядро SoC/DDR
        .vpu_power_w = 0.30,        // 300 мВт апаратний кодек
        .sensor_power_w = 0.20,     // 200 мВт CMOS сенсор
        .radio_tx_power_w = 1.10,   // 1.1 Вт Wi-Fi передавач
        .radio_idle_power_w = 0.10, // 100 мВт очікування
        .battery_capacity_wh = 37.0,// Акумулятор Li-ion 10 А·год при 3.7 В (37 Вт·год)
        .edge_ai_duty_cycle = 0.005 // 0.5% часу активні (подійна детекція)
    };

    video_budget_result_t result;
    calculate_video_budget(&config_1080p, &result);

    printf("=== АУДИТ БЮДЖЕТУ ВІДЕОСИСТЕМИ (1080p @ 30 fps, H.264) ===\n");
    printf("1. Сирий піксельний потік сенсора (10-bit RAW): %.2f Мбіт/с\n", result.raw_sensor_mbps);
    printf("2. Бітрейт стисненого відеопотоку H.264:        %.2f Мбіт/с\n", result.compressed_bitrate_mbps);
    printf("3. Навантаження на шину DRAM (AXI Bandwidth):   %.2f МБ/с\n", result.dram_bandwidth_mbytes_sec);
    printf("4. Мінімальний розмір пулу кадрових буферів:    %.2f МБ\n", result.min_ram_dpb_mb);
    printf("5. Споживання енергії (Денний режим):           %.2f Вт\n", result.total_power_day_w);
    printf("6. Споживання енергії (Нічний режим з ІЧ):      %.2f Вт\n", result.total_power_night_w);
    printf("7. Автономність (Хмарний безперервний стрім):   %.1f годин\n", result.autonomy_streaming_hours);
    printf("8. Автономність (Edge AI з подійною передачею): %.1f діб\n", result.autonomy_edge_ai_days);

    return 0;
}
