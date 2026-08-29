#include "at_engine.h"

#include <stdlib.h>
#include <string.h>

const char *at_state_str(at_engine_state_t state)
{
    switch (state) {
        case AT_STATE_IDLE:                return "IDLE";
        case AT_STATE_SEND:                return "SEND";
        case AT_STATE_WAIT_PROMPT:         return "WAIT_PROMPT";
        case AT_STATE_WAIT_RESPONSE:       return "WAIT_RESPONSE";
        case AT_STATE_RETRY_DELAY:         return "RETRY_DELAY";
        case AT_STATE_TIMEOUT_ESCALATION:  return "TIMEOUT_ESCALATION";
        default:                           return "?";
    }
}

static bool starts_with(const char *line, const char *prefix)
{
    return strncmp(line, prefix, strlen(prefix)) == 0;
}

/* Різниця беззнакових обгортається сама, тож переповнення SysTick через
   49.7 доби не робить таймаут ні вічним, ні миттєвим. */
static bool elapsed(uint32_t now, uint32_t start, uint32_t limit)
{
    return (uint32_t)(now - start) >= limit;
}

/* Тимчасова помилка означає «спробуй ще», остаточна — «не буде». Голе ERROR
   завжди остаточне: повторювати синтаксично неправильну команду безглуздо. */
static bool error_is_temporary(const char *line)
{
    static const long temporary_codes[] = {
        3,    /* operation not allowed — стек мережі ще піднімається */
        14,   /* SIM busy — картка зайнята внутрішньою операцією */
        100,  /* unknown — модуль ще не готовий відповісти по суті */
    };

    const char *colon = strstr(line, "ERROR:");
    if (colon == NULL) {
        return false;
    }
    const char *p = colon + strlen("ERROR:");
    while (*p == ' ') {
        p++;
    }

    char *end = NULL;
    const long code = strtol(p, &end, 10);
    if (end == p) {
        return false; /* текстовий опис замість коду (+CME ERROR: SIM busy) */
    }

    for (size_t i = 0U; i < sizeof(temporary_codes) / sizeof(temporary_codes[0]); ++i) {
        if (temporary_codes[i] == code) {
            return true;
        }
    }
    return false;
}

bool at_engine_init(at_engine_t *eng, const at_engine_hooks_t *hooks)
{
    if (eng == NULL || hooks == NULL ||
        hooks->uart_tx == NULL || hooks->tick_ms == NULL) {
        return false;
    }

    memset(eng, 0, sizeof(*eng));
    at_ring_init(&eng->rx);
    at_queue_init(&eng->queue);
    at_urc_init(&eng->urc);

    eng->hooks = *hooks;
    eng->state = AT_STATE_IDLE;
    /* Після подачі живлення модуль майже завжди в ATE1 — вважаємо луну
       ввімкненою, поки ATE0 не підтвердиться. */
    eng->echo_active = true;
    return true;
}

bool at_engine_register_urc(at_engine_t *eng, const char *prefix,
                            at_urc_cb_t handler, void *ctx)
{
    return at_urc_register(&eng->urc, prefix, handler, ctx);
}

bool at_engine_send_cmd(at_engine_t *eng, const at_request_t *req)
{
    return at_queue_push(&eng->queue, req);
}

/* ---- завершення команди ------------------------------------------------ */

static void finish(at_engine_t *eng, at_status_t status, const char *resp)
{
    at_cmd_t done_cmd = eng->cmd;   /* копія: колбек має право одразу класти
                                       нову команду й крутити чергу */
    memset(&eng->cmd, 0, sizeof(eng->cmd));
    eng->state = AT_STATE_IDLE;

    if (status == AT_STATUS_OK) {
        eng->consecutive_timeouts = 0U;
        /* Луна вимикається лише за підтвердженим ATE0: доти парсер
           зобов'язаний відкидати рядки, рівні надісланій команді. */
        if (strcmp(done_cmd.text, "ATE0") == 0) {
            eng->echo_active = false;
        }
    }

    if (done_cmd.done != NULL) {
        done_cmd.done(status, resp, done_cmd.ctx);
    }
}

static void schedule_retry(at_engine_t *eng, uint32_t now)
{
    eng->cmd.attempt = (uint8_t)(eng->cmd.attempt + 1U);
    eng->stats.retries++;
    /* Тіло попередньої спроби більше не наше. Не скинути його — означає
       віддати в колбек повтору рядок, якого модуль на цю спробу не присилав:
       "+CSQ: 24,99" з невдалої спроби виглядав би як свіжий рівень сигналу. */
    eng->resp_line[0] = '\0';
    eng->timer_start_ms = now;
    eng->state = AT_STATE_RETRY_DELAY;
}

static bool retries_left(const at_engine_t *eng)
{
    return eng->cmd.attempt < eng->cmd.max_retries;
}

static void abort_queue(at_engine_t *eng)
{
    /* Скільки саме скасовувати — вирішуємо ДО першого колбека. Обробник
       ABORTED має повне право поставити свою команду наново, і звичайний
       «викачуй, поки черга не порожня» ковтав би її знову й знову. */
    uint8_t victims = at_queue_count(&eng->queue);
    at_cmd_t victim;

    while (victims > 0U && at_queue_pop(&eng->queue, &victim)) {
        victims--;
        if (victim.done != NULL) {
            victim.done(AT_STATUS_ABORTED, NULL, victim.ctx);
        }
    }
}

static void escalate(at_engine_t *eng, uint16_t head)
{
    /* У буфері лишився хвіст напівприйнятої відповіді. Якщо його не викинути,
       він зсуне розбір наступної команди на одну відповідь уперед. */
    at_ring_flush(&eng->rx, head);

    eng->stats.timeouts++;
    eng->consecutive_timeouts = (uint8_t)(eng->consecutive_timeouts + 1U);

    const bool stuck = (eng->consecutive_timeouts >= AT_TIMEOUT_ESCALATION_LIMIT);

    if (stuck) {
        /* Модуль вважається завислим. Тримати чергу немає сенсу: кожен, хто
           чекає, дістає ABORTED — інакше прикладний код залишиться з
           «висячою» операцією назавжди.

           Чергу згортаємо ДО колбека таймауту, а не після. Порядок тут не
           косметичний: колбек майже завжди ставить у чергу відновлювальну
           команду, і скасування, виконане після нього, викинуло б саме її —
           тобто вбило б ту єдину спробу, заради якої аварію й обробляють. */
        abort_queue(eng);
        eng->consecutive_timeouts = 0U;
        eng->echo_active = true;    /* після PWRKEY модуль знову в ATE1 */
        eng->stats.recoveries++;
    }

    finish(eng, AT_STATUS_TIMEOUT, NULL);   /* переводить у IDLE */

    /* Смикати живлення — теж після колбека: гачок має право покласти власну
       стартову послідовність, і вона мусить лягти на вже порожню чергу. */
    if (stuck && eng->hooks.on_module_stuck != NULL) {
        eng->hooks.on_module_stuck(eng->hooks.ctx);
    }
}

/* ---- розбір рядка у контексті активної команди ------------------------- */

static void on_line(at_engine_t *eng, const char *line, uint32_t now)
{
    if (eng->state != AT_STATE_WAIT_RESPONSE && eng->state != AT_STATE_WAIT_PROMPT) {
        /* Рядок поза контекстом: спізніла відповідь на команду, яку ми вже
           закрили за таймаутом. Тихо викидаємо. */
        eng->stats.orphan_lines++;
        return;
    }

    if (eng->echo_active && strcmp(line, eng->cmd.text) == 0) {
        eng->stats.echo_dropped++;
        return;
    }

    /* Помилка розглядається першою й однаково в обох станах очікування.
       На AT+QISEND у закритий сокет модуль відповідає простим "ERROR" і
       запрошення не надсилає ВЗАГАЛІ — рушій, який у стані WAIT_PROMPT
       дивиться самі лише сирі байти, простояв би тут увесь таймаут. */
    if (strcmp(line, "ERROR") == 0 ||
        starts_with(line, "+CME ERROR:") ||
        starts_with(line, "+CMS ERROR:")) {
        if (error_is_temporary(line) && retries_left(eng)) {
            schedule_retry(eng, now);
        } else {
            finish(eng, AT_STATUS_ERROR, line);
        }
        return;
    }

    if (eng->state == AT_STATE_WAIT_PROMPT) {
        /* Усе інше до запрошення — шум: тіла відповіді тут не буває, а
           фінальне "OK" приходить уже після відправлених сирих байтів. */
        return;
    }

    if (strcmp(line, "OK") == 0 || strcmp(line, "SEND OK") == 0) {
        finish(eng, AT_STATUS_OK, (eng->resp_line[0] != '\0') ? eng->resp_line : NULL);
        return;
    }

    /* Не фінальний маркер — тіло відповіді. Коли префікс заявлено, беремо
       лише його; коли ні — тримаємо останній змістовний рядок. */
    if (eng->cmd.expect_prefix[0] != '\0' && !starts_with(line, eng->cmd.expect_prefix)) {
        return;
    }
    strncpy(eng->resp_line, line, sizeof(eng->resp_line) - 1U);
    eng->resp_line[sizeof(eng->resp_line) - 1U] = '\0';
}

/* ---- фаза 1: вичитка буфера -------------------------------------------- */

static void pump_rx(at_engine_t *eng, uint16_t head, uint32_t now)
{
    char line[AT_MAX_LINE_SIZE];
    for (;;) {
        const at_line_status_t st = at_ring_read_line(&eng->rx, head, line, sizeof(line));

        if (st == AT_LINE_NONE) {
            break;
        }
        if (st == AT_LINE_OVERFLOW) {
            eng->stats.overflows++;
            continue;
        }
        if (st == AT_LINE_EMPTY) {
            continue;   /* порожні роздільники всередині відповіді */
        }

        eng->stats.lines_in++;

        /* URC має пріоритет над контекстом команди: розрив сокета може
           прийти рівно між рядками очікуваної відповіді. */
        if (at_urc_dispatch(&eng->urc, line)) {
            eng->stats.urc_lines++;
            continue;
        }

        on_line(eng, line, now);
    }

    /* Запрошення '>' не завершується переводом рядка, тож лінійний екстрактор
       його не побачить ніколи — сирі байти добираємо окремо, і саме ПІСЛЯ
       рядків. Порядок тут робить дві речі. По-перше, перед запрошенням у
       дроті стоять "\r\n" і луна команди — вони мусять поїхати як рядки.
       По-друге, шукати '>' наосліп по всьому буферу небезпечно: символ
       трапляється всередині URC, і сліпий пошук з'їв би повідомлення разом
       із ним. Після вичитки рядків у буфері лишається тільки незавершений
       хвіст — рівно те місце, де запрошення й живе. */
    if (eng->state == AT_STATE_WAIT_PROMPT) {
        if (at_ring_take_upto(&eng->rx, head, AT_PROMPT_CHAR)) {
            eng->hooks.uart_tx(eng->cmd.payload, eng->cmd.payload_len);
            eng->timer_start_ms = now;
            eng->state = AT_STATE_WAIT_RESPONSE;
        }
    }
}

/* ---- фаза 2: автомат керування чергою ---------------------------------- */

static void run_fsm(at_engine_t *eng, uint16_t head, uint32_t now)
{
    switch (eng->state) {
        case AT_STATE_IDLE:
            if (at_queue_pop(&eng->queue, &eng->cmd)) {
                eng->resp_line[0] = '\0';
                eng->state = AT_STATE_SEND;
            }
            break;

        case AT_STATE_SEND: {
            static const uint8_t crlf[2] = { '\r', '\n' };
            eng->hooks.uart_tx((const uint8_t *)eng->cmd.text, strlen(eng->cmd.text));
            eng->hooks.uart_tx(crlf, sizeof(crlf));
            eng->timer_start_ms = now;
            eng->state = eng->cmd.wait_prompt ? AT_STATE_WAIT_PROMPT : AT_STATE_WAIT_RESPONSE;
            break;
        }

        case AT_STATE_WAIT_PROMPT:
        case AT_STATE_WAIT_RESPONSE:
            if (elapsed(now, eng->timer_start_ms, eng->cmd.timeout_ms)) {
                if (retries_left(eng)) {
                    /* Хвіст відповіді, що не дійшла, для повтору вже сміття:
                       лишити його — значить прочитати шматок старої спроби
                       як початок нової. */
                    at_ring_flush(&eng->rx, head);
                    schedule_retry(eng, now);
                } else {
                    eng->state = AT_STATE_TIMEOUT_ESCALATION;
                }
            }
            break;

        case AT_STATE_RETRY_DELAY:
            if (elapsed(now, eng->timer_start_ms, AT_RETRY_DELAY_MS)) {
                eng->state = AT_STATE_SEND;
            }
            break;

        case AT_STATE_TIMEOUT_ESCALATION:
            escalate(eng, head);
            break;

        default:
            eng->state = AT_STATE_IDLE;
            break;
    }
}

void at_engine_poll(at_engine_t *eng, uint16_t dma_cndtr)
{
    const uint32_t now  = eng->hooks.tick_ms();
    const uint16_t head = at_ring_head(dma_cndtr);

    pump_rx(eng, head, now);
    run_fsm(eng, head, now);
}
