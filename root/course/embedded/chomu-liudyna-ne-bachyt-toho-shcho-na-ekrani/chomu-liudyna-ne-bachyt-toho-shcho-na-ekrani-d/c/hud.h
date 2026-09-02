#ifndef HUD_H
#define HUD_H

#include <stddef.h>

#include "metric.h"

/* Стан екрана за принципом темної кабіни: у спокої екран мовчить сірим. */
typedef enum {
    SCREEN_CALM = 0,
    SCREEN_CAUTION,
    SCREEN_EMERGENCY
} ScreenState;

/* Незнищенне ядро (стан, режим, зв'язок, здоров'я) не ховається ніколи. */
typedef enum {
    TIER_CORE = 0,
    TIER_SECONDARY
} WidgetTier;

typedef enum {
    DRAW_FULL = 0,
    DRAW_DIM,
    DRAW_HIDDEN
} DrawMode;

typedef enum {
    INK_GRAY = 0,
    INK_AMBER,
    INK_RED
} InkColor;

#define HUD_MAX_WIDGETS       16
#define HUD_MAX_BANNERS       3        /* більше трьох банерів людина не читає */
#define HUD_ALARM_LOG         32
#define HUD_FLOOD_WINDOW_MS   (10u * 60u * 1000u)  /* EEMUA 191: вікно 10 хвилин */
#define HUD_FLOOD_LIMIT       10                   /* EEMUA 191: понад 10 — лавина */
#define HUD_RELEASE_HOLD_MS   5000u                /* латч перед пониженням стану */

typedef struct {
    const char *label;
    WidgetTier tier;
    const MetricChannel *src;   /* NULL — статичний напис (режим, версія, лічильник) */
    const char *note;
} Widget;

typedef struct {
    const char *label;
    DrawMode draw;
    InkColor ink;
    char text[64];
} WidgetView;

typedef struct {
    ScreenState state;
    WidgetView views[HUD_MAX_WIDGETS];
    size_t view_count;
    size_t hidden_count;
    char banners[HUD_MAX_BANNERS][96];
    size_t banner_count;
    size_t banners_suppressed;  /* згорнуті в підсумковий рядок тривоги */
    bool flood;
} HudFrame;

typedef struct {
    Widget widgets[HUD_MAX_WIDGETS];
    AlertSeverity last_seen[HUD_MAX_WIDGETS];
    size_t count;

    ScreenState state;
    ScreenState pending;
    uint32_t pending_since_ms;

    uint32_t alarm_log[HUD_ALARM_LOG];  /* кільце міток появи тривог */
    size_t alarm_head;
    size_t alarm_used;
} Hud;

void hud_init(Hud *h);
bool hud_add(Hud *h, const char *label, WidgetTier tier,
             const MetricChannel *src, const char *note);
void hud_render(Hud *h, uint32_t now_ms, HudFrame *out);

const char *screen_state_name(ScreenState s);
const char *ink_name(InkColor c);

#endif /* HUD_H */
