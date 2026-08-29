#include "actuator.h"

#include "link.h"

#include <string.h>

#define INBOX_SIZE         4
#define MOVE_TIMEOUT_MS    6000u
#define PROGRESS_PERIOD_MS 500u
#define POS_TOLERANCE_PCT  2

#define PERSIST_MAGIC 0x5A11C0DEu

/* Ця структура в прошивці лежить у RTC-пам'яті (RTC_NOINIT_ATTR) або в секції
   .noinit: вона переживає скидання по просіданню живлення, а RAM — ні.
   Саме з неї після перезапуску видно, що вал лишився посеред ходу. */
typedef struct {
    uint32_t magic;
    char     cmd_id[CMD_ID_MAX_LEN];
    int      target_pct;
    uint8_t  in_flight;
} act_persist_t;

static act_persist_t s_persist;

/* Інбокс воркера: пише мережевий колбек, читає цикл приводу. На FreeRTOS тут
   стоїть пара xQueueSend/xQueueReceive — той самий кільцевий буфер на одного
   письменника й одного читача, тільки з примітивами ядра. */
static act_job_t        s_inbox[INBOX_SIZE];
static volatile uint8_t s_in_head;
static volatile uint8_t s_in_tail;

static bool     s_moving;
static char     s_cmd_id[CMD_ID_MAX_LEN];
static int      s_target_pct;
static int      s_start_pct;
static uint32_t s_started_ms;
static uint32_t s_last_report_ms;

static void copy_str(char *dst, size_t cap, const char *src)
{
    size_t n = 0;
    while (src[n] != '\0' && n + 1 < cap) {
        dst[n] = src[n];
        ++n;
    }
    dst[n] = '\0';
}

/* Кінцевики точніші за датчик: у крайніх положеннях віримо їм. */
static int read_position(void)
{
    if (hal_limit_closed()) {
        return 0;
    }
    if (hal_limit_open()) {
        return 100;
    }
    return hal_position_pct();
}

static bool reached(int pos)
{
    if (s_target_pct <= 0) {
        return hal_limit_closed() || pos <= POS_TOLERANCE_PCT;
    }
    if (s_target_pct >= 100) {
        return hal_limit_open() || pos >= 100 - POS_TOLERANCE_PCT;
    }
    {
        int delta = pos - s_target_pct;
        if (delta < 0) {
            delta = -delta;
        }
        return delta <= POS_TOLERANCE_PCT;
    }
}

static int progress_pct(int pos)
{
    int span = s_target_pct - s_start_pct;
    int moved = pos - s_start_pct;
    int pct;

    if (span < 0) {
        span = -span;
    }
    if (moved < 0) {
        moved = -moved;
    }
    if (span == 0) {
        return 100;
    }
    pct = (moved * 100) / span;
    if (pct < 0) {
        pct = 0;
    }
    if (pct > 99) {
        pct = 99;      /* сто відсотків ставить лише справжнє завершення */
    }
    return pct;
}

static void report(const char *state, int progress, int value, int err)
{
    link_publish_status(s_cmd_id, state, progress, value, err);
    dedup_update(s_cmd_id, state, progress, value, err);
}

static void finish(const char *state, int progress, int pos, int err)
{
    hal_drive_stop();
    s_persist.in_flight = 0;
    s_moving = false;
    report(state, progress, pos, err);
}

void actuator_init(uint32_t now_ms)
{
    int pos;

    s_in_head = 0;
    s_in_tail = 0;
    s_moving = false;
    s_last_report_ms = now_ms;
    hal_drive_stop();

    pos = read_position();
    if (s_persist.magic == PERSIST_MAGIC && s_persist.in_flight) {
        /* Плату перезавантажило посеред маневру. Кінцевики кажуть, де вал
           опинився насправді, і сервер мусить дізнатися про незакритий хід —
           інакше транзакція висітиме в панелі до таймауту. */
        link_publish_status(s_persist.cmd_id, "FAILED", 0, pos, ERR_HARDWARE_FAULT);
        dedup_update(s_persist.cmd_id, "FAILED", 0, pos, ERR_HARDWARE_FAULT);
        s_persist.in_flight = 0;
    }
    s_persist.magic = PERSIST_MAGIC;
}

bool actuator_submit(const act_job_t *job)
{
    uint8_t next = (uint8_t)((s_in_head + 1u) % INBOX_SIZE);

    if (next == s_in_tail) {
        return false;
    }
    s_inbox[s_in_head] = *job;
    s_in_head = next;          /* індекс рухаємо ОСТАННІМ: читач не побачить недописаного */
    return true;
}

bool actuator_busy(void)
{
    return s_moving || s_in_head != s_in_tail;
}

int actuator_position(void)
{
    return read_position();
}

static bool take_job(act_job_t *out)
{
    if (s_in_tail == s_in_head) {
        return false;
    }
    *out = s_inbox[s_in_tail];
    s_in_tail = (uint8_t)((s_in_tail + 1u) % INBOX_SIZE);
    return true;
}

static void begin(const act_job_t *job, uint32_t now_ms)
{
    copy_str(s_cmd_id, sizeof s_cmd_id, job->cmd_id);
    s_target_pct = job->target_pct;
    s_start_pct = read_position();
    s_started_ms = now_ms;
    s_last_report_ms = now_ms;
    s_moving = true;

    copy_str(s_persist.cmd_id, sizeof s_persist.cmd_id, job->cmd_id);
    s_persist.target_pct = job->target_pct;
    s_persist.in_flight = 1;

    hal_drive_set(s_target_pct);
    report("STARTED", 0, s_start_pct, ERR_NONE);
}

void actuator_poll(uint32_t now_ms)
{
    int pos;

    if (!s_moving) {
        act_job_t job;
        if (take_job(&job)) {
            begin(&job, now_ms);
        }
        return;
    }

    pos = read_position();
    if (reached(pos)) {
        finish("COMPLETED", 100, pos, ERR_NONE);
        return;
    }
    if (now_ms - s_started_ms >= MOVE_TIMEOUT_MS) {
        /* Вал не дійшов за відведений час: заклинило, зрив муфти, обрив драйвера. */
        finish("FAILED", progress_pct(pos), pos, ERR_HARDWARE_FAULT);
        return;
    }
    if (now_ms - s_last_report_ms >= PROGRESS_PERIOD_MS) {
        s_last_report_ms = now_ms;
        report("IN_PROGRESS", progress_pct(pos), pos, ERR_NONE);
    }
}
