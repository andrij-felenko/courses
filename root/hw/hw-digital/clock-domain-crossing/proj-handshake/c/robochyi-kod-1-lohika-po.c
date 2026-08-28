#include <stdint.h>
#include <stdbool.h>

// Стани машини A
typedef enum { A_IDLE, A_REQ, A_WAIT } a_state_t;

typedef struct {
    a_state_t state;
    uint32_t  data_out;   // шина в бік B: стоїть незмінно весь обмін
    bool      req;        // прапорець «дані готові» в бік B

    // Двотактовий синхронізатор ack, що приходить з домену B:
    // два тригери, тактовані CLK_A. ack_meta ловить можливу метастабільність,
    // ack_sync — уже чистий сигнал, яким користується машина.
    bool      ack_meta;
    bool      ack_sync;
} tx_t;

// Один фронт CLK_A. ack_in — сирий асинхронний ack з домену B.
// new_word/word — чи є що слати і що саме (з логіки-джерела в домені A).
void tx_clk(tx_t *s, bool ack_in, bool new_word, uint32_t word) {
    // 1) Синхронізатор ack: спершу засуваємо конвеєр тригерів.
    //    Порядок саме такий — новий сирий біт входить у meta,
    //    попереднє meta переходить у sync (як два тригери поспіль).
    s->ack_sync = s->ack_meta;
    s->ack_meta = ack_in;
    bool ack = s->ack_sync;        // чистий, синхронізований ack

    // 2) Скінченна машина за синхронізованим ack.
    switch (s->state) {
    case A_IDLE:
        s->req = false;
        if (new_word) {
            s->data_out = word;     // виставили слово на шину…
            s->req      = true;     // …і аж тепер підняли req (фаза 1)
            s->state    = A_REQ;
        }
        break;

    case A_REQ:
        // Слово тримаємо, req тримаємо. Чекаємо ack = 1 (фаза 2 дійшла).
        if (ack) {
            s->req   = false;       // фаза 3: знімаємо запит
            s->state = A_WAIT;
        }
        break;

    case A_WAIT:
        // req уже 0. Чекаємо, поки ack теж упаде (фаза 4 дійшла).
        if (!ack) {
            s->state = A_IDLE;      // коло замкнулося, готові до наступного
        }
        break;
    }
}
