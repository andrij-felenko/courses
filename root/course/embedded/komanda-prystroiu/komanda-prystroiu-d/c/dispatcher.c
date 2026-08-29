#include "dispatcher.h"
#include "actuator.h"
#include "journal.h"
#include "platform.h"

#include <stdio.h>
#include <string.h>

/* ─────────────────────────── квитанції ─────────────────────────── */

static void emit_ack(uint8_t phase, const cmd_record_t *r) {
    ack_t a;
    a.token  = r->token;
    a.phase  = phase;
    a.state  = r->state;
    a.result = r->result;
    a.detail = r->detail;

    uint8_t frame[ACK_FRAME_LEN];
    size_t n = wire_build_ack(&a, frame, sizeof(frame));
    if (n > 0) plat_uplink_send(frame, n);
}

/* ─────────────────────── кільце ідемпотентності ─────────────────── */

static cmd_record_t *ring_find(dispatcher_t *d, uint64_t token) {
    for (uint8_t i = 0; i < RING_SIZE; ++i) {
        if (d->ring[i].state != ST_FREE && d->ring[i].token == token) {
            return &d->ring[i];
        }
    }
    return NULL;
}

/* Витіснення найстарішого слота. Слоти незавершених команд (у черзі або в
 * роботі) пропускаємо: на них посилається черга виконання, і затерти такий
 * слот означало б загубити команду посеред руху приводу. */
static int ring_alloc(dispatcher_t *d) {
    for (uint8_t n = 0; n < RING_SIZE; ++n) {
        uint8_t i = (uint8_t)((d->ring_head + n) % RING_SIZE);
        uint8_t st = d->ring[i].state;
        if (st == ST_ACCEPTED || st == ST_EXECUTING) continue;

        d->ring_head = (uint8_t)((i + 1u) % RING_SIZE);
        memset(&d->ring[i], 0, sizeof(d->ring[i]));
        return (int)i;
    }
    return -1;
}

/* ───────────────────────── черга виконання ──────────────────────── */

static bool queue_push(dispatcher_t *d, uint8_t slot) {
    if (d->q_count >= QUEUE_SIZE) return false;
    d->queue[(d->q_head + d->q_count) % QUEUE_SIZE] = slot;
    d->q_count++;
    return true;
}

static bool queue_pop(dispatcher_t *d, uint8_t *slot) {
    if (d->q_count == 0) return false;
    *slot = d->queue[d->q_head];
    d->q_head = (uint8_t)((d->q_head + 1u) % QUEUE_SIZE);
    d->q_count--;
    return true;
}

/* Чи є далі в черзі свіжіша команда того самого призначення. Для абсолютних
 * команд («встановити стан», «їхати в позицію») виконувати застарілу — це
 * марний знос механіки: залп після сну інакше проганяє заслінку туди-сюди. */
static bool superseded_later(const dispatcher_t *d, const cmd_record_t *r) {
    if (r->type != CMD_SET_RELAY && r->type != CMD_GOTO_POS) return false;

    for (uint8_t n = 0; n < d->q_count; ++n) {
        const cmd_record_t *o = &d->ring[d->queue[(d->q_head + n) % QUEUE_SIZE]];
        if (o->state != ST_ACCEPTED || o->type != r->type) continue;
        if (r->type == CMD_SET_RELAY) {
            if (o->payload_len < 1 || r->payload_len < 1) continue;
            if (o->payload[0] != r->payload[0]) continue;   /* інший канал реле */
        }
        return true;
    }
    return false;
}

/* ───────────────────────────── прийом ───────────────────────────── */

void dispatcher_init(dispatcher_t *d) {
    memset(d, 0, sizeof(*d));
    d->active = -1;
}

cmd_err_t dispatcher_on_frame(dispatcher_t *d, const uint8_t *buf, size_t len) {
    cmd_frame_t f;
    cmd_err_t err = wire_parse_command(buf, len, &f);
    if (err != E_OK) {
        /* Квитанції немає навмисно: у битому кадрі й токен битий, відповідати
         * нема кому й нема на що. Сервер розбереться повтором. */
        d->stats.dropped++;
        printf("  --> [кадр %u B] відкинуто на вході: %s\n", (unsigned)len, cmd_err_name(err));
        return err;
    }

    printf("  --> %-11s token=0x%08lX seq=%u ttl=%u мс\n",
           cmd_type_name(f.type), (unsigned long)(f.token & 0xFFFFFFFFu),
           (unsigned)f.seq, (unsigned)f.ttl_ms);

    /* 1. Дедуплікація — ПЕРШОЮ, до перевірки лічильника. Легітимний повтор
     *    несе той самий seq, і перевірка порядку відкинула б його мовчки,
     *    залишивши сервер без квитанції назавжди. */
    cmd_record_t *dup = ring_find(d, f.token);
    if (dup != NULL) {
        d->stats.duplicates++;
        if (dup->state == ST_ACCEPTED || dup->state == ST_EXECUTING) {
            printf("      [дедуп] токен уже в роботі — залізо не чіпаємо\n");
            emit_ack(1, dup);
        } else {
            printf("      [дедуп] токен уже відпрацьовано — віддаємо збережений результат\n");
            emit_ack(2, dup);
        }
        return E_OK;
    }

    /* 2. Монотонний лічильник повідомлень: старий кадр із ефіру не пройде. */
    if (f.seq <= d->last_seq) {
        d->stats.replays++;
        printf("      [повтор] seq=%u не більший за вже прийнятий %u — кадр знищено\n",
               (unsigned)f.seq, (unsigned)d->last_seq);
        return E_REPLAY;
    }

    /* 3. Вхідний фільтр строку придатності. Шлюз віднімає час, проведений у
     *    своїй черзі, тож нульовий залишок означає прострочену команду. */
    uint32_t now = plat_now_ms();
    int slot_idx = ring_alloc(d);
    if (slot_idx < 0) {
        printf("      [кільце] вільних слотів немає — усі зайняті незавершеними командами\n");
        cmd_record_t tmp = { f.token, f.type, ST_FAILED, 0, {0}, now, now, E_NO_SLOT, 0 };
        emit_ack(2, &tmp);
        return E_NO_SLOT;
    }

    cmd_record_t *r = &d->ring[slot_idx];
    r->token       = f.token;
    r->type        = f.type;
    r->payload_len = f.payload_len;
    memcpy(r->payload, f.payload, f.payload_len);
    r->rx_time_ms  = now;
    r->deadline_ms = now + f.ttl_ms;
    r->result      = E_OK;
    r->detail      = 0;
    d->last_seq    = f.seq;

    if (f.ttl_ms == 0) {
        r->state  = ST_EXPIRED;
        r->result = E_EXPIRED;
        d->stats.expired++;
        printf("      [ttl] залишок нульовий — команда протухла ще в мережі\n");
        emit_ack(2, r);
        return E_EXPIRED;
    }

    /* 4. Фаза 1: пакет цілий, токен зафіксовано, команда прийнята до виконання.
     *    Сервер зупиняє таймер повторів. */
    r->state = ST_ACCEPTED;
    emit_ack(1, r);

    if (!queue_push(d, (uint8_t)slot_idx)) {
        r->state  = ST_FAILED;
        r->result = E_QUEUE_FULL;
        printf("      [черга] переповнена — команду виконати нікуди\n");
        emit_ack(2, r);
        return E_QUEUE_FULL;
    }

    return E_OK;
}

/* ─────────────────────── крок автомата станів ───────────────────── */

static void finish(dispatcher_t *d, cmd_record_t *r, uint8_t state, int32_t result, int32_t detail) {
    journal_commit();            /* транзакція закрита: у FRAM відкритих записів немає */
    r->state  = state;
    r->result = result;
    r->detail = detail;
    emit_ack(2, r);
    d->active = -1;
}

void dispatcher_tick(dispatcher_t *d) {
    uint32_t now = plat_now_ms();

    /* А. Команда в роботі: опитуємо привід і стежимо за строком виконання. */
    if (d->active >= 0) {
        cmd_record_t *r = &d->ring[d->active];
        act_result_t res = actuator_poll();

        if (res.status == ACT_BUSY) {
            /* Передстартовий фільтр не рятує від затягнутого руху: перевіряємо
             * дедлайн і посеред виконання, знімаючи струм із драйвера. */
            if ((int32_t)(now - r->deadline_ms) >= 0) {
                actuator_abort();
                d->stats.expired++;
                printf("      [ttl] строк вичерпано під час руху — операцію скасовано\n");
                finish(d, r, ST_EXPIRED, E_EXPIRED, actuator_position());
            }
            return;   /* привід зайнятий — черга чекає */
        }

        if (res.status == ACT_FAILED) {
            printf("      [виконання] зрив: %s\n", cmd_err_name(res.error));
            finish(d, r, ST_FAILED, res.error, res.detail);
        } else {
            d->stats.executed++;
            finish(d, r, ST_SUCCEEDED, E_OK, res.detail);
        }
    }

    /* Б. Привід вільний: дістаємо наступну команду з черги. */
    uint8_t idx;
    while (d->active < 0 && queue_pop(d, &idx)) {
        cmd_record_t *r = &d->ring[idx];
        if (r->state != ST_ACCEPTED) continue;   /* слот уже закритий іншою гілкою */

        /* Передстартовий фільтр: остання перевірка перед подачею напруги. */
        if ((int32_t)(now - r->deadline_ms) >= 0) {
            d->stats.expired++;
            printf("      [ttl] %s token=0x%08lX простояв у черзі довше за строк — не пускаємо в залізо\n",
                   cmd_type_name(r->type), (unsigned long)(r->token & 0xFFFFFFFFu));
            r->state  = ST_EXPIRED;
            r->result = E_EXPIRED;
            emit_ack(2, r);
            continue;
        }

        if (superseded_later(d, r)) {
            d->stats.superseded++;
            printf("      [залп] %s token=0x%08lX витіснено свіжішою командою того ж призначення\n",
                   cmd_type_name(r->type), (unsigned long)(r->token & 0xFFFFFFFFu));
            r->state  = ST_EXPIRED;
            r->result = E_SUPERSEDED;
            emit_ack(2, r);
            continue;
        }

        /* Слід у незалежній пам'яті ДО подачі струму: якщо живлення зникне
         * посеред руху, після перезапуску буде видно незавершений токен. */
        journal_begin(r->token, r->type);

        cmd_err_t err = actuator_start(r->type, r->payload, r->payload_len);
        if (err != E_OK) {
            printf("      [виконання] залізо відмовило на старті: %s\n", cmd_err_name(err));
            finish(d, r, ST_FAILED, err, 0);
            continue;
        }

        r->state  = ST_EXECUTING;
        d->active = (int8_t)idx;

        /* Миттєві дії (реле) завершуються в тому ж такті — забираємо результат
         * одразу, щоб не тримати сервер в очікуванні зайвий цикл. */
        act_result_t res = actuator_poll();
        if (res.status == ACT_DONE) {
            d->stats.executed++;
            finish(d, r, ST_SUCCEEDED, E_OK, res.detail);
        } else if (res.status == ACT_FAILED) {
            printf("      [виконання] зрив: %s\n", cmd_err_name(res.error));
            finish(d, r, ST_FAILED, res.error, res.detail);
        }
    }
}

/* ────────────────────── відновлення після скидання ──────────────── */

void dispatcher_boot_recover(dispatcher_t *d) {
    uint64_t token;
    uint8_t  type;
    if (!journal_open_entry(&token, &type)) return;

    printf("      [старт] у FRAM відкрита транзакція %s token=0x%08lX — рух обірвано живленням\n",
           cmd_type_name(type), (unsigned long)(token & 0xFFFFFFFFu));

    /* Механізм у невизначеному стані: спершу зводимо його в безпечну точку. */
    actuator_home();
    journal_commit();

    /* Реєструємо токен як провалений. Без цього повтор із сервера виглядав би
     * новою командою — і насос налив би дозу вдруге. */
    int slot_idx = ring_alloc(d);
    if (slot_idx >= 0) {
        cmd_record_t *r = &d->ring[slot_idx];
        r->token       = token;
        r->type        = type;
        r->state       = ST_FAILED;
        r->result      = E_POWER_RESET;
        r->detail      = 0;
        r->rx_time_ms  = plat_now_ms();
        r->deadline_ms = plat_now_ms();
        emit_ack(2, r);
    }
}

void dispatcher_print_stats(const dispatcher_t *d) {
    printf("\n--- підсумок диспетчера ---\n");
    printf("  виконано:          %u\n", (unsigned)d->stats.executed);
    printf("  дублікатів:        %u\n", (unsigned)d->stats.duplicates);
    printf("  протухло за TTL:   %u\n", (unsigned)d->stats.expired);
    printf("  витіснено залпом:  %u\n", (unsigned)d->stats.superseded);
    printf("  повторів з ефіру:  %u\n", (unsigned)d->stats.replays);
    printf("  битих кадрів:      %u\n", (unsigned)d->stats.dropped);
    printf("  пам'ять кільця:    %u байт (%u слотів)\n",
           (unsigned)(RING_SIZE * sizeof(cmd_record_t)), (unsigned)RING_SIZE);
}
