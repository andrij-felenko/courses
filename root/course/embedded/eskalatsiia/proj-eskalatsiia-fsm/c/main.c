/* Прогін автомата на сцені зі статті: ровер 350 кг, 4 м/с, силует за 20 м.
   Модель руху груба навмисно — предмет тут автомат, а не динаміка платформи. */
#include "escalation.h"

#include <stdio.h>
#include <string.h>

#define TICK_MS        20u      /* петля керування 50 Гц */
#define OBSTACLE_X_M   60.0f
#define DETECT_RANGE_M 20.0f

/* Планувальник знайшов лише два виходи: вузький об'їзд праворуч і зупинку */
static const EscOption PLANNER_OPTIONS[2] = {
    { 1, "Обхід праворуч", 6.5f, 0.35f },
    { 2, "Зупинка",        0.0f, 0.05f },
};

typedef struct {
    float    x;                 /* позиція вздовж проїзду, метри */
    float    speed;
    uint32_t now_ms;
    uint32_t last_heartbeat_ms;
    bool     link;
} Sim;

static void step_motion(Sim* s, const EscOutputs* out)
{
    const float dt = (float)TICK_MS / 1000.0f;
    float target = 0.0f;
    switch (out->command) {
        case ESC_CMD_CONTINUE:       target =  4.0f; break;
        case ESC_CMD_FOLLOW_OPTION:  target =  2.0f; break;  /* об'їзд повільніше */
        case ESC_CMD_GOTO_POINT:     target = -1.5f; break;  /* реверс по слідах */
        default:                     target =  0.0f; break;
    }
    float dv = target - s->speed;
    const float lim = 2.0f * dt;                 /* ±2 м/с² */
    if (dv >  lim) dv =  lim;
    if (dv < -lim) dv = -lim;
    s->speed += dv;
    s->x     += s->speed * dt;
}

/* Те, що бачить оператор: станція розбирає кадр і показує варіанти */
static void gcs_show(const uint8_t* frame, size_t len)
{
    EscQuery q;
    const EscWireErr err = esc_unpack_query(frame, len, &q);
    if (err != ESC_WIRE_OK) {
        printf("  [GCS] кадр не розібрано: %s\n", esc_wire_err_str(err));
        return;
    }
    printf("  [GCS] %zu Б у ефірі: запит #%u, тригер %u, дедлайн %u мс%s\n",
           len, (unsigned)q.query_id, (unsigned)q.trigger_code, (unsigned)q.deadline_ms,
           (q.flags & ESC_FLAG_ROI_DROPPED) ? ", мініатюру відкинуто" : "");
    for (uint8_t i = 0; i < q.options_count; ++i) {
        printf("        [%u] %s  +%.1f м, ризик %.2f\n",
               (unsigned)q.options[i].option_id, q.options[i].description,
               (double)q.options[i].estimated_cost_detour_m, (double)q.options[i].risk_score);
    }
}

static void run(const char* title, bool operator_answers, uint32_t answer_delay_ms, bool link_dies)
{
    printf("\n=== %s ===\n", title);

    EscManager mgr;
    esc_init(&mgr, 1500u);

    Sim sim = { 0.0f, 4.0f, 0u, 0u, true };
    uint8_t roi[96];
    memset(roi, 0xA5, sizeof roi);      /* умовна мініатюра спірної ділянки кадру */

    EscState  shown        = mgr.state;
    bool      query_sent   = false;
    uint32_t  reply_due_ms = 0u;
    bool      reply_done   = false;

    for (uint32_t tick = 0; tick < 3000u; ++tick) {
        sim.now_ms = tick * TICK_MS;
        if (sim.link) sim.last_heartbeat_ms = sim.now_ms;

        const float dist = OBSTACLE_X_M - sim.x;

        EscInputs in;
        memset(&in, 0, sizeof in);
        in.now_ms             = sim.now_ms;
        in.dist_to_obstacle_m = dist;
        in.speed_mps          = sim.speed;
        in.pose.x             = sim.x;
        in.pose.timestamp_ms  = sim.now_ms;
        in.pose.rssi_dbm      = sim.link ? -78 : -110;
        in.last_heartbeat_ms  = sim.last_heartbeat_ms;
        if (!query_sent && dist <= DETECT_RANGE_M) {
            in.trigger       = ESC_TRIGGER_BORDERLINE_CRITICAL;  /* 49% мішок / 51% людина */
            in.options       = PLANNER_OPTIONS;
            in.options_count = 2u;
            in.roi_jpeg      = roi;
            in.roi_len       = (uint16_t)sizeof roi;
        }
        /* Об'їзд вважаємо завершеним, коли ровер проминув перешкоду */
        in.maneuver_done = (sim.x > OBSTACLE_X_M + 3.0f);

        EscOutputs out;
        esc_tick(&mgr, &in, &out);

        if (mgr.state != shown) {
            printf("[%6u мс] %s -> %s (x=%.1f м, v=%.2f м/с, слідів %u)\n",
                   (unsigned)sim.now_ms, esc_state_str(shown), esc_state_str(mgr.state),
                   (double)sim.x, (double)sim.speed, (unsigned)esc_trail_count(&mgr.trail));
            shown = mgr.state;
        }
        if (out.frame_len > 0u) {
            query_sent   = true;
            reply_due_ms = sim.now_ms + answer_delay_ms;
            gcs_show(out.frame, out.frame_len);
            if (link_dies) {
                sim.link = false;       /* радіо вмирає одразу після відправлення */
                printf("  [радіо] HEARTBEAT зник\n");
            }
        }
        if (out.persist_incident) {
            printf("  [NVRAM] інцидент #%u записано, мотори знеструмлено\n",
                   (unsigned)mgr.query_id);
        }

        /* Оператор натискає кнопку: станція шле відповідь тим самим протоколом */
        if (operator_answers && query_sent && !reply_done && sim.now_ms >= reply_due_ms) {
            reply_done = true;
            const EscReply rep = { mgr.query_id, 1u, sim.now_ms };
            uint8_t frame[16];
            size_t  len = 0u;
            if (esc_pack_reply(&rep, frame, sizeof frame, &len) == ESC_WIRE_OK) {
                const EscReplyVerdict v = escalation_manager_handle_response(&mgr, frame, len, sim.now_ms);
                printf("  [оператор] опція 1 на %u мс: %s\n",
                       (unsigned)(sim.now_ms - mgr.request_started_ms), esc_verdict_str(v));
            }
        }

        step_motion(&sim, &out);
        if (mgr.state == FSM_STATE_FAILSAFE_SAFE_ABORT && sim.speed == 0.0f) break;
        if (mgr.state == FSM_STATE_AUTONOMOUS && query_sent && sim.x > OBSTACLE_X_M + 5.0f) break;
    }
}

int main(void)
{
    run("Оператор відповів вчасно", true, 900u, false);
    run("Оператор спізнився на 200 мс після дедлайну", true, 4200u, false);
    run("Радіо мовчить: HOLD -> BACKTRACK -> SAFE_ABORT", false, 0u, true);
    return 0;
}
