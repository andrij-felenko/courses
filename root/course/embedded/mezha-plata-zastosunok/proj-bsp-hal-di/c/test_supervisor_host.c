/* test_supervisor_host.c — модульні тести супервізора на комп'ютері розробника.
 *
 * Мок-плата веде віртуальний годинник і журнал викликів, тому тест
 * перевіряє не лише кінцевий стан, а й ПОРЯДОК та ЧАС дій.
 */
#include "supervisor.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef enum { EV_LED, EV_POWER, EV_ENV, EV_SLEEP } ev_kind_t;

typedef struct {
    ev_kind_t kind;
    int a;          /* led/domain/mode або ознака успіху для EV_ENV */
    int b;          /* state/enable або timeout_ms для EV_SLEEP */
    uint32_t t;     /* мітка віртуального годинника, мс */
} event_t;

#define MAX_EVENTS 128

static struct {
    uint32_t now_ms;
    uint16_t voltage_mv;
    bool battery_fault;
    unsigned env_calls;
    unsigned env_fail_every;   /* 0 — не збоїти; 3 — кожен третій виклик */
    bool env_fail_always;
    bool sensors_powered;
    bool radio_powered;
    board_led_state_t led[BOARD_LED_ID_COUNT];
    event_t events[MAX_EVENTS];
    size_t event_count;
} g;

static void push(ev_kind_t kind, int a, int b)
{
    if (g.event_count < MAX_EVENTS) {
        g.events[g.event_count].kind = kind;
        g.events[g.event_count].a = a;
        g.events[g.event_count].b = b;
        g.events[g.event_count].t = g.now_ms;
        g.event_count++;
    }
}

/* Пошук події від позиції from; a або b зі значенням -1 — «будь-яке». */
static long find_event(ev_kind_t kind, int a, int b, size_t from)
{
    for (size_t i = from; i < g.event_count; ++i) {
        if (g.events[i].kind != kind) continue;
        if (a >= 0 && g.events[i].a != a) continue;
        if (b >= 0 && g.events[i].b != b) continue;
        return (long)i;
    }
    return -1;
}

static bsp_status_t mock_led_set(board_led_id_t led, board_led_state_t state)
{
    if (led >= BOARD_LED_ID_COUNT) return BSP_STATUS_ERR_INVALID_PARAM;
    g.led[led] = state;
    push(EV_LED, (int)led, (int)state);
    return BSP_STATUS_OK;
}

static bsp_status_t mock_power_set(board_power_domain_t domain, bool enable)
{
    switch (domain) {
    case BOARD_POWER_DOMAIN_SENSORS: g.sensors_powered = enable; break;
    case BOARD_POWER_DOMAIN_RADIO:   g.radio_powered = enable;   break;
    default: return BSP_STATUS_ERR_INVALID_PARAM;
    }
    push(EV_POWER, (int)domain, enable ? 1 : 0);
    return BSP_STATUS_OK;
}

static bsp_status_t mock_get_bat(board_battery_metrics_t *m)
{
    if (g.battery_fault) return BSP_STATUS_ERR_TIMEOUT;
    m->voltage_mv = g.voltage_mv;
    m->charge_percent = 50;
    return BSP_STATUS_OK;
}

static bsp_status_t mock_read_env(board_env_metrics_t *e)
{
    g.env_calls++;

    /* Інжекція збою шини: або завжди, або на кожен N-й виклик. */
    bool fail = g.env_fail_always;
    if (!fail && g.env_fail_every != 0 && (g.env_calls % g.env_fail_every) == 0) {
        fail = true;
    }
    if (!g.sensors_powered) {
        fail = true;   /* знеструмлений давач мовчить — це теж збій шини */
    }

    push(EV_ENV, fail ? 0 : 1, -1);
    if (fail) return BSP_STATUS_ERR_BUS_FAULT;

    e->temperature_centi_c = 2250;
    return BSP_STATUS_OK;
}

static bsp_status_t mock_enter_low_power(board_sleep_mode_t mode, uint32_t timeout_ms)
{
    push(EV_SLEEP, (int)mode, (int)timeout_ms);
    g.now_ms += timeout_ms;   /* сон рухає віртуальний годинник */
    return BSP_STATUS_OK;
}

static void mock_delay_ms(uint32_t ms) { g.now_ms += ms; }
static uint32_t mock_uptime_ms(void) { return g.now_ms; }

static const bsp_driver_t mock_bsp = {
    .led_set             = mock_led_set,
    .power_domain_set    = mock_power_set,
    .get_battery_metrics = mock_get_bat,
    .read_environment    = mock_read_env,
    .enter_low_power     = mock_enter_low_power,
    .delay_ms            = mock_delay_ms,
    .uptime_ms           = mock_uptime_ms
};

static void mock_reset(uint16_t voltage_mv)
{
    memset(&g, 0, sizeof(g));
    g.voltage_mv = voltage_mv;
    g.now_ms = 1000;
}

static void test_normal_voltage(void)
{
    mock_reset(3800);
    supervisor_t sup;
    assert(supervisor_init(&sup, &mock_bsp) == BSP_STATUS_OK);

    supervisor_run_cycle(&sup);

    assert(!sup.is_low_power_warning);
    assert(!sup.is_critical_shutdown);
    assert(sup.has_fresh_env);
    assert(sup.last_env.temperature_centi_c == 2250);
    assert(sup.last_env.timestamp_ms >= 1015);      /* час витримки врахований */
    assert(g.led[BOARD_LED_ID_WARNING] == BOARD_LED_STATE_OFF);
    assert(g.led[BOARD_LED_ID_SYSTEM_STATUS] == BOARD_LED_STATE_OFF);
    assert(g.radio_powered);                        /* радіо дозволене */
    assert(!g.sensors_powered);                     /* давачі знеструмлені */
    assert(find_event(EV_SLEEP, -1, -1, 0) < 0);
    printf("[PASS] 3800 мВ: штатний цикл, радіо ввімкнене\n");
}

static void test_warning_voltage(void)
{
    mock_reset(3200);
    supervisor_t sup;
    assert(supervisor_init(&sup, &mock_bsp) == BSP_STATUS_OK);

    supervisor_run_cycle(&sup);

    assert(sup.is_low_power_warning);
    assert(!sup.is_critical_shutdown);
    assert(sup.has_fresh_env);                      /* вимірювати ще можна */
    assert(g.led[BOARD_LED_ID_WARNING] == BOARD_LED_STATE_ON);
    assert(!g.radio_powered);                       /* радіо заблоковане */
    assert(find_event(EV_SLEEP, -1, -1, 0) < 0);
    printf("[PASS] 3200 мВ: тривога, радіо заблоковане\n");
}

static void test_critical_shutdown(void)
{
    mock_reset(2900);
    supervisor_t sup;
    assert(supervisor_init(&sup, &mock_bsp) == BSP_STATUS_OK);

    supervisor_run_cycle(&sup);

    assert(sup.is_critical_shutdown);
    assert(!g.sensors_powered);
    assert(!g.radio_powered);
    assert(g.led[BOARD_LED_ID_WARNING] == BOARD_LED_STATE_ON);

    const long sleep_idx = find_event(EV_SLEEP, BOARD_SLEEP_MODE_DEEP, -1, 0);
    assert(sleep_idx >= 0);
    assert(g.events[sleep_idx].b == (int)SUPERVISOR_DEEP_SLEEP_MS);
    /* Давачі знеструмлено ДО того, як ядро лягло спати. */
    assert(find_event(EV_POWER, BOARD_POWER_DOMAIN_SENSORS, 0, 0) < sleep_idx);
    printf("[PASS] 2900 мВ: аварійний сон на 1 годину\n");
}

static void test_settle_time_invariant(void)
{
    mock_reset(3800);
    supervisor_t sup;
    assert(supervisor_init(&sup, &mock_bsp) == BSP_STATUS_OK);

    supervisor_run_cycle(&sup);

    const long on_idx = find_event(EV_POWER, BOARD_POWER_DOMAIN_SENSORS, 1, 0);
    assert(on_idx >= 0);
    const long env_idx = find_event(EV_ENV, -1, -1, (size_t)on_idx);
    assert(env_idx >= 0);

    const uint32_t settle = g.events[env_idx].t - g.events[on_idx].t;
    assert(settle >= SUPERVISOR_SENSOR_SETTLE_MS);
    printf("[PASS] витримка стабілізації: %u мс (потрібно %u)\n",
           settle, SUPERVISOR_SENSOR_SETTLE_MS);
}

static void test_fault_injection_recovers(void)
{
    mock_reset(3800);
    g.env_fail_every = 3;            /* кожен третій виклик — збій шини */
    supervisor_t sup;
    assert(supervisor_init(&sup, &mock_bsp) == BSP_STATUS_OK);

    for (int i = 0; i < 5; ++i) {
        supervisor_run_cycle(&sup);
        assert(sup.has_fresh_env);   /* повтор витягує кожен цикл */
        assert(!g.sensors_powered);
    }
    assert(sup.env_fault_count > 0); /* збої були і їх пораховано */
    printf("[PASS] збій на кожен третій виклик: %u повторів, дані отримано\n",
           sup.env_fault_count);
}

static void test_fault_injection_gives_up(void)
{
    mock_reset(3800);
    g.env_fail_always = true;        /* давач мертвий назавжди */
    supervisor_t sup;
    assert(supervisor_init(&sup, &mock_bsp) == BSP_STATUS_OK);

    supervisor_run_cycle(&sup);      /* якби був нескінченний цикл — тут би й повисло */

    assert(!sup.has_fresh_env);
    assert(sup.env_fault_count == SUPERVISOR_ENV_ATTEMPTS);
    assert(!g.sensors_powered);      /* живлення знято попри збій */
    assert(g.led[BOARD_LED_ID_SYSTEM_STATUS] == BOARD_LED_STATE_OFF);
    printf("[PASS] мертвий давач: %u спроби й вихід без зависання\n",
           SUPERVISOR_ENV_ATTEMPTS);
}

static void test_battery_read_fault(void)
{
    mock_reset(3800);
    g.battery_fault = true;
    supervisor_t sup;
    assert(supervisor_init(&sup, &mock_bsp) == BSP_STATUS_OK);

    supervisor_run_cycle(&sup);

    assert(sup.battery_fault_count == 1);
    assert(g.led[BOARD_LED_ID_WARNING] == BOARD_LED_STATE_ON);
    assert(find_event(EV_SLEEP, -1, -1, 0) < 0);   /* наосліп не засинаємо */
    assert(find_event(EV_ENV, -1, -1, 0) < 0);
    printf("[PASS] збій АЦП: тривога без сну й без вимірювань\n");
}

static void test_incomplete_driver_rejected(void)
{
    bsp_driver_t broken = mock_bsp;
    broken.uptime_ms = NULL;

    supervisor_t sup;
    assert(supervisor_init(&sup, &broken) == BSP_STATUS_ERR_INVALID_PARAM);
    assert(supervisor_init(&sup, NULL) == BSP_STATUS_ERR_INVALID_PARAM);
    printf("[PASS] неповна таблиця методів відхилена на старті\n");
}

int main(void)
{
    test_normal_voltage();
    test_warning_voltage();
    test_critical_shutdown();
    test_settle_time_invariant();
    test_fault_injection_recovers();
    test_fault_injection_gives_up();
    test_battery_read_fault();
    test_incomplete_driver_rejected();

    printf("\nУсі тести супервізора пройдено на хості — без жодного мікроконтролера.\n");
    return 0;
}
