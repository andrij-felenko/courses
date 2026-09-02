#include <stdio.h>

#include "dispatcher.h"

#define SIM_STEPS 10
#define SIM_DT_S 1.0f
#define MAX_SPEED_MPS 15.0f  /* маршова швидкість апарата */
#define SENSOR_RANGE_M 25.0f /* далі перешкода виходить з поля зору далекоміра */

/* Груба модель апарата: за такт він проходить у бік заданої точки не більше
   MAX_SPEED_MPS * dt метрів. Регулятора й планувальника траєкторії тут немає —
   нас цікавить лише те, які цілі диспетчер вмикає і коли. */
static void plant_advance(VehicleTelemetry_t *telem, const DispatcherOutput_t *cmd, float dt_s) {
    if (cmd->mode != OUTPUT_TRACK) {
        return;  /* IDLE/HOLD/LAND — апарат тримає поточну позицію */
    }

    const float dist = goal_distance(cmd->x, cmd->y, cmd->z,
                                     telem->pos_x, telem->pos_y, telem->pos_z);
    if (dist < 1e-3f) {
        return;
    }

    const float span = MAX_SPEED_MPS * dt_s;
    const float k = (span < dist) ? (span / dist) : 1.0f;
    telem->pos_x += (cmd->x - telem->pos_x) * k;
    telem->pos_y += (cmd->y - telem->pos_y) * k;
    telem->pos_z += (cmd->z - telem->pos_z) * k;

    telem->battery_v -= 0.05f * dt_s;  /* політ їсть заряд */
}

/* Другий бік мосту: потік телеметрії забирає події й пакує їх у MAVLink.
   Тут замість пакувальника — друк, решта поведінки та сама. */
static void drain_outbox(MissionOutbox_t *box, float t_s) {
    MissionEvent_t ev;
    while (outbox_pop(box, &ev)) {
        printf("  t=%4.1f с | ціль #%-4u %-9s | MAVLink msg %2u, result %2u | точка [%.1f, %.1f, %.1f]\n",
               (double)t_s, ev.goal_id, goal_state_name(ev.state),
               (unsigned)ev.msg_id, (unsigned)ev.result,
               (double)ev.x, (double)ev.y, (double)ev.z);
    }
}

int main(void) {
    MissionOutbox_t outbox;
    outbox_init(&outbox);

    MissionDispatcher_t dispatcher;
    mission_dispatcher_init(&dispatcher, &outbox);

    VehicleTelemetry_t telemetry = {
        .pos_x = 0.0f,
        .pos_y = 0.0f,
        .pos_z = -10.0f,
        .battery_v = 24.2f,
        .geofence_valid = true,
        .ekf_healthy = true,
        .obstacle_detected = false
    };

    const GoalItem_t survey_goal = {
        .id = 101,
        .action = GOAL_SURVEY_POLYGON,
        .priority = 50,
        .target_x = 100.0f,
        .target_y = 50.0f,
        .target_z = -50.0f,
        .tolerance_m = 3.0f,
        .timeout_s = 60.0f
    };

    if (!mission_dispatcher_enqueue(&dispatcher, &survey_goal)) {
        fprintf(stderr, "черга цілей повна вже на старті — місію не завантажено\n");
        return 1;
    }

    printf("=== СИМУЛЯЦІЯ АВТОНОМНОГО ДИСПЕТЧЕРА ===\n");

    /* Точка, де далекомір побачив перешкоду: доки апарат від неї не відійшов,
       давач продовжує її бачити. */
    float det_x = 0.0f, det_y = 0.0f, det_z = 0.0f;
    bool detection_live = false;
    float t_s = 0.0f;

    for (int step = 0; step < SIM_STEPS; step++, t_s += SIM_DT_S) {
        if (step == 3) {
            printf("\n--- ПОДІЯ: далекомір бачить перешкоду на курсі ---\n");
            telemetry.obstacle_detected = true;
            detection_live = true;
            det_x = telemetry.pos_x;
            det_y = telemetry.pos_y;
            det_z = telemetry.pos_z;
        }

        const DispatcherOutput_t cmd = mission_dispatcher_step(&dispatcher, &telemetry, SIM_DT_S);
        drain_outbox(&outbox, t_s);
        plant_advance(&telemetry, &cmd, SIM_DT_S);

        if (detection_live &&
            goal_distance(telemetry.pos_x, telemetry.pos_y, telemetry.pos_z,
                          det_x, det_y, det_z) > SENSOR_RANGE_M) {
            /* Маневр відпрацьовано: перешкода вийшла з поля зору давача. */
            telemetry.obstacle_detected = false;
            detection_live = false;
        }
    }

    printf("\nПідсумок: #101 %s, #9999 %s, подій загублено: %u\n",
           goal_state_name(mission_dispatcher_state_of(&dispatcher, 101)),
           goal_state_name(mission_dispatcher_state_of(&dispatcher, 9999)),
           (unsigned)outbox_dropped(&outbox));
    return 0;
}
