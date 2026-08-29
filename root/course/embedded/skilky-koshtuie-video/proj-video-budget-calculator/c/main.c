#include <stdio.h>

#include "budget.h"
#include "platform.h"

static void print_platform_fit(const video_budget_t *budget)
{
    size_t count = 0;
    const platform_t *table = platform_table(&count);

    puts("   Придатність платформ:");
    for (size_t i = 0; i < count; ++i) {
        platform_check_t fit = platform_check(&table[i], budget);
        printf("     %-36s шина %6.1f %%, пам'ять %6.1f %% — %s\n",
               table[i].name, fit.bus_load_percent, fit.ram_load_percent,
               platform_fit_text(fit.verdict));
    }
}

static void print_report(const char *title, const video_config_t *cfg)
{
    video_budget_t budget;
    budget_status_t status = video_budget_eval(cfg, &budget);

    printf("\n=== %s ===\n", title);
    if (status != BUDGET_OK) {
        printf("   Конфігурацію відхилено: %s\n", budget_status_text(status));
        return;
    }

    printf("   Кодек: %s, %ux%u @ %u fps, %u-біт RAW\n",
           codec_name(cfg->codec), cfg->width, cfg->height, cfg->fps, cfg->bpp_raw);
    printf("1. Сирий піксельний потік сенсора:              %8.2f Мбіт/с\n", budget.raw_sensor_mbps);
    printf("2. Бітрейт стисненого потоку:                   %8.2f Мбіт/с\n", budget.codec_mbps);
    printf("3. Навантаження на шину пам'яті:                %8.1f МБ/с\n",   budget.dram_mbytes_s);
    printf("4. Пул кадрових буферів (%u шт. по %.2f МБ):     %8.2f МБ\n",
           budget.frame_buffers, budget.yuv420_frame_mb, budget.ram_pool_mb);
    printf("5. Споживання вдень:                            %8.2f Вт\n",     budget.power_day_w);
    printf("6. Споживання вночі (ІЧ бере %.2f Вт):          %8.2f Вт\n",
           budget.ir_electrical_w, budget.power_night_w);
    printf("7. Автономність, безперервний стрімінг:         %8.1f годин\n",  budget.autonomy_stream_h);
    printf("8. Автономність, Edge AI (%.2f %% активності):   %8.1f діб\n",
           cfg->edge_duty_cycle * 100.0, budget.autonomy_edge_days);
    printf("   Виграш подійного режиму:                     %8.0f разів\n",
           budget.autonomy_edge_days * 24.0 / budget.autonomy_stream_h);

    print_platform_fit(&budget);
}

int main(void)
{
    /* Профіль 1: типова автономна камера спостереження з нічним підсвічуванням. */
    const video_config_t cam_1080p = {
        .width = 1920, .height = 1080, .fps = 30,
        .bpp_raw = 10,
        .codec = CODEC_H264_AVC,
        .ref_frames = 4,
        .ir_optical_w = 1.0,       /* 1 Вт світла на дистанцію ~15 м */
        .ir_led_efficiency = 0.30, /* ККД ІЧ-світлодіода 940 нм */
        .soc_base_w = 0.50,
        .vpu_w = 0.30,
        .sensor_w = 0.20,
        .radio_tx_w = 1.10,
        .standby_w = 0.030,        /* PIR + RTC + домен утримання */
        .battery_wh = 37.0,        /* Li-ion 10 А·год при 3.7 В */
        .edge_duty_cycle = 0.005   /* прокидаємось на 0.5 % часу */
    };
    print_report("1080p @ 30 fps, H.264, нічний режим", &cam_1080p);

    /* Профіль 2: та сама плата, але 4K — саме тут ламається шина. */
    video_config_t cam_4k = cam_1080p;
    cam_4k.width = 3840;
    cam_4k.height = 2160;
    cam_4k.codec = CODEC_H265_HEVC;
    cam_4k.vpu_w = 0.90; /* кодування 4K дорожче для VPU */
    print_report("4K @ 30 fps, H.265, нічний режим", &cam_4k);

    /* Профіль 3: сирий Bayer без кодека — показує, чому потік «просто в пам'ять»
     * не рятує: множник шини менший, зате бітрейт нічим не збити. */
    video_config_t cam_raw = cam_1080p;
    cam_raw.codec = CODEC_RAW_BAYER;
    print_report("1080p @ 30 fps, RAW Bayer без стиснення", &cam_raw);

    /* Профіль 4: типова помилка в специфікації — ІЧ-прожектор є, а ККД
     * забули заповнити. Без валідації тут вийшло б ділення на нуль
     * і «нескінченна» автономність у звіті. */
    video_config_t broken = cam_1080p;
    broken.ir_led_efficiency = 0.0;
    print_report("1080p, ІЧ без указаного ККД", &broken);

    return 0;
}
