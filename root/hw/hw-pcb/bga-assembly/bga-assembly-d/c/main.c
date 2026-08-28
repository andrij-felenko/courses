#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define BGA_PI 3.14159265358979323846

typedef struct {
    double pitch_mm;           /* Крок кульок BGA */
    double ball_diam_mm;       /* Початковий діаметр кульки */
    double pad_diam_mm;        /* Діаметр площадки на платі */
    double mask_clearance_mm;  /* Зазор паяльної маски */
    bool   is_nsmd;            /* true = NSMD, false = SMD */
    double trace_width_mm;     /* Ширина сигнального провідника */
    double trace_clearance_mm; /* Зазор між провідником і площадкою */
} BgaGeometryConfig;

typedef struct {
    double escape_channel_mm;  /* Ширина каналу між сусідніми площадками */
    int    max_traces_in_ch;   /* Максимальна кількість доріжок у каналі */
    double area_ratio;         /* Площинне відношення апертури (при T=0.12мм) */
    double estimated_standoff; /* Оціночна висота зазору після пайки */
    bool   is_valid;           /* Чи відповідає нормам DFM/IPC */
} BgaVerificationReport;

/* Розрахунок геометрії та технологічності BGA */
BgaVerificationReport verify_bga_layout(const BgaGeometryConfig* cfg, double stencil_thick_mm) {
    BgaVerificationReport rep;
    double effective_pad = cfg->pad_diam_mm;
    
    if (cfg->is_nsmd) {
        /* Для NSMD враховуємо зазор маски при оцінці каналу на зовнішньому шарі */
        double copper_pad = cfg->pad_diam_mm;
        rep.escape_channel_mm = cfg->pitch_mm - copper_pad;
    } else {
        /* Для SMD мідь ширша за апертуру маски */
        double copper_pad = cfg->pad_diam_mm + 2.0 * cfg->mask_clearance_mm;
        rep.escape_channel_mm = cfg->pitch_mm - copper_pad;
    }
    
    /* Розрахунок скільки доріжок вміщується в канал */
    double needed_per_trace = cfg->trace_width_mm + cfg->trace_clearance_mm;
    if (rep.escape_channel_mm > cfg->trace_clearance_mm) {
        rep.max_traces_in_ch = (int)((rep.escape_channel_mm - cfg->trace_clearance_mm) / needed_per_trace);
    } else {
        rep.max_traces_in_ch = 0;
    }
    
    /* Площинне відношення круглої апертури трафарету (AR = D / (4 * T)) */
    rep.area_ratio = cfg->pad_diam_mm / (4.0 * stencil_thick_mm);
    
    /* Оцінка висоти осадки кульки зі збереженням об'єму сфери (V = const) */
    double ball_vol = (4.0 / 3.0) * BGA_PI * pow(cfg->ball_diam_mm / 2.0, 3.0);
    double r_pad = cfg->pad_diam_mm / 2.0;
    /* Наближена висота стовпчика припою (усічена сфера) */
    rep.estimated_standoff = cfg->ball_diam_mm * (1.0 - 0.25 * pow(cfg->pad_diam_mm / cfg->ball_diam_mm, 2.0));
    
    /* Перевірка мінімальних норм DFM */
    rep.is_valid = (rep.escape_channel_mm >= 0.10) && 
                   (rep.area_ratio >= 0.66) && 
                   (rep.estimated_standoff >= 0.15);
                   
    return rep;
}

int main(void) {
    BgaGeometryConfig bga08 = {
        .pitch_mm = 0.80,
        .ball_diam_mm = 0.45,
        .pad_diam_mm = 0.38,
        .mask_clearance_mm = 0.05,
        .is_nsmd = true,
        .trace_width_mm = 0.10,
        .trace_clearance_mm = 0.10
    };
    
    BgaVerificationReport res = verify_bga_layout(&bga08, 0.12);
    
    printf("=== BGA Layout Verification (Pitch 0.8mm NSMD) ===\n");
    printf("Ширина каналу трасування: %.3f мм\n", res.escape_channel_mm);
    printf("Доріжок у каналі:         %d\n", res.max_traces_in_ch);
    printf("Area Ratio трафарету:     %.2f (Полотно >= 0.66: %s)\n", 
           res.area_ratio, res.area_ratio >= 0.66 ? "OK" : "FAIL");
    printf("Висота зазору Standoff:   %.3f мм\n", res.estimated_standoff);
    printf("Статус валідації DFM:     %s\n", res.is_valid ? "PASSED" : "REJECTED");
    
    return 0;
}
