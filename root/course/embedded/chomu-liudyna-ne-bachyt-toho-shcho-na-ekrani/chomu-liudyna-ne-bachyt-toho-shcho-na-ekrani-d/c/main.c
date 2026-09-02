#include <math.h>
#include <stdio.h>

#include "hud.h"

/* Модель польоту з зав'язки статті: 40 хвилин, батарея тихо сповзає
   з 22.2 В до 13.8 В — 3.7 мВ/с, тобто нижче будь-якого порогу сітківки. */
#define FLIGHT_S 2400u

static float battery_voltage(uint32_t t)
{
    if (t < 120u) {
        return 22.2f;
    }
    float k = (float)(t - 120u) / (float)(FLIGHT_S - 120u);
    if (k > 1.0f) {
        k = 1.0f;
    }
    return 22.2f - 8.4f * k;
}

static bool brownout(uint32_t t)
{
    return battery_voltage(t) < 14.5f;   /* просідання DC-DC тягне за собою решту */
}

static float esc_temp(uint32_t t)
{
    return brownout(t) ? 128.0f : 46.0f + 0.004f * (float)t;
}

static float link_rssi(uint32_t t)
{
    if (t >= 1500u && t <= 1506u) {
        return NAN;              /* побиті кадри: значення в пакеті сміття */
    }
    if (brownout(t)) {
        return -97.0f;
    }
    return -62.0f + (float)((t * 37u) % 7u) * 0.3f;
}

static float gps_hdop(uint32_t t)
{
    return brownout(t) ? 6.4f : 0.9f + (float)((t * 13u) % 5u) * 0.05f;
}

static void print_frame(uint32_t t, const HudFrame *f)
{
    printf("\n== t=%02u:%02u  екран: %s ==\n", t / 60u, t % 60u, screen_state_name(f->state));
    for (size_t i = 0; i < f->banner_count; ++i) {
        printf("   %s\n", f->banners[i]);
    }
    if (f->banners_suppressed > 0) {
        printf("   ... ще %zu тривог згорнуто%s\n", f->banners_suppressed,
               f->flood ? "  [ЛАВИНА ТРИВОГ, EEMUA 191]" : "");
    }
    for (size_t i = 0; i < f->view_count; ++i) {
        const WidgetView *v = &f->views[i];
        if (v->draw == DRAW_HIDDEN) {
            continue;
        }
        printf("   %-7s %-5s %s%s\n", v->label, ink_name(v->ink), v->text,
               v->draw == DRAW_DIM ? "   (приглушено)" : "");
    }
    if (f->hidden_count > 0) {
        printf("   [%zu другорядних віджетів прибрано з екрана]\n", f->hidden_count);
    }
}

int main(void)
{
    MetricConfig batt_cfg = {
        .name = "BATT", .unit = "V", .direction = METRIC_FALLING,
        .warn_limit = 18.0f, .crit_limit = 14.0f,
        .max_drift_rate = 0.002f, .hysteresis = 0.4f, .stale_after_ms = 3000u
    };
    MetricConfig esc_cfg = {
        .name = "ESC T", .unit = "C", .direction = METRIC_RISING,
        .warn_limit = 80.0f, .crit_limit = 95.0f,
        .max_drift_rate = 0.05f, .hysteresis = 3.0f, .stale_after_ms = 3000u
    };
    MetricConfig link_cfg = {
        .name = "LINK", .unit = "dBm", .direction = METRIC_FALLING,
        .warn_limit = -85.0f, .crit_limit = -95.0f,
        .max_drift_rate = 0.0f, .hysteresis = 3.0f, .stale_after_ms = 3000u
    };
    MetricConfig hdop_cfg = {
        .name = "HDOP", .unit = "", .direction = METRIC_RISING,
        .warn_limit = 2.0f, .crit_limit = 4.0f,
        .max_drift_rate = 0.0f, .hysteresis = 0.3f, .stale_after_ms = 3000u
    };

    MetricChannel batt, esc, link, hdop;
    metric_init(&batt, &batt_cfg);
    metric_init(&esc, &esc_cfg);
    metric_init(&link, &link_cfg);
    metric_init(&hdop, &hdop_cfg);

    Hud hud;
    hud_init(&hud);

    bool ok = true;
    ok &= hud_add(&hud, "BATT", TIER_CORE, &batt, NULL);
    ok &= hud_add(&hud, "LINK", TIER_CORE, &link, NULL);
    ok &= hud_add(&hud, "MODE", TIER_CORE, NULL, "AUTO");
    ok &= hud_add(&hud, "ESC T", TIER_SECONDARY, &esc, NULL);
    ok &= hud_add(&hud, "HDOP", TIER_SECONDARY, &hdop, NULL);
    ok &= hud_add(&hud, "FW", TIER_SECONDARY, NULL, "v4.3.1-rc2");
    ok &= hud_add(&hud, "PKT RX", TIER_SECONDARY, NULL, "312481");
    if (!ok) {
        fprintf(stderr, "HUD переповнено: збільште HUD_MAX_WIDGETS\n");
        return 1;
    }

    ScreenState prev = SCREEN_CALM;
    for (uint32_t t = 0; t <= FLIGHT_S; ++t) {
        uint32_t now = t * 1000u;

        metric_update(&batt, battery_voltage(t), now);
        metric_update(&esc, esc_temp(t), now);
        metric_update(&link, link_rssi(t), now);   /* NaN відкидається сам */
        if (t < 2000u) {
            metric_update(&hdop, gps_hdop(t), now); /* далі GPS-модуль замовкає */
        }

        metric_tick(&batt, now);
        metric_tick(&esc, now);
        metric_tick(&link, now);
        metric_tick(&hdop, now);

        HudFrame frame;
        hud_render(&hud, now, &frame);

        if (frame.state != prev || t % 300u == 0u) {
            print_frame(t, &frame);
            prev = frame.state;
        }
    }
    return 0;
}
