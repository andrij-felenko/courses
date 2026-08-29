/* Стенд для арбітра: модельний час, чотири станції в ефірі й сценарій,
 * що проганяє всі переходи — захоплення токена, передачу зміни, втрату
 * звʼязку й перехоплення командиром.
 *
 * На борту цю роль виконують три задачі FreeRTOS: приймач телеметрії кличе
 * arbiter_process_heartbeat(), задача ручного керування на 50 Гц —
 * arbiter_is_flight_command_allowed(), таймер на 50 Гц — arbiter_periodic_tick().
 * Тут вони згорнуті в один цикл, щоб час був відтворюваним. */
#include "arbiter.h"

#include <stdio.h>

#define TICK_MS       20u  /* період задачі-таймера */
#define HB_PERIOD_MS 100u  /* станції шлють heartbeat 10 разів на секунду */

#define GCS_ALPHA   10  /* пілот-1 */
#define GCS_BRAVO   20  /* пілот-2, змінний */
#define GCS_SENSOR  30  /* оператор корисного навантаження */
#define GCS_CMD     40  /* командир */
#define GCS_GHOST   99  /* станція, якої в ефірі немає */

typedef struct {
    uint8_t     id;
    uint8_t     roles;
    bool        tx;     /* чи чути її на борту просто зараз */
    const char *name;
} sim_gcs_t;

static sim_gcs_t g_net[] = {
    { GCS_ALPHA,  ROLE_PILOT | ROLE_MONITOR,     true, "ALPHA"  },
    { GCS_BRAVO,  ROLE_PILOT | ROLE_MONITOR,     true, "BRAVO"  },
    { GCS_SENSOR, ROLE_PAYLOAD | ROLE_MONITOR,   true, "SENSOR" },
    { GCS_CMD,    ROLE_COMMANDER | ROLE_MONITOR, true, "CMD"    },
};

static uint32_t g_now;      /* модельний час борта, мс */
static uint32_t g_hb_timer; /* відлік до наступної пачки heartbeat */

static sim_gcs_t *station_by_id(uint8_t id)
{
    for (unsigned i = 0; i < sizeof(g_net) / sizeof(g_net[0]); ++i) {
        if (g_net[i].id == id) {
            return &g_net[i];
        }
    }
    return NULL;
}

/* Один оберт бортового циклу: що почули з ефіру, те й згодували арбітрові. */
static void board_cycle(void)
{
    g_now += TICK_MS;
    g_hb_timer += TICK_MS;
    if (g_hb_timer >= HB_PERIOD_MS) {
        g_hb_timer = 0;
        for (unsigned i = 0; i < sizeof(g_net) / sizeof(g_net[0]); ++i) {
            if (g_net[i].tx) {
                arbiter_process_heartbeat(g_net[i].id, g_net[i].roles, g_now);
            }
        }
    }
    arbiter_periodic_tick(g_now);
}

static void advance(uint32_t dt_ms)
{
    for (uint32_t t = 0; t < dt_ms; t += TICK_MS) {
        board_cycle();
    }
}

/* Ширину під українську колонку не ставимо: printf рахує байти, а не літери,
 * тож рівняти по ній нема сенсу. */
static void say(const char *what, const char *result)
{
    printf("[%6u мс] %s -> %s [%s, пілот=%u]\n",
           g_now, what, result, arb_state_str(arbiter_state()), arbiter_active_pilot());
}

static void say_err(const char *what, arb_err_t err)
{
    say(what, arb_err_str(err));
}

static void say_flag(const char *what, bool allowed)
{
    say(what, allowed ? "ПРОПУЩЕНО" : "ВІДКИНУТО");
}

static arb_err_t confirm(uint8_t id, int16_t roll, int16_t pitch, int16_t yaw, int16_t thr,
                         uint32_t *nonce_out)
{
    stick_axes_t sticks = { roll, pitch, yaw, thr };
    return arbiter_confirm_handover_sticks(id, &sticks, g_now, nonce_out);
}

int main(void)
{
    uint32_t nonce_alpha = 0, nonce_bravo = 0, nonce_cmd = 0;
    arb_err_t err;

    arbiter_init(0x0BADF00Du, 0);
    advance(200); /* станції встигають назватися */
    say("борт піднявся, реєстр наповнено", "—");

    /* 1. Захоплення вільного токена. */
    err = arbiter_request_pilot_token(GCS_ALPHA, g_now, &nonce_alpha);
    say_err("ALPHA просить токен пілота", err);

    err = arbiter_request_pilot_token(GCS_BRAVO, g_now, NULL);
    say_err("BRAVO просить той самий токен", err);

    err = arbiter_request_pilot_token(GCS_GHOST, g_now, NULL);
    say_err("невідома станція просить токен", err);

    err = arbiter_request_pilot_token(GCS_SENSOR, g_now, NULL);
    say_err("SENSOR (без ролі пілота) просить токен", err);

    /* 2. Гарячий шлях: що пропускається в мікшер, а що ні. */
    say_flag("стіки ALPHA із чинним nonce",
             arbiter_is_flight_command_allowed(GCS_ALPHA, nonce_alpha));
    say_flag("стіки ALPHA зі старим nonce",
             arbiter_is_flight_command_allowed(GCS_ALPHA, nonce_alpha ^ 1u));
    say_flag("стіки BRAVO з підгляненим nonce ALPHA",
             arbiter_is_flight_command_allowed(GCS_BRAVO, nonce_alpha));

    /* 3. Розділення площин: камера й політ не заважають одне одному. */
    say_flag("SENSOR веде підвіс",
             arbiter_is_payload_command_allowed(GCS_SENSOR, g_now));
    say_flag("ALPHA лізе в підвіс",
             arbiter_is_payload_command_allowed(GCS_ALPHA, g_now));

    /* 4. Передача зміни ALPHA -> BRAVO. Апарат висить, тяга 550. */
    arbiter_set_current_thrust(550);
    err = arbiter_initiate_handover(GCS_ALPHA, GCS_BRAVO, g_now);
    say_err("ALPHA пропонує зміну BRAVO", err);

    say_flag("ALPHA керує далі, поки триває перевірка",
             arbiter_is_flight_command_allowed(GCS_ALPHA, nonce_alpha));

    advance(100);
    err = confirm(GCS_BRAVO, 120, -8, 4, 545, NULL);
    say_err("BRAVO: крен відхилено на 12%", err);

    advance(100);
    err = confirm(GCS_BRAVO, -14, 9, -6, 0, NULL);
    say_err("BRAVO: стіки в центрі, газ в упорі вниз", err);

    advance(100);
    err = confirm(GCS_BRAVO, -14, 9, -6, 528, NULL);
    say_err("BRAVO: нейтраль і газ під тягу (перший кадр)", err);

    advance(100);
    err = confirm(GCS_BRAVO, 20, -3, 11, 572, NULL); /* дрейф у межах гістерезису */
    say_err("BRAVO: витримка ще не набігла", err);

    advance(300);
    err = confirm(GCS_BRAVO, -22, 12, 7, 561, &nonce_bravo);
    say_err("BRAVO: витримка 300 мс набігла", err);

    say_flag("ALPHA шле стіки після передачі",
             arbiter_is_flight_command_allowed(GCS_ALPHA, nonce_alpha));
    say_flag("BRAVO шле стіки з новим nonce",
             arbiter_is_flight_command_allowed(GCS_BRAVO, nonce_bravo));

    /* 5. Передача, яку ніхто не підтвердив: вікно згоряє, борт лишається за BRAVO. */
    err = arbiter_initiate_handover(GCS_BRAVO, GCS_ALPHA, g_now);
    say_err("BRAVO пропонує зміну назад ALPHA", err);
    advance(5200);
    say("вікно передачі згоріло, ніхто не підтвердив", "—");

    /* 6. Асиметричне зникнення каналу: борт судить лише за власним таймером. */
    station_by_id(GCS_BRAVO)->tx = false;
    advance(1100);
    say("BRAVO замовк на 1.1 с", "—");
    say_flag("стіки BRAVO після втрати оренди",
             arbiter_is_flight_command_allowed(GCS_BRAVO, nonce_bravo));
    say_flag("SENSOR і далі веде підвіс",
             arbiter_is_payload_command_allowed(GCS_SENSOR, g_now));

    station_by_id(GCS_BRAVO)->tx = true;
    advance(200);
    say("BRAVO знову в ефірі", "—");
    say_flag("стіки BRAVO зі СТАРИМ nonce",
             arbiter_is_flight_command_allowed(GCS_BRAVO, nonce_bravo));

    /* 7. Аварійне перехоплення командиром — без згоди чинного пілота. */
    err = arbiter_commander_override(GCS_SENSOR, g_now, NULL);
    say_err("SENSOR вдає командира", err);

    err = arbiter_commander_override(GCS_CMD, g_now, &nonce_cmd);
    say_err("CMD перехоплює борт", err);

    say_flag("стіки BRAVO під замком",
             arbiter_is_flight_command_allowed(GCS_BRAVO, nonce_bravo));
    say_flag("стіки CMD під замком",
             arbiter_is_flight_command_allowed(GCS_CMD, nonce_cmd));
    say_flag("SENSOR веде підвіс під замком",
             arbiter_is_payload_command_allowed(GCS_SENSOR, g_now));

    err = arbiter_request_pilot_token(GCS_ALPHA, g_now, NULL);
    say_err("ALPHA просить токен під замком", err);

    err = arbiter_release_override(GCS_BRAVO, g_now);
    say_err("BRAVO намагається зняти замок", err);

    err = arbiter_release_override(GCS_CMD, g_now);
    say_err("CMD віддає борт", err);

    say_flag("стіки CMD після зняття замка",
             arbiter_is_flight_command_allowed(GCS_CMD, nonce_cmd));

    err = arbiter_request_pilot_token(GCS_ALPHA, g_now, &nonce_alpha);
    say_err("ALPHA бере вільний токен", err);
    say_flag("стіки ALPHA із новим nonce",
             arbiter_is_flight_command_allowed(GCS_ALPHA, nonce_alpha));

    return 0;
}
