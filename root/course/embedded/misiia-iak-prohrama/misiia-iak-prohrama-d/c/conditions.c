#include "conditions.h"

#include <math.h>

void condition_arm(condition_t *c, cond_kind_t kind, float p1, float p2,
                   const cond_ctx_t *ctx)
{
    c->kind     = kind;
    c->armed    = true;
    c->start_ms = ctx->now_ms;

    switch (kind) {
        case COND_DELAY:
            c->duration_ms = (p1 > 0.0f) ? (uint32_t)(p1 * 1000.0f) : 0u;
            break;

        case COND_DISTANCE:
            c->trigger_dist_m = (p1 > 0.0f) ? p1 : 0.0f;
            break;

        case COND_YAW:
            c->target_yaw_deg = geo_norm_heading_deg(p1);
            c->start_yaw_deg  = ctx->yaw_deg;
            c->yaw_rate_dps   = (p2 > 0.0f) ? p2 : COND_YAW_DEFAULT_DPS;
            break;

        case COND_NONE:
        default:
            c->armed = false;
            break;
    }
}

bool condition_met(const condition_t *c, const cond_ctx_t *ctx)
{
    switch (c->kind) {
        case COND_DELAY:
            /* Різниця беззнакових: коректна й тоді, коли 32-бітний
               лічильник мілісекунд переповнився (кожні 49.7 доби). */
            return (uint32_t)(ctx->now_ms - c->start_ms) >= c->duration_ms;

        case COND_DISTANCE: {
            /* Порівнюємо квадрати — sqrtf() у такті 50 Гц зайвий. */
            const float trig2 = c->trigger_dist_m * c->trigger_dist_m;
            return geo_dist_sq_m2(ctx->position, ctx->next_waypoint) <= trig2;
        }

        case COND_YAW:
            return fabsf(geo_wrap_deg(ctx->yaw_deg - c->target_yaw_deg))
                   <= COND_YAW_TOLERANCE_DEG;

        case COND_NONE:
        default:
            return true;
    }
}

float condition_yaw_setpoint(const condition_t *c, const cond_ctx_t *ctx)
{
    if (c->kind != COND_YAW) {
        return -1.0f;
    }

    /* Найкоротший шлях до цілі: нормалізація вирішує, куди крутити. */
    const float full_deg  = geo_wrap_deg(c->target_yaw_deg - c->start_yaw_deg);
    const float elapsed_s = (float)(uint32_t)(ctx->now_ms - c->start_ms) / 1000.0f;
    const float done_deg  = c->yaw_rate_dps * elapsed_s;

    if (done_deg >= fabsf(full_deg)) {
        return c->target_yaw_deg;
    }
    return geo_norm_heading_deg(c->start_yaw_deg + copysignf(done_deg, full_deg));
}

void battery_filter_init(battery_filter_t *f, float tau_s)
{
    f->value_v = 0.0f;
    f->tau_s   = (tau_s > 0.0f) ? tau_s : 3.0f;
    f->primed  = false;
}

float battery_filter_update(battery_filter_t *f, float raw_v, float dt_s)
{
    if (!f->primed) {
        /* Перше читання беремо як є — інакше фільтр повзе з нуля
           й перші секунди польоту вважає батарею розрядженою. */
        f->value_v = raw_v;
        f->primed  = true;
        return f->value_v;
    }
    if (dt_s <= 0.0f) {
        return f->value_v;
    }

    const float alpha = dt_s / (f->tau_s + dt_s);
    f->value_v += alpha * (raw_v - f->value_v);
    return f->value_v;
}
