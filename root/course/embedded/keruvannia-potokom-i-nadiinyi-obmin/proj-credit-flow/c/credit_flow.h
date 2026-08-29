/* Кредитний обмін для шини без апаратних ліній керування (RS-485, CAN, радіоміст).
 *
 * Передавач має баланс слотів приймача й витрачає його на кадри. Приймач
 * повертає кредити КУМУЛЯТИВНИМ лічильником звільнених слотів, а не інкрементом
 * «+1»: втрачений кадр повернення тоді не з'їдає кредит назавжди, бо наступний
 * кадр несе те саме абсолютне число. Проти повної тиші на лінії передавач має
 * таймер неактивності й запит стану POLL. */
#ifndef CREDIT_FLOW_H
#define CREDIT_FLOW_H

#include <stdbool.h>
#include <stdint.h>

#define CF_MAX_PAYLOAD 64u
#define CF_RX_SLOTS 4u /* вікно: скільки кадрів приймач тримає одночасно */
#define CF_GRANT_BATCH 2u /* стільки звільнень копимо, перш ніж слати GRANT */
#define CF_POLL_TIMEOUT_MS 250u /* тиша при нульовому балансі — і шлемо POLL */
#define CF_MAX_POLLS 5u /* після цього вважаємо лінк мертвим */

typedef enum {
    CF_FRAME_DATA = 0x01,
    CF_FRAME_GRANT = 0x02,
    CF_FRAME_POLL = 0x03
} cf_frame_type_t;

typedef struct {
    uint8_t type;
    uint8_t seq; /* номер кадру даних, для виявлення пропусків */
    uint16_t cum_release; /* кумулятивно звільнених слотів у приймача */
    uint8_t length;
    uint8_t payload[CF_MAX_PAYLOAD];
} cf_frame_t;

/* --- Передавач ----------------------------------------------------------- */

typedef enum {
    CF_LINK_READY, /* кредити є, можна слати */
    CF_LINK_BLOCKED, /* баланс нульовий, чекаємо повернення */
    CF_LINK_POLLING, /* мовчання затяглося, шлемо запити стану */
    CF_LINK_DEAD /* відповіді немає й після CF_MAX_POLLS */
} cf_link_state_t;

typedef struct {
    int32_t credits;
    uint16_t last_cum_release; /* останнє зараховане абсолютне число */
    uint8_t next_seq;
    cf_link_state_t state;
    uint32_t last_event_ms; /* мить, від якої рахуємо тишу */
    uint8_t polls_sent;
    /* Лічильники для діагностики, без них лінк неможливо розбирати в полі. */
    uint32_t frames_sent;
    uint32_t credits_granted;
    uint32_t stale_grants; /* кадр не приніс нічого нового */
    uint32_t suspect_grants; /* приріст більший за вікно — кадр побито */
} cf_sender_t;

typedef enum {
    CF_SEND_OK,
    CF_SEND_NO_CREDIT,
    CF_SEND_TOO_LONG,
    CF_SEND_LINK_DEAD
} cf_send_result_t;

void cf_sender_init(cf_sender_t *s, uint32_t now_ms);
bool cf_sender_can_send(const cf_sender_t *s);
cf_send_result_t cf_sender_encode(cf_sender_t *s, const uint8_t *data, uint8_t len,
                                  uint32_t now_ms, cf_frame_t *out_frame);
/* Будь-який кадр із того боку несе кумулятивне число — це і є піггібекінг. */
void cf_sender_on_frame(cf_sender_t *s, const cf_frame_t *frame, uint32_t now_ms);
/* Таймер неактивності: true — треба відправити сформований запит стану. */
bool cf_sender_tick(cf_sender_t *s, uint32_t now_ms, cf_frame_t *out_poll);
const char *cf_link_state_name(cf_link_state_t state);

/* --- Приймач ------------------------------------------------------------- */

typedef enum {
    CF_RX_ACCEPTED,
    CF_RX_POLLED, /* прийшов POLL: відповісти станом позачергово */
    CF_RX_OVER_QUOTA, /* передавач вийшов за вікно — порушення протоколу */
    CF_RX_BAD_FRAME
} cf_rx_result_t;

typedef struct {
    cf_frame_t slots[CF_RX_SLOTS];
    uint8_t write_idx;
    uint8_t read_idx;
    uint8_t occupied;
    uint16_t cum_release; /* скільки слотів звільнено за весь час */
    uint16_t last_reported; /* яке число вже пішло в ефір */
    uint8_t expected_seq;
    bool seq_seen;
    bool poll_pending;
    uint32_t over_quota;
    uint32_t bad_frames;
    uint32_t seq_gaps;
} cf_receiver_t;

void cf_receiver_init(cf_receiver_t *r);
cf_rx_result_t cf_receiver_on_frame(cf_receiver_t *r, const cf_frame_t *frame);
/* Завдання забирає найстаріший пакет; слот звільняється саме тут. */
bool cf_receiver_take(cf_receiver_t *r, cf_frame_t *out_frame);
/* true — назбиралася пачка або прийшов POLL, кадр повернення сформовано. */
bool cf_receiver_build_grant(cf_receiver_t *r, cf_frame_t *out_frame);

#endif /* CREDIT_FLOW_H */
