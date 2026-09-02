#include "conn_fsm.h"

#include "at_link.h"
#include "blackbox.h"
#include "modem_hal.h"

#include <stdio.h>
#include <string.h>

/* Параметри вузла зашиті навмисно: це один конкретний прилад, а не бібліотека. */
#define APN         "iot.provider.apn"
#define BROKER_HOST "cloud.example.com"
#define BROKER_PORT "1883"
#define SIM_PIN     "0000"
#define MQTT_ID     "well-042"
#define MQTT_USER   "well-042"
#define MQTT_PASS   "s3cret"
#define MQTT_TOPIC  "telemetry/well-042"
#define KEEPALIVE_S 60u
#define PSM_ENABLED 1 /* модуль уміє PSM за 3GPP Rel.12 */

/* Таймаути станів, мілісекунди. */
#define T_VBAT_SETTLE    200u
#define T_PWRKEY_PULSE  1200u
#define T_STATUS_WAIT   5000u
#define T_AT_PROBE       500u
#define T_AT_CMD        3000u
#define T_SIM          10000u
#define T_NET_SEARCH   90000u
#define T_IP_ATTACH    30000u
#define T_TCP          20000u
#define T_AUTH         10000u
#define T_SEND         20000u
#define T_PING_RESP    10000u
#define T_RESET_PULSE    300u
#define T_RESET_WAIT    5000u
#define T_POWER_DOWN    4000u /* розряд ємностей фільтрації */
#define T_CLOSE         3000u
#define T_SIM_BUSY      1000u
#define T_FATAL_SLEEP 3600000u

#define NET_POLL_MS     3000u
#define KEEPALIVE_MS    (KEEPALIVE_S * 1000u)

#define MAX_RETRIES        5u
#define AT_PROBE_LIMIT     5u
#define BACKOFF_BASE_MS 2000u
#define BACKOFF_CEIL_MS 300000u

#define EVENT_TIMEOUT 0xFFu /* мітка таймауту в чорній скриньці */

static const char *const k_init_seq[] = {
    "ATE0",      /* луна засмічує приймальний буфер */
    "AT+CMEE=2", /* розширені коди помилок */
    "AT+IFC=2,2" /* апаратний контроль потоку RTS/CTS */
};

static const char *const k_attach_seq[] = {
    "AT+CGDCONT=1,\"IP\",\"" APN "\"",
    "AT+CGATT=1",
    "AT+CGPADDR=1"
};

#define N_INIT   (sizeof(k_init_seq) / sizeof(k_init_seq[0]))
#define N_ATTACH (sizeof(k_attach_seq) / sizeof(k_attach_seq[0]))

static void enter(conn_fsm_t *f, conn_state_t st, uint32_t timeout_ms);
static void escalate(conn_fsm_t *f, uint8_t level);

static void arm_timer(conn_fsm_t *f, uint32_t timeout_ms)
{
    f->enter_ms = hal_now_ms();
    f->timeout_ms = timeout_ms;
}

static void arm_poll(conn_fsm_t *f, uint32_t period_ms)
{
    f->poll_period_ms = period_ms;
    f->poll_last_ms = hal_now_ms();
}

/* Кадр у сокет: спершу AT+CIPSEND=<len>, тіло — після запрошення '>'. */
static void tx_frame(conn_fsm_t *f, size_t len)
{
    char cmd[32];

    f->out_len = len;
    snprintf(cmd, sizeof(cmd), "AT+CIPSEND=%u", (unsigned)len);
    at_link_send_line(cmd);
}

static void enter(conn_fsm_t *f, conn_state_t st, uint32_t timeout_ms)
{
    blackbox_record((uint8_t)f->state, (uint8_t)st, f->last_event, f->retry,
                    f->rssi_dbm, f->last_cme, hal_vbat_mv());

    f->state = st;
    f->substep = 0;
    f->poll_period_ms = 0;
    f->out_len = 0;
    arm_timer(f, timeout_ms);

    switch (st) {
    case CONN_NO_POWER:
        hal_modem_power_set(false);
        hal_modem_pwrkey_set(false);
        hal_modem_reset_set(false);
        blackbox_flush(); /* журнал мусить пережити знеструмлення */
        break;

    case CONN_POWERING_ON:
        hal_modem_power_set(true);
        arm_timer(f, T_VBAT_SETTLE); /* далі витримки веде substep */
        break;

    case CONN_MODEM_READY:
        f->probes = 0;
        at_link_send_line("AT"); /* автопідлаштування бодрейту */
        arm_timer(f, T_AT_PROBE);
        break;

    case CONN_SIM_READY:
        at_link_send_line("AT+CPIN?");
        arm_timer(f, T_SIM);
        break;

    case CONN_NET_SEARCH:
        at_link_send_line("AT+CEREG=1"); /* URC про зміну реєстрації */
        at_link_send_line("AT+CEREG?");
        arm_poll(f, NET_POLL_MS);
        arm_timer(f, T_NET_SEARCH);
        break;

    case CONN_IP_ATTACH:
        at_link_send_line(k_attach_seq[0]);
        arm_timer(f, T_IP_ATTACH);
        break;

    case CONN_TCP_CONNECT:
        at_link_send_line("AT+CIPSTART=\"TCP\",\"" BROKER_HOST "\"," BROKER_PORT);
        arm_timer(f, T_TCP);
        break;

    case CONN_PROTOCOL_AUTH:
        mqtt_rx_init(&f->mqtt);
        tx_frame(f, mqtt_connect(f->out, sizeof(f->out), MQTT_ID, MQTT_USER,
                                 MQTT_PASS, (uint16_t)KEEPALIVE_S));
        arm_timer(f, T_AUTH);
        break;

    case CONN_READY_TO_SEND:
        /* Тракт цілий: драбина відновлення повертається на нульову сходинку. */
        f->level = 0;
        f->retry = 0;
        f->ping_pending = false;
        arm_poll(f, KEEPALIVE_MS);
        arm_timer(f, 0);
        break;

    case CONN_SENDING:
        if (++f->packet_id == 0u) {
            f->packet_id = 1u; /* нуль як ідентифікатор MQTT заборонений */
        }
        /* submit() обмежує довжину, тож кадр гарантовано вміщається. */
        tx_frame(f, mqtt_publish_qos1(f->out, sizeof(f->out), MQTT_TOPIC,
                                      f->tx, f->tx_len, f->packet_id));
        arm_timer(f, T_SEND);
        break;

    case CONN_DISCONNECTING:
        tx_frame(f, mqtt_disconnect(f->out, sizeof(f->out)));
        arm_timer(f, T_CLOSE);
        break;

    case CONN_PSM_SLEEP:
        /* T3412_ext ≈ 1 год, T3324 ≈ 20 с: радіо спить, реєстрацію тримає мережа. */
        at_link_send_line("AT+CPSMS=1,,,\"00100001\",\"00000101\"");
        arm_timer(f, 0);
        break;

    case CONN_BACKOFF:
        break; /* час паузи вже пораховано викликачем */

    case CONN_HW_RESET:
        hal_modem_reset_set(true);
        arm_timer(f, T_RESET_PULSE);
        break;

    case CONN_POWER_CYCLE:
        hal_modem_power_set(false);
        hal_modem_pwrkey_set(false);
        hal_modem_reset_set(false);
        blackbox_flush();
        arm_timer(f, T_POWER_DOWN);
        break;

    case CONN_FATAL_STOP:
        hal_modem_power_set(false);
        blackbox_flush();
        arm_timer(f, T_FATAL_SLEEP); /* година тиші замість штурму ефіру */
        break;
    }
}

/* Усічений двійковий експоненційний відкат із ПОВНИМ джиттером. */
static void enter_backoff(conn_fsm_t *f, conn_state_t target)
{
    uint32_t shift = (f->retry > 7u) ? 7u : f->retry;
    uint32_t span = BACKOFF_BASE_MS << shift;

    if (span > BACKOFF_CEIL_MS) {
        span = BACKOFF_CEIL_MS;
    }
    /* random(0, span): зсув усередині вікна розводить тисячі вузлів у часі. */
    uint32_t wait = hal_random_u32() % (span + 1u);

    f->backoff_target = target;
    enter(f, CONN_BACKOFF, wait);
}

/* Коди CME → сходинка драбини (таблиця зі статті). 0 — пауза без зміни стану. */
static uint8_t cme_level(uint16_t code)
{
    switch (code) {
    case 10:  return 5; /* SIM not inserted — лікувати нічим */
    case 13:  return 4; /* SIM failure */
    case 14:  return 0; /* SIM busy: читає адресну книгу */
    case 30:  return 3; /* No network service */
    case 33:  return 2; /* Operation not allowed — немає PDP */
    case 100: return 4; /* фатальний збій бейсбенду */
    default:  return 1;
    }
}

static void escalate(conn_fsm_t *f, uint8_t level)
{
    if (level == f->level) {
        if (++f->retry > MAX_RETRIES) {
            /* Сходинка вичерпана: штурмувати її далі — марно палити батарею. */
            f->retry = 1;
            level = (uint8_t)(level + 1u);
        }
    } else {
        f->retry = 1;
    }
    f->level = level;

    switch (level) {
    case 1: /* Сокет: модем живий, реєстрація й IP на місці */
        at_link_send_line("AT+CIPCLOSE");
        enter_backoff(f, CONN_TCP_CONNECT);
        break;

    case 2: /* PDP-контекст: радіолінк цілий, IP втрачено */
        at_link_send_line("AT+CIPCLOSE");
        at_link_send_line("AT+CGACT=0,1");
        enter_backoff(f, CONN_IP_ATTACH);
        break;

    case 3: /* Радіо: перезапуск радіотракту без знеструмлення */
        at_link_send_line("AT+CIPCLOSE");
        at_link_send_line("AT+CFUN=0");
        at_link_send_line("AT+CFUN=1");
        enter_backoff(f, CONN_NET_SEARCH);
        break;

    case 4: /* Залізо: спершу RESET, і лише потім силовий ключ */
        enter(f, CONN_HW_RESET, 0);
        break;

    default:
        enter(f, CONN_FATAL_STOP, 0);
        break;
    }
}

/* Обмін у межах відкритої сесії: запрошення, SEND OK і байти від брокера. */
static void on_session_msg(conn_fsm_t *f, const at_msg_t *m)
{
    if (m->kind == AT_MSG_PROMPT) {
        if (f->out_len > 0) {
            at_link_send_raw(f->out, f->out_len);
            f->out_len = 0;
        }
        return;
    }
    if (m->kind == AT_MSG_SEND_OK) {
        /* Модем узяв кадр у свій буфер. Це ще НЕ доставка: підтвердження
           дає лише PUBACK від брокера. */
        return;
    }
    if (m->kind == AT_MSG_ERROR) {
        escalate(f, 1);
        return;
    }
    if (m->kind != AT_MSG_DATA) {
        return;
    }

    mqtt_pkt_t pkt;
    for (size_t i = 0; i < m->len; ++i) {
        if (!mqtt_rx_byte(&f->mqtt, m->data[i], &pkt)) {
            continue;
        }
        switch (pkt.kind) {
        case MQTT_PKT_CONNACK:
            if (f->state != CONN_PROTOCOL_AUTH) {
                break;
            }
            if (pkt.code == 0u) {
                f->log_pending = (blackbox_count() > 0u);
                enter(f, CONN_READY_TO_SEND, 0);
            } else {
                /* Брокер відмовив у правах — повтори тут не допоможуть. */
                f->last_cme = pkt.code;
                enter(f, CONN_FATAL_STOP, 0);
            }
            break;

        case MQTT_PKT_PUBACK:
            if (f->state == CONN_SENDING && pkt.packet_id == f->packet_id) {
                if (f->tx_is_log) {
                    blackbox_mark_sent(f->tx_len);
                    f->log_pending = (blackbox_count() > 0u);
                }
                f->tx_pending = false;
                enter(f, CONN_READY_TO_SEND, 0);
            }
            break;

        case MQTT_PKT_PINGRESP:
            f->ping_pending = false;
            if (f->state == CONN_READY_TO_SEND) {
                arm_timer(f, 0);
            }
            break;

        case MQTT_PKT_BROKEN:
            escalate(f, 1); /* потік зіпсовано — перевідкриваємо сокет */
            return;

        default:
            break;
        }
    }
}

static void on_message(conn_fsm_t *f, const at_msg_t *m)
{
    f->last_event = (uint8_t)m->kind;

    /* Спершу — асинхронні сповіщення, що б'ють по тракту незалежно від стану. */
    switch (m->kind) {
    case AT_MSG_CSQ:
        f->rssi_dbm = (int8_t)m->value;
        return;

    case AT_MSG_BOOT:
        if (f->state > CONN_POWERING_ON) {
            /* Модем перезавантажився САМ: просів VBAT на передавальному
               імпульсі. Усе, що ми про нього знали, більше не чинне. */
            f->last_cme = 0;
            enter(f, CONN_MODEM_READY, 0);
        }
        return;

    case AT_MSG_CLOSED:
        if (f->state >= CONN_TCP_CONNECT && f->state <= CONN_SENDING) {
            escalate(f, 1);
        } else if (f->state == CONN_DISCONNECTING) {
            enter(f, PSM_ENABLED ? CONN_PSM_SLEEP : CONN_NO_POWER, 0);
        }
        return;

    case AT_MSG_PDP_DEACT:
        if (f->state >= CONN_TCP_CONNECT && f->state <= CONN_SENDING) {
            escalate(f, 2);
        }
        return;

    case AT_MSG_CME_ERROR: {
        f->last_cme = (uint16_t)m->value;
        uint8_t level = cme_level(f->last_cme);
        if (level == 0u) { /* SIM busy: пауза й той самий крок */
            f->backoff_target = f->state;
            enter(f, CONN_BACKOFF, T_SIM_BUSY);
        } else {
            escalate(f, level);
        }
        return;
    }

    case AT_MSG_CREG:
        if (m->value == 1 || m->value == 5) { /* домашня мережа або роумінг */
            if (f->state == CONN_NET_SEARCH) {
                f->level = 0;
                f->retry = 0;
                enter(f, CONN_IP_ATTACH, 0);
            }
        } else if (f->state > CONN_NET_SEARCH) {
            escalate(f, 3); /* вишку втрачено */
        }
        return;

    default:
        break;
    }

    switch (f->state) {
    case CONN_MODEM_READY:
        if (m->kind == AT_MSG_OK) {
            if (f->substep < N_INIT) {
                at_link_send_line(k_init_seq[f->substep++]);
                arm_timer(f, T_AT_CMD);
            } else {
                enter(f, CONN_SIM_READY, 0);
            }
        }
        break;

    case CONN_SIM_READY:
        if (m->kind == AT_MSG_CPIN) {
            if (m->value == CPIN_READY) {
                f->substep = 1; /* лишилося дочекатися OK */
            } else if (m->value == CPIN_NEED_PIN) {
                at_link_send_line("AT+CPIN=\"" SIM_PIN "\"");
                f->substep = 2;
                arm_timer(f, T_SIM);
            } else {
                /* Картки немає або збій контактів — зв'язку не буде. */
                enter(f, CONN_FATAL_STOP, 0);
            }
        } else if (m->kind == AT_MSG_OK) {
            if (f->substep == 1) {
                enter(f, CONN_NET_SEARCH, 0);
            } else if (f->substep == 2) {
                at_link_send_line("AT+CPIN?"); /* перевіряємо після введення PIN */
                f->substep = 0;
                arm_timer(f, T_SIM);
            }
        } else if (m->kind == AT_MSG_ERROR) {
            escalate(f, 4);
        }
        break;

    case CONN_NET_SEARCH:
        break; /* реєстрацію ловить обробник +CREG/+CEREG вище */

    case CONN_IP_ATTACH:
        if (m->kind == AT_MSG_OK) {
            if (++f->substep < N_ATTACH) {
                at_link_send_line(k_attach_seq[f->substep]);
            }
            /* Після останньої команди чекаємо на +CGPADDR з адресою. */
        } else if (m->kind == AT_MSG_IP_READY) {
            f->level = 0;
            f->retry = 0;
            enter(f, CONN_TCP_CONNECT, 0);
        } else if (m->kind == AT_MSG_ERROR) {
            escalate(f, 2);
        }
        break;

    case CONN_TCP_CONNECT:
        if (m->kind == AT_MSG_CONNECT_OK) {
            f->level = 0;
            f->retry = 0;
            enter(f, CONN_PROTOCOL_AUTH, 0);
        } else if (m->kind == AT_MSG_ERROR) {
            escalate(f, 1);
        }
        break;

    case CONN_PROTOCOL_AUTH:
    case CONN_READY_TO_SEND:
    case CONN_SENDING:
    case CONN_DISCONNECTING:
        on_session_msg(f, m);
        break;

    default:
        break;
    }
}

static void on_timeout(conn_fsm_t *f)
{
    f->last_event = EVENT_TIMEOUT;

    switch (f->state) {
    case CONN_POWERING_ON:
        if (f->substep == 0) { /* напруга усталилася — тиснемо PWRKEY */
            hal_modem_pwrkey_set(true);
            f->substep = 1;
            arm_timer(f, T_PWRKEY_PULSE);
        } else if (f->substep == 1) { /* відпускаємо й чекаємо на STATUS */
            hal_modem_pwrkey_set(false);
            f->substep = 2;
            arm_timer(f, T_STATUS_WAIT);
        } else {
            escalate(f, 4); /* пін STATUS не піднявся */
        }
        break;

    case CONN_MODEM_READY:
        if (f->substep == 0 && ++f->probes < AT_PROBE_LIMIT) {
            at_link_send_line("AT");
            arm_timer(f, T_AT_PROBE);
        } else {
            escalate(f, 4); /* UART мовчить — це вже залізо */
        }
        break;

    case CONN_SIM_READY:
        escalate(f, 4);
        break;

    case CONN_NET_SEARCH:
        escalate(f, 3);
        break;

    case CONN_IP_ATTACH:
        escalate(f, 2);
        break;

    case CONN_TCP_CONNECT:
    case CONN_PROTOCOL_AUTH:
    case CONN_SENDING:
        escalate(f, 1);
        break;

    case CONN_READY_TO_SEND:
        /* Мовчання на PINGREQ — класична ознака напіввідкритого сокета:
           локально він «відкритий», але жоден байт не доходить. */
        escalate(f, 1);
        break;

    case CONN_DISCONNECTING:
        enter(f, PSM_ENABLED ? CONN_PSM_SLEEP : CONN_NO_POWER, 0);
        break;

    case CONN_BACKOFF:
        enter(f, f->backoff_target, 0);
        break;

    case CONN_HW_RESET:
        if (f->substep == 0) {
            hal_modem_reset_set(false);
            f->substep = 1;
            arm_timer(f, T_RESET_WAIT); /* чекаємо на RDY */
        } else {
            enter(f, CONN_POWER_CYCLE, 0); /* скидання не допомогло */
        }
        break;

    case CONN_POWER_CYCLE:
        enter(f, CONN_POWERING_ON, 0);
        break;

    case CONN_FATAL_STOP:
        f->level = 0;
        f->retry = 0;
        enter(f, CONN_NO_POWER, 0);
        break;

    default:
        arm_timer(f, 0);
        break;
    }
}

void conn_fsm_init(conn_fsm_t *f)
{
    memset(f, 0, sizeof(*f));
    f->state = CONN_NO_POWER;
    f->rssi_dbm = RSSI_UNKNOWN;
    mqtt_rx_init(&f->mqtt);
    hal_modem_power_set(false);
    hal_modem_pwrkey_set(false);
    hal_modem_reset_set(false);
}

void conn_fsm_tick(conn_fsm_t *f)
{
    at_msg_t m;

    while (at_link_poll(&m)) {
        on_message(f, &m);
    }

    uint32_t now = hal_now_ms();

    if (f->poll_period_ms != 0u && (uint32_t)(now - f->poll_last_ms) >= f->poll_period_ms) {
        f->poll_last_ms = now;
        if (f->state == CONN_NET_SEARCH) {
            at_link_send_line("AT+CEREG?");
            at_link_send_line("AT+CSQ");
        } else if (f->state == CONN_READY_TO_SEND && !f->ping_pending) {
            /* Keep-alive тримає відкритою трансляцію адрес у мережі оператора. */
            tx_frame(f, mqtt_pingreq(f->out, sizeof(f->out)));
            f->ping_pending = true;
            arm_timer(f, T_PING_RESP);
        }
    }

    /* Пін STATUS замість сліпого очікування фіксованої паузи. */
    if (f->state == CONN_POWERING_ON && f->substep == 2 && hal_modem_status_pin()) {
        enter(f, CONN_MODEM_READY, 0);
    }

    if (f->state == CONN_READY_TO_SEND && !f->ping_pending) {
        if (!f->tx_pending && f->log_pending) {
            /* Сесія жива — віддаємо чорну скриньку минулих аварій. */
            size_t n = blackbox_export(f->tx, sizeof(f->tx));
            if (n > 0) {
                f->tx_len = n;
                f->tx_pending = true;
                f->tx_is_log = true;
            } else {
                f->log_pending = false;
            }
        }
        if (f->tx_pending) {
            enter(f, CONN_SENDING, 0);
        } else if (f->want_disconnect) {
            f->want_disconnect = false;
            enter(f, CONN_DISCONNECTING, 0);
        }
    }

    if (f->timeout_ms != 0u && (uint32_t)(hal_now_ms() - f->enter_ms) >= f->timeout_ms) {
        on_timeout(f);
    }
}

void conn_fsm_connect(conn_fsm_t *f)
{
    if (f->state == CONN_NO_POWER) {
        enter(f, CONN_POWERING_ON, 0);
    } else if (f->state == CONN_PSM_SLEEP) {
        /* Реєстрацію та IP мережа тримала за нас: одразу відкриваємо сокет. */
        enter(f, CONN_TCP_CONNECT, 0);
    }
}

bool conn_fsm_submit(conn_fsm_t *f, const uint8_t *payload, size_t len)
{
    if (len == 0 || len > CONN_TX_MAX) {
        return false; /* краще відмовити явно, ніж мовчки різати кадр */
    }
    if (f->tx_pending) {
        return false; /* один кадр у польоті: черги під телеметрію тут немає */
    }
    memcpy(f->tx, payload, len);
    f->tx_len = len;
    f->tx_pending = true;
    f->tx_is_log = false;
    conn_fsm_connect(f);
    return true;
}

void conn_fsm_disconnect(conn_fsm_t *f)
{
    f->want_disconnect = true;
}

conn_state_t conn_fsm_state(const conn_fsm_t *f)
{
    return f->state;
}

bool conn_fsm_idle(const conn_fsm_t *f)
{
    return f->state == CONN_READY_TO_SEND && !f->tx_pending && !f->log_pending;
}
