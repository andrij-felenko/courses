#include "hud.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

void hud_init(Hud *h)
{
    memset(h, 0, sizeof(*h));
    h->state = SCREEN_CALM;
    h->pending = SCREEN_CALM;
}

bool hud_add(Hud *h, const char *label, WidgetTier tier,
             const MetricChannel *src, const char *note)
{
    if (h->count >= HUD_MAX_WIDGETS) {
        return false;
    }
    Widget *w = &h->widgets[h->count];
    w->label = label;
    w->tier = tier;
    w->src = src;
    w->note = note;
    h->last_seen[h->count] = SEV_NORMAL;
    h->count++;
    return true;
}

/* Застиглі дані — теж аномалія: цифра виглядає живою, а вона вже неправда. */
static AlertSeverity widget_severity(const Widget *w)
{
    if (w->src == NULL) {
        return SEV_NORMAL;
    }
    AlertSeverity s = w->src->severity;
    if (w->src->stale && s < SEV_WARNING) {
        s = SEV_WARNING;
    }
    return s;
}

static void note_alarm(Hud *h, uint32_t now_ms)
{
    h->alarm_log[h->alarm_head] = now_ms;
    h->alarm_head = (h->alarm_head + 1u) % HUD_ALARM_LOG;
    if (h->alarm_used < HUD_ALARM_LOG) {
        h->alarm_used++;
    }
}

static size_t alarms_in_window(const Hud *h, uint32_t now_ms)
{
    size_t n = 0;
    for (size_t i = 0; i < h->alarm_used; ++i) {
        uint32_t t = h->alarm_log[i];
        if ((uint32_t)(now_ms - t) <= HUD_FLOOD_WINDOW_MS) {
            n++;
        }
    }
    return n;
}

/* Стан падає вниз лише після витримки: аварійний екран, що клацає туди-сюди,
   гірший за постійний, бо кожне перемальовування маскує решту змін. */
static void advance_state(Hud *h, ScreenState target, uint32_t now_ms)
{
    if (target > h->state) {
        h->state = target;
        h->pending = target;
        h->pending_since_ms = now_ms;
        return;
    }
    if (target == h->state) {
        h->pending = target;
        h->pending_since_ms = now_ms;
        return;
    }
    if (h->pending != target) {
        h->pending = target;
        h->pending_since_ms = now_ms;
    } else if ((uint32_t)(now_ms - h->pending_since_ms) >= HUD_RELEASE_HOLD_MS) {
        h->state = target;
    }
}

static void format_value(const Widget *w, uint32_t now_ms, char *out, size_t cap)
{
    const MetricChannel *m = w->src;
    if (m == NULL) {
        snprintf(out, cap, "%s", w->note ? w->note : "—");
        return;
    }
    if (m->stale) {
        snprintf(out, cap, "%.1f %s  СТАРІ ДАНІ (%.0f с)", m->value, m->cfg.unit,
                 (float)metric_silence_ms(m, now_ms) / 1000.0f);
        return;
    }
    bool trending = m->cfg.max_drift_rate > 0.0f &&
                    m->drift_rate >= m->cfg.max_drift_rate * 0.5f &&
                    isfinite(m->seconds_to_limit);
    if (trending) {
        snprintf(out, cap, "%.1f %s  тренд %.3f %s/с  ліміт через %.0f с",
                 m->value, m->cfg.unit, m->drift_rate, m->cfg.unit, m->seconds_to_limit);
    } else {
        snprintf(out, cap, "%.1f %s", m->value, m->cfg.unit);
    }
}

static void format_banner(const Widget *w, uint32_t now_ms, char *out, size_t cap)
{
    const MetricChannel *m = w->src;
    if (m->stale) {
        snprintf(out, cap, "!  %s: ДАНІ ЗАСТИГЛИ %.0f с — показник на екрані вже неправда",
                 w->label, (float)metric_silence_ms(m, now_ms) / 1000.0f);
    } else if (m->severity == SEV_CRITICAL && m->seconds_to_limit > 0.0f &&
               isfinite(m->seconds_to_limit)) {
        snprintf(out, cap, "!! %s %.1f %s: ліміт %.1f %s через %.0f с",
                 w->label, m->value, m->cfg.unit, m->cfg.crit_limit, m->cfg.unit,
                 m->seconds_to_limit);
    } else if (m->severity == SEV_CRITICAL) {
        snprintf(out, cap, "!! %s %.1f %s: за критичним лімітом %.1f %s",
                 w->label, m->value, m->cfg.unit, m->cfg.crit_limit, m->cfg.unit);
    } else {
        snprintf(out, cap, "!  %s %.1f %s: прихований дрейф %.3f %s/с",
                 w->label, m->value, m->cfg.unit, m->drift_rate, m->cfg.unit);
    }
}

/* Сортування тривог: спершу критичні, серед рівних — ті, до чийого ліміту ближче. */
static void sort_alarms(const Hud *h, size_t *idx, size_t n)
{
    for (size_t i = 0; i + 1 < n; ++i) {
        size_t best = i;
        for (size_t j = i + 1; j < n; ++j) {
            AlertSeverity sj = widget_severity(&h->widgets[idx[j]]);
            AlertSeverity sb = widget_severity(&h->widgets[idx[best]]);
            if (sj > sb) {
                best = j;
            } else if (sj == sb) {
                const MetricChannel *mj = h->widgets[idx[j]].src;
                const MetricChannel *mb = h->widgets[idx[best]].src;
                if (mj->seconds_to_limit < mb->seconds_to_limit) {
                    best = j;
                }
            }
        }
        size_t tmp = idx[i];
        idx[i] = idx[best];
        idx[best] = tmp;
    }
}

void hud_render(Hud *h, uint32_t now_ms, HudFrame *out)
{
    memset(out, 0, sizeof(*out));

    AlertSeverity worst = SEV_NORMAL;
    size_t alarming[HUD_MAX_WIDGETS];
    size_t alarm_count = 0;

    /* 1. Фронти тривог: лавину робить поява нових алярмів, а не їхня наявність. */
    for (size_t i = 0; i < h->count; ++i) {
        AlertSeverity s = widget_severity(&h->widgets[i]);
        if (s > h->last_seen[i] && s >= SEV_WARNING) {
            note_alarm(h, now_ms);
        }
        h->last_seen[i] = s;
        if (s > worst) {
            worst = s;
        }
        if (s >= SEV_WARNING) {
            alarming[alarm_count++] = i;
        }
    }
    out->flood = alarms_in_window(h, now_ms) > HUD_FLOOD_LIMIT;

    /* 2. Стан екрана. */
    ScreenState target = (worst == SEV_CRITICAL) ? SCREEN_EMERGENCY
                       : (worst == SEV_WARNING)  ? SCREEN_CAUTION
                                                 : SCREEN_CALM;
    advance_state(h, target, now_ms);
    out->state = h->state;

    /* 3. Розхаращення: аварія забирає весь фовеальний бюджет собі. */
    for (size_t i = 0; i < h->count; ++i) {
        const Widget *w = &h->widgets[i];
        AlertSeverity s = widget_severity(w);
        WidgetView *v = &out->views[out->view_count++];

        v->label = w->label;
        v->ink = (s == SEV_CRITICAL) ? INK_RED : (s == SEV_WARNING) ? INK_AMBER : INK_GRAY;
        format_value(w, now_ms, v->text, sizeof(v->text));

        if (s >= SEV_WARNING || w->tier == TIER_CORE) {
            v->draw = DRAW_FULL;
        } else if (h->state == SCREEN_EMERGENCY) {
            v->draw = DRAW_HIDDEN;
            out->hidden_count++;
        } else if (h->state == SCREEN_CAUTION) {
            v->draw = DRAW_DIM;
        } else {
            v->draw = DRAW_FULL;
        }
    }

    /* 4. Банери: не більше трьох, решта — одним підсумковим рядком. */
    sort_alarms(h, alarming, alarm_count);
    for (size_t i = 0; i < alarm_count; ++i) {
        if (out->banner_count < HUD_MAX_BANNERS) {
            format_banner(&h->widgets[alarming[i]], now_ms,
                          out->banners[out->banner_count], sizeof(out->banners[0]));
            out->banner_count++;
        } else {
            out->banners_suppressed++;
        }
    }
}

const char *screen_state_name(ScreenState s)
{
    switch (s) {
    case SCREEN_EMERGENCY: return "АВАРІЯ";
    case SCREEN_CAUTION:   return "увага";
    default:               return "спокій";
    }
}

const char *ink_name(InkColor c)
{
    switch (c) {
    case INK_RED:   return "red";
    case INK_AMBER: return "amber";
    default:        return "gray";
    }
}
