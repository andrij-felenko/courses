/* service_engine.c — скінченний автомат сервісної консолі: приймання рядка,
   автентифікація «виклик — відповідь», таймери й аварійне знеструмлення.
   Динамічної пам'яті модуль не вживає взагалі: увесь стан — у g_srv. */

#include "service_engine.h"

#include <stdio.h>
#include <string.h>

#include "bist.h"
#include "hw_port.h"

#define CHALLENGE_TIMEOUT_MS 30000u  /* вікно на відповідь після виклику */
#define SESSION_TIMEOUT_MS   900000u /* 15 хвилин неактивності сесії */
#define MAX_ACT_TIMEOUT_S    15u
#define SRV_MAX_ERRORS       8u
#define CAL_EEPROM_BASE      0x0040u
#define ADC_VREF_MV          3300u
#define ADC_FULL_SCALE       4096u

/* Спільний секрет. У виробі його читають з OTP чи захищеної сторінки flash:
   у .rodata він живе рівно доти, доки хтось не зчитав образ прошивки. */
static const char SRV_SECRET[] = "SRV-2026-PLANT-KEY";

typedef struct {
    srv_state_t state;
    uint32_t    state_deadline; /* виклик 30 с або сесія 900 с */
    uint32_t    act_deadline;
    uint8_t     active_channel;
    uint32_t    current_nonce;
    uint32_t    fault_flags;
    bool        emergency_announced;
    uint8_t     err_count;
    int32_t     cal[SRV_CAL_SLOTS];

    /* Приймання. rx_* пише ISR, тому volatile. */
    volatile char     rx_buf[CLI_BUFFER_SIZE];
    volatile uint16_t rx_idx;
    volatile bool     rx_overflow;

    /* Готовий рядок для диспетчера. Поки line_ready == true, ISR його не чіпає. */
    char              line[CLI_BUFFER_SIZE];
    volatile bool     line_ready;
    volatile bool     line_overflow;
    volatile bool     line_lost;
} srv_context_t;

static srv_context_t g_srv;

/* Порівняння моментів різницею: працює і на переході лічильника через нуль. */
static bool reached(uint32_t now, uint32_t deadline)
{
    return (int32_t)(now - deadline) >= 0;
}

static const char *state_name(srv_state_t s)
{
    switch (s) {
    case SRV_STATE_LOCKED:            return "LOCKED";
    case SRV_STATE_CHALLENGE_ISSUED:  return "CHALLENGE";
    case SRV_STATE_UNLOCKED:          return "UNLOCKED";
    case SRV_STATE_ACTUATION_ACTIVE:  return "ACTUATION";
    case SRV_STATE_EMERGENCY:         return "EMERGENCY";
    }
    return "?";
}

static void prompt(void)
{
    if (g_srv.state == SRV_STATE_UNLOCKED || g_srv.state == SRV_STATE_ACTUATION_ACTIVE) {
        hw_uart_puts("SRV> ");
    }
}

/* Успіх скидає лічильник помилок і поновлює відлік сесії:
   «кожна валідна команда поновлює відлік». */
static void reply_ok(const char *s)
{
    g_srv.err_count = 0;
    if (g_srv.state == SRV_STATE_UNLOCKED || g_srv.state == SRV_STATE_ACTUATION_ACTIVE) {
        g_srv.state_deadline = hw_get_tick_ms() + SESSION_TIMEOUT_MS;
    }
    hw_uart_puts(s);
}

static void enter_locked(void)
{
    srv_emergency_all_off();
    g_srv.state = SRV_STATE_LOCKED;
    g_srv.current_nonce = 0;
}

static void reply_err(srv_err_t code, const char *text)
{
    char buf[80];
    snprintf(buf, sizeof buf, "-ERR: 0x%04X %s\r\n", (unsigned)code, text);
    hw_uart_puts(buf);

    /* Лічильник помилок переповнився: або лінія шумить, або хтось перебирає
       команди наосліп. Знеструмлюємо й вимагаємо нової автентифікації. */
    if (++g_srv.err_count >= SRV_MAX_ERRORS) {
        enter_locked();
        g_srv.err_count = 0;
        hw_uart_puts("[EVENT: ERROR_LIMIT_LOCKED]\r\n");
    }
}

/* ---- розбір аргументів -------------------------------------------------- */
/* Власний парсер чисел: sscanf тягне в образ кілька кілобайтів коду,
   а в деяких бібліотеках уміє смикнути malloc — у прошивці це зайве. */

static const char *skip_ws(const char *p)
{
    while (*p == ' ' || *p == '\t') {
        p++;
    }
    return p;
}

static bool parse_u32(const char **pp, uint32_t *out)
{
    const char *p = skip_ws(*pp);
    uint32_t    v = 0;

    if (*p < '0' || *p > '9') {
        return false;
    }
    while (*p >= '0' && *p <= '9') {
        uint32_t digit = (uint32_t)(*p - '0');
        if (v > (0xFFFFFFFFu - digit) / 10u) { /* переповнення */
            return false;
        }
        v = v * 10u + digit;
        p++;
    }
    *pp  = p;
    *out = v;
    return true;
}

static bool parse_i32(const char **pp, int32_t *out)
{
    const char *p = skip_ws(*pp);
    bool        neg = (*p == '-');
    uint32_t    mag = 0;

    if (neg || *p == '+') {
        p++;
    }
    if (!parse_u32(&p, &mag)) {
        return false;
    }
    if (mag > (neg ? 2147483648u : 2147483647u)) {
        return false;
    }
    *pp  = p;
    *out = neg ? -(int32_t)mag : (int32_t)mag;
    return true;
}

static bool end_of_args(const char *p)
{
    return *skip_ws(p) == '\0';
}

/* ---- автентифікація ----------------------------------------------------- */

static uint32_t fnv1a(const void *data, uint16_t len, uint32_t hash)
{
    const uint8_t *b = (const uint8_t *)data;
    for (uint16_t i = 0; i < len; i++) {
        hash ^= b[i];
        hash *= 16777619u;
    }
    return hash;
}

/* Очікувана відповідь на виклик. FNV-1a — НЕ криптографія: він показує форму
   обміну (nonce + секрет -> відповідь), а у виробі тут стоїть HMAC-SHA256. */
static void expected_response(uint32_t nonce, char out[9])
{
    uint32_t h = fnv1a(SRV_SECRET, (uint16_t)(sizeof SRV_SECRET - 1u), 2166136261u);
    h = fnv1a(&nonce, (uint16_t)sizeof nonce, h);
    snprintf(out, 9, "%08lX", (unsigned long)h);
}

/* Порівняння без ранньої відсічі: час відповіді не має підказувати,
   скільки символів ключа вгадано. */
static bool ct_equal(const char *a, const char *b, uint16_t n)
{
    uint8_t diff = 0;
    for (uint16_t i = 0; i < n; i++) {
        diff |= (uint8_t)(a[i] ^ b[i]);
    }
    return diff == 0;
}

/* ---- обробники команд --------------------------------------------------- */

static void cmd_sys_info(void)
{
    char buf[112];
    snprintf(buf, sizeof buf,
             "+OK: STATE=%s UPTIME=%lus FAULTS=0x%04lX ERRORS=%u\r\n",
             state_name(g_srv.state),
             (unsigned long)(hw_get_tick_ms() / 1000u),
             (unsigned long)g_srv.fault_flags,
             (unsigned)g_srv.err_count);
    reply_ok(buf);
}

static void cmd_auth_challenge(void)
{
    char buf[64];

    if (g_srv.state == SRV_STATE_UNLOCKED || g_srv.state == SRV_STATE_ACTUATION_ACTIVE) {
        reply_err(SRV_ERR_ACCESS_DENIED, "ALREADY_UNLOCKED");
        return;
    }
    g_srv.current_nonce  = hw_trng_get_random();
    g_srv.state          = SRV_STATE_CHALLENGE_ISSUED;
    g_srv.state_deadline = hw_get_tick_ms() + CHALLENGE_TIMEOUT_MS;

    snprintf(buf, sizeof buf, "+OK: CHALLENGE %08lX (ANSWER WITHIN 30 S)\r\n",
             (unsigned long)g_srv.current_nonce);
    reply_ok(buf);
}

static void cmd_auth_key(const char *args)
{
    const char *key = skip_ws(args);
    char        expected[9];

    if (g_srv.state != SRV_STATE_CHALLENGE_ISSUED) {
        reply_err(SRV_ERR_AUTH_FAILED, "NO_ACTIVE_CHALLENGE");
        return;
    }
    expected_response(g_srv.current_nonce, expected);
    if (strlen(key) != 8u || !ct_equal(key, expected, 8u)) {
        enter_locked(); /* одна хиба — і виклик згорає */
        reply_err(SRV_ERR_AUTH_FAILED, "AUTH_FAILED");
        return;
    }
    g_srv.state          = SRV_STATE_UNLOCKED;
    g_srv.state_deadline = hw_get_tick_ms() + SESSION_TIMEOUT_MS;
    g_srv.current_nonce  = 0; /* одноразовий: повтор того самого рядка не пройде */
    reply_ok("+OK: SERVICE_UNLOCKED (SESSION 15 MIN)\r\n");
}

static void cmd_diag_selftest(void)
{
    bist_report_t rep;
    char          buf[128];

    if (!bist_run(&rep)) {
        reply_err(SRV_ERR_BUS_BUSY, "I2C_BUS_BUSY");
        return;
    }
    snprintf(buf, sizeof buf,
             "+OK: BIST (BUS:%s, RTC:%s, EEPROM:%s, ADC0_RAW:0x%04X, ADC0_MV:%u)\r\n",
             rep.bus_free ? "FREE" : "STUCK",
             rep.rtc_ok ? "OK" : "FAULT",
             rep.eeprom_ok ? "OK" : "FAULT",
             (unsigned)rep.adc0_raw,
             (unsigned)rep.adc0_mv);
    reply_ok(buf);
}

static void cmd_diag_adc(const char *args)
{
    const char *p = args;
    uint32_t    ch = 0;
    uint16_t    raw;
    int32_t     mv;
    char        buf[80];

    if (!parse_u32(&p, &ch) || !end_of_args(p)) {
        reply_err(SRV_ERR_BAD_ARGUMENTS, "USAGE: diag adc <ch>");
        return;
    }
    if (ch > 7u) {
        reply_err(SRV_ERR_BAD_CHANNEL, "INVALID_CHANNEL (0..7)");
        return;
    }
    raw = hw_adc_read_raw((uint8_t)ch);
    mv  = (int32_t)(((uint32_t)raw * ADC_VREF_MV) / ADC_FULL_SCALE);
    if (ch < SRV_CAL_SLOTS) {
        mv += g_srv.cal[ch]; /* зсув нуля з калібрування */
    }
    snprintf(buf, sizeof buf, "+OK: ADC%lu RAW=0x%04X MV=%ld\r\n",
             (unsigned long)ch, (unsigned)raw, (long)mv);
    reply_ok(buf);
}

static void cmd_diag_act_relay(const char *args)
{
    const char *p   = args;
    uint32_t    ch  = 0;
    uint32_t    sec = 0;
    char        buf[72];

    if (!parse_u32(&p, &ch) || !parse_u32(&p, &sec) || !end_of_args(p)) {
        reply_err(SRV_ERR_BAD_ARGUMENTS, "USAGE: diag act relay <ch> <sec>");
        return;
    }
    if (ch < 1u || ch > HW_RELAY_COUNT) {
        reply_err(SRV_ERR_BAD_CHANNEL, "INVALID_CHANNEL");
        return;
    }
    if (sec == 0u || sec > MAX_ACT_TIMEOUT_S) {
        reply_err(SRV_ERR_BAD_TIMEOUT, "TIMEOUT_OUT_OF_RANGE (1..15 S)");
        return;
    }
    if (g_srv.fault_flags != 0u) {
        reply_err(SRV_ERR_HW_FAULT, "FAULT_LATCHED");
        return;
    }

    srv_emergency_all_off(); /* два канали одночасно не вмикаємо */
    /* Таймер зводимо ДО подачі напруги: інакше скидання між двома рядками
       лишило б реле ввімкненим без жодного відліку. */
    g_srv.act_deadline    = hw_get_tick_ms() + sec * 1000u;
    g_srv.active_channel  = (uint8_t)ch;
    g_srv.state           = SRV_STATE_ACTUATION_ACTIVE;
    hw_gpio_set_relay((uint8_t)ch, true);

    snprintf(buf, sizeof buf, "+OK: RELAY_%lu ACTIVE FOR %lu SEC\r\n",
             (unsigned long)ch, (unsigned long)sec);
    reply_ok(buf);
}

static void cmd_cal_get(void)
{
    char   buf[96];
    size_t used;
    int    n = snprintf(buf, sizeof buf, "+OK: CAL");

    if (n < 0) {
        return;
    }
    used = (size_t)n;
    for (uint8_t i = 0; i < SRV_CAL_SLOTS; i++) {
        n = snprintf(buf + used, sizeof buf - used, " %u=%ldMV",
                     (unsigned)i, (long)g_srv.cal[i]);
        if (n < 0 || (size_t)n >= sizeof buf - used) {
            break;
        }
        used += (size_t)n;
    }
    snprintf(buf + used, sizeof buf - used, "\r\n"); /* місце під це лишили */
    reply_ok(buf);
}

static void cmd_cal_set(const char *args)
{
    const char *p     = args;
    uint32_t    slot  = 0;
    int32_t     value = 0;
    char        buf[64];

    if (!parse_u32(&p, &slot) || !parse_i32(&p, &value) || !end_of_args(p)) {
        reply_err(SRV_ERR_BAD_ARGUMENTS, "USAGE: cal set <slot> <mv>");
        return;
    }
    if (slot >= SRV_CAL_SLOTS) {
        reply_err(SRV_ERR_BAD_CHANNEL, "INVALID_SLOT (0..3)");
        return;
    }
    if (value < -500 || value > 500) {
        reply_err(SRV_ERR_BAD_TIMEOUT, "CAL_OUT_OF_RANGE (-500..500 MV)");
        return;
    }
    g_srv.cal[slot] = value;
    if (!hw_eeprom_write((uint16_t)(CAL_EEPROM_BASE + slot * sizeof(int32_t)),
                         &g_srv.cal[slot], (uint16_t)sizeof(int32_t))) {
        reply_err(SRV_ERR_EEPROM_WRITE, "EEPROM_WRITE_FAILED");
        return;
    }
    snprintf(buf, sizeof buf, "+OK: CAL %lu=%ldMV STORED\r\n",
             (unsigned long)slot, (long)value);
    reply_ok(buf);
}

/* ---- диспетчер ---------------------------------------------------------- */

static void dispatch_line(const char *cmd)
{
    /* В аварії лишається одна команда — подивитися, що саме спрацювало. */
    if (g_srv.state == SRV_STATE_EMERGENCY) {
        if (strcmp(cmd, "sys info") == 0) {
            cmd_sys_info();
        } else {
            reply_err(SRV_ERR_HW_FAULT, "EMERGENCY_POWER_CYCLE_REQUIRED");
        }
        return;
    }

    if (strcmp(cmd, "sys info") == 0) {
        cmd_sys_info();
        return;
    }
    if (strcmp(cmd, "auth challenge") == 0) {
        cmd_auth_challenge();
        return;
    }
    if (strncmp(cmd, "auth key ", 9) == 0) {
        cmd_auth_key(cmd + 9);
        return;
    }

    if (g_srv.state != SRV_STATE_UNLOCKED && g_srv.state != SRV_STATE_ACTUATION_ACTIVE) {
        reply_err(SRV_ERR_LOCKED, "LOCKED_ENTER_AUTH_FIRST");
        return;
    }

    if (strcmp(cmd, "sys lock") == 0) {
        enter_locked();
        reply_ok("+OK: SERVICE_LOCKED\r\n");
        return;
    }
    if (strcmp(cmd, "diag act off") == 0) {
        srv_emergency_all_off();
        reply_ok("+OK: ALL_OUTPUTS_OFF\r\n");
        return;
    }

    /* Поки навантаження під напругою, приймаємо лише те, що його знімає. */
    if (g_srv.state == SRV_STATE_ACTUATION_ACTIVE) {
        reply_err(SRV_ERR_ACT_ACTIVE, "ACTUATION_ACTIVE_USE_ACT_OFF");
        return;
    }

    if (strcmp(cmd, "diag selftest") == 0) {
        cmd_diag_selftest();
    } else if (strncmp(cmd, "diag adc ", 9) == 0) {
        cmd_diag_adc(cmd + 9);
    } else if (strncmp(cmd, "diag act relay ", 15) == 0) {
        cmd_diag_act_relay(cmd + 15);
    } else if (strcmp(cmd, "cal get") == 0) {
        cmd_cal_get();
    } else if (strncmp(cmd, "cal set ", 8) == 0) {
        cmd_cal_set(cmd + 8);
    } else {
        reply_err(SRV_ERR_UNKNOWN_CMD, "UNKNOWN_COMMAND");
    }
}

/* ---- публічний інтерфейс ------------------------------------------------ */

void srv_emergency_all_off(void)
{
    /* Пряма робота з GPIO: ні черг, ні перевірок стану автомата — ця функція
       мусить спрацювати навіть із зіпсованим контекстом. */
    for (uint8_t ch = 1; ch <= HW_RELAY_COUNT; ch++) {
        hw_gpio_set_relay(ch, false);
    }
    g_srv.active_channel = 0;
    g_srv.act_deadline   = 0;
    if (g_srv.state == SRV_STATE_ACTUATION_ACTIVE) {
        g_srv.state = SRV_STATE_UNLOCKED;
    }
}

void srv_fault_trip(uint32_t flags)
{
    /* Контекст ISR: гасимо виходи й фіксуємо причину. Друкувати звідси не
       можна — повідомлення видасть srv_poll_step() у своєму контексті. */
    for (uint8_t ch = 1; ch <= HW_RELAY_COUNT; ch++) {
        hw_gpio_set_relay(ch, false);
    }
    g_srv.active_channel      = 0;
    g_srv.fault_flags        |= flags;
    g_srv.state               = SRV_STATE_EMERGENCY;
    g_srv.emergency_announced = false;
}

void srv_init(void)
{
    memset(&g_srv, 0, sizeof g_srv);
    g_srv.state = SRV_STATE_LOCKED;

    for (uint8_t ch = 1; ch <= HW_RELAY_COUNT; ch++) {
        hw_gpio_set_relay(ch, false);
    }
    for (uint8_t i = 0; i < SRV_CAL_SLOTS; i++) {
        int32_t stored = 0;
        if (hw_eeprom_read((uint16_t)(CAL_EEPROM_BASE + i * sizeof(int32_t)),
                           &stored, (uint16_t)sizeof stored)
            && stored >= -500 && stored <= 500) {
            g_srv.cal[i] = stored; /* сміття з чистої EEPROM просто ігноруємо */
        }
    }
    hw_uart_puts("\r\n[SERVICE ENGINE READY - 'auth challenge' TO START]\r\n");
}

void srv_feed_byte(char c)
{
    if (c == '\r' || c == '\n') {
        if (g_srv.rx_idx == 0 && !g_srv.rx_overflow) {
            return; /* порожній рядок — просто Enter */
        }
        if (g_srv.line_ready) {
            /* Диспетчер ще не забрав попередній рядок: новий втрачаємо
               свідомо, бо переписувати буфер під ним не можна. */
            g_srv.line_lost = true;
        } else {
            for (uint16_t i = 0; i < g_srv.rx_idx; i++) {
                g_srv.line[i] = g_srv.rx_buf[i];
            }
            g_srv.line[g_srv.rx_idx] = '\0';
            g_srv.line_overflow      = g_srv.rx_overflow;
            g_srv.line_ready         = true;
        }
        g_srv.rx_idx      = 0;
        g_srv.rx_overflow = false;
        return;
    }

    if (c < 0x20 || c > 0x7E) {
        return; /* керуючі символи й брязкіт лінії відкидаємо */
    }
    if (g_srv.rx_idx < (CLI_BUFFER_SIZE - 1)) {
        g_srv.rx_buf[g_srv.rx_idx++] = c;
    } else {
        g_srv.rx_overflow = true; /* індекс став на 127 і далі не рухається */
    }
}

void srv_poll_step(void)
{
    uint32_t now    = hw_get_tick_ms();
    uint32_t faults = hw_fault_flags();

    if (faults != 0u && g_srv.state != SRV_STATE_EMERGENCY) {
        srv_fault_trip(faults);
    }
    if (g_srv.state == SRV_STATE_EMERGENCY && !g_srv.emergency_announced) {
        char buf[96];
        snprintf(buf, sizeof buf,
                 "\r\n[EVENT: EMERGENCY_STOP FLAGS=0x%04lX - POWER CYCLE REQUIRED]\r\n",
                 (unsigned long)g_srv.fault_flags);
        hw_uart_puts(buf);
        g_srv.emergency_announced = true;
    }

    if (g_srv.state == SRV_STATE_ACTUATION_ACTIVE && reached(now, g_srv.act_deadline)) {
        srv_emergency_all_off(); /* повертає автомат в UNLOCKED */
        hw_uart_puts("\r\n[EVENT: ACTUATION_TIMEOUT_AUTO_SHUTDOWN]\r\n");
        prompt();
    }
    if (g_srv.state == SRV_STATE_CHALLENGE_ISSUED && reached(now, g_srv.state_deadline)) {
        enter_locked();
        hw_uart_puts("\r\n[EVENT: CHALLENGE_EXPIRED_LOCKED]\r\n");
    }
    if ((g_srv.state == SRV_STATE_UNLOCKED || g_srv.state == SRV_STATE_ACTUATION_ACTIVE)
        && reached(now, g_srv.state_deadline)) {
        enter_locked();
        hw_uart_puts("\r\n[EVENT: SESSION_TIMEOUT_LOCKED]\r\n");
    }

    if (g_srv.line_lost) {
        g_srv.line_lost = false;
        reply_err(SRV_ERR_INPUT_OVERRUN, "INPUT_OVERRUN_LINE_DROPPED");
    }
    if (!g_srv.line_ready) {
        return;
    }
    if (g_srv.line_overflow) {
        g_srv.line_overflow = false;
        reply_err(SRV_ERR_LINE_TOO_LONG, "LINE_TOO_LONG (MAX 127)");
    } else {
        dispatch_line(g_srv.line);
    }
    /* Прапорець знімаємо ПІСЛЯ розбору: доти ISR не має права торкатися line. */
    g_srv.line_ready = false;
    prompt();
}

srv_state_t srv_get_state(void)
{
    return g_srv.state;
}

int32_t srv_get_cal(uint8_t slot)
{
    return (slot < SRV_CAL_SLOTS) ? g_srv.cal[slot] : 0;
}
