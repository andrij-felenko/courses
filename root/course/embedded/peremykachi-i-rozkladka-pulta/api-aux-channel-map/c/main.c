#include <stdio.h>
#include <string.h>

#include "arming.h"
#include "aux_switch.h"
#include "crsf.h"
#include "rc_channels.h"
#include "sbus.h"

/* Сценарій з теми: передавач шле канали в порядку TAER, а польотний
   контролер налаштований на AETR. Пілот рухає стік тангажу — контролер
   бачить газ. Далі — втрата лінку й поведінка приймача. */

#define FRAME_PERIOD_MS     4U     /* 250 Гц, типово для ExpressLRS */
#define FAILSAFE_TIMEOUT_MS 100U
#define ARM_CHANNEL_INDEX   RC_AUX_INDEX(1)  /* AUX1 = CH5 */
#define MODE_CHANNEL_INDEX  RC_AUX_INDEX(2)  /* AUX2 = CH6 */
#define FAILSAFE_THROTTLE_US 950U            /* нижче порога виявлення */

typedef enum {
    FS_POLICY_CUT = 0,      /* приймач мовчить, контролер ловить таймаут */
    FS_POLICY_HOLD,         /* приймач нескінченно повторює останні значення */
    FS_POLICY_PRESET        /* приймач сам виставляє наперед задані значення */
} failsafe_policy_t;

typedef struct {
    failsafe_policy_t policy;
    rc_channel_map_t  map;
    uint32_t last_frame_ms;
    bool     failsafe;
    uint16_t us[RC_TOTAL_CHANNELS];
} rc_link_t;

static void link_init(rc_link_t *link, failsafe_policy_t policy, rc_channel_map_t map)
{
    memset(link, 0, sizeof(*link));
    link->policy = policy;
    link->map    = map;
    for (unsigned i = 0; i < RC_TOTAL_CHANNELS; ++i) {
        link->us[i] = RC_US_CENTER;
    }
}

static void link_on_frame(rc_link_t *link, const uint16_t raw[RC_TOTAL_CHANNELS],
                          uint32_t now_ms, bool rx_failsafe_bit)
{
    for (unsigned i = 0; i < RC_TOTAL_CHANNELS; ++i) {
        link->us[i] = rc_raw_to_us(raw[i]);
    }
    if (rx_failsafe_bit) {
        /* Біт у самому кадрі — приймач уже визнав втрату лінку */
        link->failsafe = true;
        return;
    }
    link->last_frame_ms = now_ms;
    link->failsafe      = false;
}

static void link_apply_failsafe(rc_link_t *link)
{
    if (link->policy == FS_POLICY_HOLD) {
        /* Нічого не робимо — і саме тому цей режим заборонений */
        return;
    }
    uint8_t thr = rc_map_channel_index(link->map, RC_AXIS_THROTTLE);
    link->us[thr] = FAILSAFE_THROTTLE_US;
    link->us[MODE_CHANNEL_INDEX] = flight_mode_nominal_us(FLIGHT_MODE_RTL);
}

static bool link_tick(rc_link_t *link, uint32_t now_ms)
{
    if (!link->failsafe && (now_ms - link->last_frame_ms) > FAILSAFE_TIMEOUT_MS) {
        link->failsafe = true;
    }
    if (link->failsafe) {
        link_apply_failsafe(link);
    }
    return link->failsafe;
}

static void print_axes(const char *title, rc_channel_map_t map,
                       const uint16_t us[RC_TOTAL_CHANNELS])
{
    uint16_t axes[RC_AXIS_COUNT];

    if (!rc_apply_map(map, us, axes)) {
        printf("  %-34s невідома розкладка\n", title);
        return;
    }
    printf("  %-34s [%s] крен=%4u  тангаж=%4u  курс=%4u  ГАЗ=%4u мкс\n",
           title, rc_map_name(map),
           axes[RC_AXIS_ROLL], axes[RC_AXIS_PITCH],
           axes[RC_AXIS_YAW], axes[RC_AXIS_THROTTLE]);
}

/* Рядок журналу Blackbox: сирі канали, нормалізовані команди, маска режиму */
static void blackbox_line(uint32_t t_ms, const uint16_t us[RC_TOTAL_CHANNELS],
                          const uint16_t axes[RC_AXIS_COUNT], flight_mode_t mode)
{
    const float rate_dps = 200.0f;   /* типова швидкість у режимі Acro */

    float roll  = ((float)axes[RC_AXIS_ROLL]  - 1500.0f) / 500.0f * rate_dps;
    float pitch = ((float)axes[RC_AXIS_PITCH] - 1500.0f) / 500.0f * rate_dps;
    float yaw   = ((float)axes[RC_AXIS_YAW]   - 1500.0f) / 500.0f * rate_dps;
    float thr   = ((float)axes[RC_AXIS_THROTTLE] - (float)RC_US_MIN) /
                  (float)(RC_US_MAX - RC_US_MIN);

    printf("BB %5u мс  rcData=%u,%u,%u,%u,%u,%u  rcCommand=%+.0f/%+.0f/%+.0f град/с, газ %.2f  flightModeFlags=0x%04X\n",
           t_ms, us[0], us[1], us[2], us[3], us[4], us[5],
           (double)roll, (double)pitch, (double)yaw, (double)thr,
           flight_mode_flags(mode));
}

static void demo_channel_order_mismatch(void)
{
    puts("=== 1. Розкладка передавача TAER, контролера — AETR ===");

    uint16_t raw[RC_TOTAL_CHANNELS];
    for (unsigned i = 0; i < RC_TOTAL_CHANNELS; ++i) {
        raw[i] = RC_RAW_CENTER;
    }

    /* Передавач у порядку TAER: CH1 газ, CH2 крен, CH3 тангаж, CH4 курс.
       Пілот тримає газ унизу й штовхає стік тангажу вперед. */
    raw[0] = rc_us_to_raw(RC_US_MIN);    /* газ на мінімумі */
    raw[1] = rc_us_to_raw(1500U);        /* крен по центру */
    raw[2] = rc_us_to_raw(RC_US_MAX);    /* тангаж уперед до упору */
    raw[3] = rc_us_to_raw(1500U);        /* курс по центру */
    raw[ARM_CHANNEL_INDEX]  = rc_us_to_raw(2000U);  /* тумблер ARM угору */
    raw[MODE_CHANNEL_INDEX] = rc_us_to_raw(flight_mode_nominal_us(FLIGHT_MODE_STABILIZE));

    uint8_t frame[CRSF_RC_FRAME_SIZE];
    size_t  len = crsf_build_rc_frame(raw, frame);
    printf("  кадр CRSF, %zu байтів, CRC8=0x%02X:", len, frame[len - 1U]);
    for (size_t i = 0; i < len; ++i) {
        printf(" %02X", frame[i]);
    }
    puts("");

    uint16_t decoded[RC_TOTAL_CHANNELS];
    crsf_status_t st = crsf_parse_rc_frame(frame, len, decoded);
    printf("  розбір: %s\n", crsf_status_text(st));
    if (st != CRSF_OK) {
        return;
    }

    uint16_t us[RC_TOTAL_CHANNELS];
    for (unsigned i = 0; i < RC_TOTAL_CHANNELS; ++i) {
        us[i] = rc_raw_to_us(decoded[i]);
    }

    print_axes("як задумав пілот:", RC_MAP_TAER, us);
    print_axes("як зрозумів контролер:", RC_MAP_AETR, us);
    puts("  зсув на один канал — і рух тангажем дає 100% газу, а скидання газу — крен.");

    /* Той самий кадр із зіпсованим байтом: CRC не пускає сміття далі */
    uint8_t broken[CRSF_RC_FRAME_SIZE];
    memcpy(broken, frame, len);
    broken[7] ^= 0x20U;
    printf("  кадр із перевернутим бітом: %s\n",
           crsf_status_text(crsf_parse_rc_frame(broken, len, decoded)));
}

static void demo_switch_hysteresis(void)
{
    puts("\n=== 2. Гістерезис тумблера ARM (AUX1) і селектор режимів (AUX2) ===");

    static const uint16_t series[] = { 1000U, 1340U, 1380U, 1500U, 1620U, 1660U, 1200U };
    switch_state_t arm_sw;
    switch_init(&arm_sw, SWITCH_POS_LOW);

    for (unsigned i = 0; i < sizeof(series) / sizeof(series[0]); ++i) {
        switch_position_t pos = switch2_update(&arm_sw, series[i]);
        printf("  AUX1 = %4u мкс -> %s\n", series[i], switch_position_name(pos));
    }
    printf("  перемикань за прогін: %u (смуга 1350..1650 мкс гасить брязкіт)\n",
           (unsigned)arm_sw.transitions);

    switch_state_t three;
    switch_init(&three, SWITCH_POS_LOW);
    printf("  3-позиційний на 1500 мкс -> %s, на 1320 мкс -> ",
           switch_position_name(switch3_update(&three, 1500U)));
    printf("%s (проміжок між вікнами утримує позицію)\n",
           switch_position_name(switch3_update(&three, 1320U)));

    for (unsigned m = 0; m < FLIGHT_MODE_COUNT; ++m) {
        uint16_t nominal = flight_mode_nominal_us((flight_mode_t)m);
        flight_mode_t decoded = flight_mode_from_us(nominal);
        printf("  AUX2 = %4u мкс -> %-9s  GNSS %s\n",
               nominal, flight_mode_name(decoded),
               flight_mode_requires_gnss(decoded) ? "потрібен" : "не потрібен");
    }
}

static void demo_arming(void)
{
    puts("\n=== 3. Блокування запуску двигунів ===");

    arming_state_t st;
    /* Тумблер ARM стояв угорі ще до подачі живлення */
    arming_init(&st, true);

    arming_inputs_t in = {
        .throttle_us     = 1500U,    /* газ «по центру» — наслідок чужої розкладки */
        .failsafe_active = false,
        .prearm_engaged  = false,
        .arm_switch      = true,
        .calibrating     = true,
        .tilt_deg        = 31.0f,
        .compass_healthy = false,
        .gnss_fix_3d     = false,
        .hdop            = 3.2f,
        .mode            = FLIGHT_MODE_LOITER,
    };

    uint16_t blocks = 0U;
    char text[320];

    bool armed = arming_update(&st, &in, &blocks);
    printf("  маска блокувань = 0x%04X, armed = %s\n", blocks, armed ? "так" : "ні");
    size_t reasons = arming_format_reasons(blocks, text, sizeof(text));
    printf("  STATUSTEXT (%zu причин): %s\n", reasons, text);

    for (uint16_t bit = 0x0001U; bit <= 0x0080U; bit = (uint16_t)(bit << 1)) {
        if (blocks & bit) {
            printf("    %-30s 0x%04X\n", arming_flag_name(bit), bit);
        }
    }

    /* Пілот усе виправив: тумблер униз (знімає засувку), газ на мінімум,
       апарат вирівняно, датчики готові. */
    in.arm_switch = false;
    (void)arming_update(&st, &in, &blocks);

    in.arm_switch      = true;
    in.throttle_us     = RC_US_MIN;
    in.calibrating     = false;
    in.prearm_engaged  = true;
    in.tilt_deg        = 1.4f;
    in.compass_healthy = true;
    in.gnss_fix_3d     = true;
    in.hdop            = 0.9f;

    armed = arming_update(&st, &in, &blocks);
    printf("  після усунення причин: маска = 0x%04X, armed = %s\n",
           blocks, armed ? "так" : "ні");
}

static void demo_failsafe(void)
{
    puts("\n=== 4. Втрата лінку: таймаут 100 мс і політика приймача ===");

    rc_link_t link;
    link_init(&link, FS_POLICY_PRESET, RC_MAP_AETR);

    uint16_t raw[RC_TOTAL_CHANNELS];
    for (unsigned i = 0; i < RC_TOTAL_CHANNELS; ++i) {
        raw[i] = RC_RAW_CENTER;
    }
    raw[rc_map_channel_index(RC_MAP_AETR, RC_AXIS_THROTTLE)] = rc_us_to_raw(1700U);
    raw[MODE_CHANNEL_INDEX] = rc_us_to_raw(flight_mode_nominal_us(FLIGHT_MODE_ALT_HOLD));

    rc_biquad_t roll_lpf, pitch_lpf;
    rc_biquad_init(&roll_lpf, 40.0f, 1000.0f / (float)FRAME_PERIOD_MS);
    rc_biquad_init(&pitch_lpf, 40.0f, 1000.0f / (float)FRAME_PERIOD_MS);

    uint32_t now_ms = 0U;
    for (unsigned frame_no = 0; frame_no < 40U; ++frame_no, now_ms += FRAME_PERIOD_MS) {
        bool link_alive = (frame_no < 10U);

        if (link_alive) {
            link_on_frame(&link, raw, now_ms, false);
        }
        bool failsafe = link_tick(&link, now_ms);

        uint16_t axes[RC_AXIS_COUNT];
        (void)rc_apply_map(link.map, link.us, axes);

        /* Мертва зона й згладжування — саме в такому порядку, як у стеку */
        axes[RC_AXIS_ROLL]  = rc_apply_deadband(axes[RC_AXIS_ROLL], 4U);
        axes[RC_AXIS_PITCH] = rc_apply_deadband(axes[RC_AXIS_PITCH], 4U);
        axes[RC_AXIS_ROLL]  = (uint16_t)rc_biquad_apply(&roll_lpf, (float)axes[RC_AXIS_ROLL]);
        axes[RC_AXIS_PITCH] = (uint16_t)rc_biquad_apply(&pitch_lpf, (float)axes[RC_AXIS_PITCH]);

        flight_mode_t mode = flight_mode_from_us(link.us[MODE_CHANNEL_INDEX]);

        if (frame_no == 9U || frame_no == 10U || frame_no == 35U) {
            printf("  %s", failsafe ? "FAILSAFE " : "         ");
            blackbox_line(now_ms, link.us, axes, mode);
        }
    }

    /* Той самий обрив, але приймач у режимі Hold Last State */
    rc_link_t hold;
    link_init(&hold, FS_POLICY_HOLD, RC_MAP_AETR);
    link_on_frame(&hold, raw, 0U, false);
    (void)link_tick(&hold, 200U);
    printf("  Hold Last State: газ лишився %u мкс — апарат летить за вектором до удару\n",
           hold.us[rc_map_channel_index(RC_MAP_AETR, RC_AXIS_THROTTLE)]);
}

static void demo_sbus_flags(void)
{
    puts("\n=== 5. Прапорці кадру SBUS ===");

    sbus_frame_t tx;
    memset(&tx, 0, sizeof(tx));
    for (unsigned i = 0; i < RC_TOTAL_CHANNELS; ++i) {
        tx.raw[i] = RC_RAW_CENTER;
    }
    tx.raw[0]    = rc_us_to_raw(RC_US_MAX);
    tx.ch17      = true;
    tx.frame_lost = true;
    tx.failsafe  = true;

    uint8_t frame[SBUS_FRAME_SIZE];
    size_t len = sbus_build(&tx, frame);

    sbus_frame_t rx;
    sbus_status_t st = sbus_parse(frame, len, &rx);
    printf("  %s; байт прапорців = 0x%02X\n", sbus_status_text(st), frame[23]);
    if (st == SBUS_OK) {
        printf("  CH1 = %u мкс, CH17 = %d, frame_lost = %d, failsafe = %d\n",
               rc_raw_to_us(rx.raw[0]), rx.ch17, rx.frame_lost, rx.failsafe);
    }

    frame[0] = 0x00U;   /* зсув по байтах на шині — заголовок зник */
    printf("  кадр без заголовка: %s\n",
           sbus_status_text(sbus_parse(frame, len, &rx)));
}

int main(void)
{
    demo_channel_order_mismatch();
    demo_switch_hysteresis();
    demo_arming();
    demo_failsafe();
    demo_sbus_flags();
    return 0;
}
