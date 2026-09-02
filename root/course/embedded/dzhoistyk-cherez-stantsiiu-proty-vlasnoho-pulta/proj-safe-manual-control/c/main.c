#include "arbiter.h"
#include "gcs_link.h"
#include "mavlink_frame.h"

#include <stdio.h>
#include <string.h>

/* Стенд на 3.4 секунди модельного часу. Контур стабілізації крутиться 400 Гц,
 * джойстик станції шле MANUAL_CONTROL 50 Гц, серцебиття йде 1 Гц.
 * Сценарій відтворює саме той політ, з якого починається стаття. */

#define TICK_US   2500u      /* 400 Гц */
#define OUR_SYSID 1u
#define GCS_SYSID 255u
#define ROGUE_SYSID 250u

static uint8_t g_tx[1024];
static size_t  g_tx_len;
static uint8_t g_seq_gcs, g_seq_rogue;

static void tx_push(uint8_t sysid, uint8_t *seq, uint32_t msgid,
                    const uint8_t *payload, uint8_t len)
{
    size_t n = mav_encode(g_tx + g_tx_len, sizeof(g_tx) - g_tx_len,
                          sysid, MAV_COMP_ID_MISSIONPLANNER, (*seq)++, msgid, payload, len);
    g_tx_len += n;
}

static void send_manual(uint8_t sysid, uint8_t *seq, int16_t x, int16_t y, int16_t z, int16_t r)
{
    mav_manual_control_t mc;
    uint8_t payload[11];

    memset(&mc, 0, sizeof(mc));
    mc.x = x; mc.y = y; mc.z = z; mc.r = r;
    mc.target = OUR_SYSID;
    tx_push(sysid, seq, MAV_MSG_MANUAL_CONTROL, payload, mav_pack_manual_control(payload, &mc));
}

static void send_heartbeat(void)
{
    mav_heartbeat_t hb;
    uint8_t payload[9];

    memset(&hb, 0, sizeof(hb));
    hb.type = 6;             /* MAV_TYPE_GCS */
    hb.autopilot = 8;        /* MAV_AUTOPILOT_INVALID — так робить станція */
    hb.system_status = 4;    /* MAV_STATE_ACTIVE */
    hb.mavlink_version = 3;
    tx_push(GCS_SYSID, &g_seq_gcs, MAV_MSG_HEARTBEAT, payload, mav_pack_heartbeat(payload, &hb));
}

static void send_arm(bool arm, uint8_t confirmation)
{
    mav_command_long_t cl;
    uint8_t payload[33];

    memset(&cl, 0, sizeof(cl));
    cl.command          = MAV_CMD_COMPONENT_ARM_DISARM;
    cl.param[0]         = arm ? 1.0f : 0.0f;
    cl.target_system    = OUR_SYSID;
    cl.target_component = MAV_COMP_ID_AUTOPILOT1;
    cl.confirmation     = confirmation;
    tx_push(GCS_SYSID, &g_seq_gcs, MAV_MSG_COMMAND_LONG, payload, mav_pack_command_long(payload, &cl));
}

/* Розклад подій радіолінії на модельний момент t (мс). */
static void simulate_gcs(uint32_t t)
{
    static uint32_t next_manual = 0;
    static uint32_t next_hb = 0;
    static bool arm_sent0, arm_sent1, rogue_sent, disarm_sent;

    if (t >= next_hb) {                 /* серцебиття йде завжди, навіть коли */
        send_heartbeat();               /* вікно джойстика вже не відповідає */
        next_hb += 1000u;
    }

    if (t == 100u && !arm_sent0) { send_arm(true, 0); arm_sent0 = true; }
    if (t == 200u && !arm_sent1) { send_arm(true, 1); arm_sent1 = true; }
    if (t >= 3200u && !disarm_sent) { send_arm(false, 1); disarm_sent = true; }

    if (t >= 800u && t < 820u && !rogue_sent) {
        /* Друга станція на тому ж модемі шле повний крен. */
        send_manual(ROGUE_SYSID, &g_seq_rogue, 0, 1000, 500, 0);
        rogue_sent = true;
    }

    if (t >= 900u && t < 2900u) {
        /* Вікно введення джойстика зависло: черга в ОС НЕ росте, слати нічого. */
        next_manual = t + 20u;
        return;
    }
    if (t >= 520u && t < 700u) {
        /* Сплеск DPC-затримки: драйвер USB-UART тримає буфер, пакети чекають
         * у черзі — і вистрілять пачкою, коли ОС нарешті віддасть керування. */
        return;
    }

    while (t >= next_manual) {
        /* До 700 мс — крейсерський тангаж уперед; далі оператор уже відхилив
         * стік назад на екстрене гальмування. */
        int16_t x = (next_manual >= 640u) ? -1000 : 400;
        send_manual(GCS_SYSID, &g_seq_gcs, x, 0, 500, 0);
        next_manual += 20u;
    }
}

/* Фізичний пульт: 50 Гц, живий на початку і з 2050 мс. */
static void simulate_rc(uint32_t t, arbiter_t *arb)
{
    static uint32_t next_rc = 0;
    control_axes_t rc;

    if (t < next_rc)
        return;
    next_rc += 20u;

    if (t >= 400u && t < 2050u)
        return; /* пульт поза межею дальності — кадрів CRSF немає */

    memset(&rc, 0, sizeof(rc));
    if (t >= 2100u && t < 2500u)
        rc.pitch = -600; /* пілот безпеки взяв керування на себе */
    arbiter_feed_rc(arb, &rc, t);
}

int main(void)
{
    arbiter_t arb;
    gcs_link_t link;
    uint32_t t_us = 0;
    arbiter_state_t prev_state = ARB_RC_ACTIVE; /* завідомо інший, щоб перший рядок надрукувався */
    failsafe_action_t prev_fs = FS_RTL;
    bool prev_armed = true;

    arbiter_init(&arb);
    arbiter_set_home_available(&arb, true); /* фікс є, домашня точка записана */
    gcs_link_init(&link, OUR_SYSID, MAV_COMP_ID_AUTOPILOT1);

    printf("  час  стан          FS   armed  roll pitch  yaw thr\n");

    for (; t_us <= 3400000u; t_us += TICK_US) {
        const uint32_t t = t_us / 1000u;
        const uint8_t *ack;
        size_t ack_len;

        /* 1. Радіолінія: байти з UART радіомодема. */
        g_tx_len = 0;
        simulate_gcs(t);
        if (g_tx_len)
            gcs_link_feed(&link, g_tx, g_tx_len, t, &arb);

        /* 2. Кадри прямого пульта. */
        simulate_rc(t, &arb);

        /* 3. Контур стабілізації — рівний такт, незалежний від приходу пакетів. */
        arbiter_update(&arb, t, (float)TICK_US / 1000000.0f);

        if (gcs_link_take_ack(&link, &ack, &ack_len))
            printf("%5u  -> COMMAND_ACK, %zu байт у модем\n", t, ack_len);

        if (arb.state != prev_state || arb.failsafe != prev_fs || arb.armed != prev_armed) {
            printf("%5u  %-12s  %-4s %-5s  %5d %5d %4d %4d\n",
                   t, arbiter_state_name(arb.state), arbiter_failsafe_name(arb.failsafe),
                   arb.armed ? "так" : "ні",
                   arb.out.roll, arb.out.pitch, arb.out.yaw, arb.out.throttle);
            prev_state = arb.state;
            prev_fs    = arb.failsafe;
            prev_armed = arb.armed;
        }

        /* Вікно, де видно роботу лімітера: пачка після провалу DPC. */
        if (t >= 700u && t < 900u && (t % 40u) == 0u && (t_us % 1000u) == 0u)
            printf("%5u  ...           -    -      %5d %5d %4d %4d  (ціль тангажа %d)\n",
                   t, arb.out.roll, arb.out.pitch, arb.out.yaw, arb.out.throttle, arb.gcs.pitch);
    }

    printf("\nпідсумок:\n");
    printf("  кадрів прийнято      %u (CRC-помилок %u, поза діалектом %u)\n",
           link.parser.stat_ok, link.parser.stat_crc_err, link.parser.stat_unknown);
    printf("  MANUAL_CONTROL       %u, HEARTBEAT %u, команд арму %u\n",
           link.n_manual, link.n_heartbeat, link.n_arm_cmd);
    printf("  чужа станція         %u пакетів відкинуто, не наша адреса %u\n",
           link.n_foreign, link.n_wrong_target);
    printf("  перехоплень пультом  %u, деградацій %u, аварійних режимів %u\n",
           arb.preempt_events, arb.degrade_events, arb.failsafe_events);
    return 0;
}
