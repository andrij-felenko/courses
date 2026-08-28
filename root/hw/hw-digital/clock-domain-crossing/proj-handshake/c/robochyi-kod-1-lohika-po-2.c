// Стани машини B
typedef enum { B_WAIT, B_GOT, B_DONE } b_state_t;

typedef struct {
    b_state_t state;
    uint32_t  data_latched;  // сюди защіпається ціле слово
    bool      got;           // прапорець: є свіже прийняте слово
    bool      ack;           // прапорець «прийняв» у бік A

    // Двотактовий синхронізатор req, тактований CLK_B.
    bool      req_meta;
    bool      req_sync;
} rx_t;

// Один фронт CLK_B. req_in — сирий асинхронний req з домену A.
// bus — поточне значення шини data (те, що A виставила й тримає).
void rx_clk(rx_t *s, bool req_in, uint32_t bus) {
    // 1) Синхронізатор req: два тригери поспіль.
    s->req_sync = s->req_meta;
    s->req_meta = req_in;
    bool req = s->req_sync;         // чистий, синхронізований req

    s->got = false;                 // імпульс «нове слово» тримаємо один такт

    // 2) Скінченна машина за синхронізованим req.
    switch (s->state) {
    case B_WAIT:
        s->ack = false;
        if (req) {
            // req уже давно 1 (пройшов 2 тригери), отже шина під ним
            // стоїть незмінно ще довше — можна брати ВСІ біти разом.
            s->data_latched = bus;   // цілісний захват 32 бітів одним фронтом
            s->got          = true;  // сигнал логіці B: слово готове
            s->ack          = true;  // фаза 2: підтверджуємо
            s->state        = B_GOT;
        }
        break;

    case B_GOT:
        // ack тримаємо. Чекаємо, поки req упаде (фаза 3 дійшла).
        if (!req) {
            s->ack   = false;        // фаза 4: знімаємо підтвердження
            s->state = B_DONE;
        }
        break;

    case B_DONE:
        s->ack   = false;
        s->state = B_WAIT;           // одразу назад у чекання
        break;
    }
}
