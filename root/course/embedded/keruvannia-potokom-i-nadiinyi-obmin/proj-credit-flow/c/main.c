/* Прогін обох механізмів на віртуальному часі: на столі видно те саме, що на
 * логічному аналізаторі — коли смикається /RTS і як лінк виходить зі стопора
 * після втраченого кадру повернення кредитів. */
#include "credit_flow.h"
#include "ring_buffer.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

/* --- Частина 1: буфер із порогами --------------------------------------- */

static uint32_t g_rts_transitions;

static void rts_line(bool ready)
{
    g_rts_transitions++;
    printf("    /RTS -> %-5s (перемикань: %u)\n", ready ? "READY" : "BUSY", g_rts_transitions);
}

static void demo_ring_buffer(void)
{
    ring_buffer_t rb;
    uint8_t byte;
    uint8_t chunk[32];
    unsigned i;

    puts("== Кільцевий буфер з гістерезисом ==");
    rb_init(&rb, rts_line);

    /* Пачка від швидкого передавача: заливаємо 200 байтів без жодного читання. */
    for (i = 0; i < 200u; i++) {
        if (!rb_push_from_isr(&rb, (uint8_t)i)) {
            break;
        }
    }
    printf("  залито %u, рівень %zu, вільно %zu, лінія %s\n", i, rb_level(&rb),
           rb_free_space(&rb), rb_is_ready(&rb) ? "READY" : "BUSY");

    /* Тепер найважливіше: вичитуємо по одному байту від рівня 200 до 64.
     * З одним порогом кожен байт давав би пару перемикань лінії. */
    while (rb_level(&rb) > RB_LOW_WATERMARK) {
        (void)rb_pop(&rb, &byte);
    }
    printf("  рівень %zu, лінія %s, усього перемикань %u\n", rb_level(&rb),
           rb_is_ready(&rb) ? "READY" : "BUSY", g_rts_transitions);

    /* Передавач, що проігнорував Busy: запас у 64 байти поглинає байти в польоті,
     * далі починається справжня втрата. */
    for (i = 0; i < 300u; i++) {
        (void)rb_push_from_isr(&rb, (uint8_t)i);
    }
    printf("  після переливу: рівень %zu, втрачено байтів %u\n", rb_level(&rb),
           rb_overruns(&rb));

    /* Вигрібання пачкою — так це робить фонове завдання, а не побайтовий цикл. */
    while (rb_level(&rb) > 0u) {
        size_t got = rb_pop_bulk(&rb, chunk, sizeof chunk);
        if (got == 0u) {
            break;
        }
    }
    printf("  спорожнено: рівень %zu, лінія %s\n\n", rb_level(&rb),
           rb_is_ready(&rb) ? "READY" : "BUSY");
}

/* --- Частина 2: кредитний обмін ----------------------------------------- */

/* Модель шини: один кадр GRANT ми навмисно губимо, щоб побачити роботу таймера. */
static unsigned g_grants_to_drop = 1u;

static bool wire_deliver_grant(cf_sender_t *tx, const cf_frame_t *frame, uint32_t now_ms)
{
    if (g_grants_to_drop > 0u) {
        g_grants_to_drop--;
        printf("[%4u мс] ШИНА  : GRANT(cum=%u) ЗАГУБЛЕНО\n", now_ms, frame->cum_release);
        return false;
    }
    cf_sender_on_frame(tx, frame, now_ms);
    printf("[%4u мс] TX    : прийнято %s(cum=%u), кредитів %d, стан %s\n", now_ms,
           frame->type == CF_FRAME_GRANT ? "GRANT" : "FRAME", frame->cum_release,
           tx->credits, cf_link_state_name(tx->state));
    return true;
}

static void demo_credit_link(void)
{
    static const char *messages[] = { "temp=21.4", "temp=21.6", "temp=21.9", "temp=22.1",
                                      "temp=22.0", "temp=21.8", "temp=21.5", "temp=21.3" };
    const size_t total = sizeof messages / sizeof messages[0];

    cf_sender_t tx;
    cf_receiver_t rx;
    size_t next_msg = 0;
    uint32_t consume_at = 90u;
    uint32_t t;

    puts("== Кредитний автомат ==");
    cf_sender_init(&tx, 0u);
    cf_receiver_init(&rx);

    for (t = 0u; t <= 3000u; t += 10u) {
        cf_frame_t frame;

        /* 1. Передавач віддає чергове повідомлення, поки є баланс. */
        if (next_msg < total && cf_sender_can_send(&tx)) {
            const char *msg = messages[next_msg];
            cf_send_result_t res =
                cf_sender_encode(&tx, (const uint8_t *)msg, (uint8_t)strlen(msg), t, &frame);
            if (res == CF_SEND_OK) {
                cf_rx_result_t rx_res = cf_receiver_on_frame(&rx, &frame);
                printf("[%4u мс] TX->RX: DATA seq=%u \"%s\", лишилось кредитів %d%s\n", t,
                       frame.seq, msg, tx.credits,
                       rx_res == CF_RX_ACCEPTED ? "" : " [ВІДКИНУТО ПРИЙМАЧЕМ]");
                next_msg++;
            }
        }

        /* 2. Таймер неактивності передавача. */
        if (cf_sender_tick(&tx, t, &frame)) {
            printf("[%4u мс] TX->RX: POLL (спроба %u, зараховано cum=%u)\n", t, tx.polls_sent,
                   frame.cum_release);
            (void)cf_receiver_on_frame(&rx, &frame);
        }

        /* 3. Завдання приймача вичитує пакет із пам'яті — повільніше за передавача. */
        if (t >= consume_at) {
            cf_frame_t done;
            if (cf_receiver_take(&rx, &done)) {
                printf("[%4u мс] RX    : оброблено seq=%u, зайнято слотів %u, звільнено всього %u\n",
                       t, done.seq, rx.occupied, rx.cum_release);
                consume_at = t + 90u;
            }
        }

        /* 4. Повернення кредитів: пачкою або у відповідь на POLL. */
        if (cf_receiver_build_grant(&rx, &frame)) {
            printf("[%4u мс] RX->TX: GRANT cum=%u\n", t, frame.cum_release);
            (void)wire_deliver_grant(&tx, &frame, t);
        }

        if (next_msg == total && rx.occupied == 0u) {
            break;
        }
        if (tx.state == CF_LINK_DEAD) {
            puts("        лінк визнано мертвим: далі потрібне повторне встановлення зв'язку");
            break;
        }
    }

    printf("\n  підсумок: надіслано %u кадрів, повернено %u кредитів, "
           "порожніх кадрів %u, підозрілих %u\n",
           tx.frames_sent, tx.credits_granted, tx.stale_grants, tx.suspect_grants);
    printf("  приймач: понад квоту %u, пропусків у нумерації %u, биті кадри %u\n",
           rx.over_quota, rx.seq_gaps, rx.bad_frames);
}

int main(void)
{
    demo_ring_buffer();
    demo_credit_link();
    return 0;
}
