// ---- Стани: «де ми зараз у розмові» ----
typedef enum { VBUS_5V, WAIT_CAPS, REQ_SENT, WAIT_PSRDY, CONTRACT } state_t;

// ---- Розкодовані повідомлення PD (їх дає PHY/контролер) ----
typedef enum { MSG_SRC_CAPS, MSG_ACCEPT, MSG_REJECT, MSG_WAIT, MSG_PS_RDY } msg_t;

// Один рядок меню джерела: напруга й стеля струму фіксованого PDO.
typedef struct { uint16_t mv, max_ma; bool fixed; } pdo_t;

// ---- Дедлайни (мс): кожен стереже свій вид збою ----
enum { T_WAIT_CAP = 500, T_SENDER_RESP = 30, T_PS_TRANS = 550 };

// ---- Політика: чого хоче САМЕ наш пристрій ----
static const uint16_t desired_mv[] = { 12000, 9000 };  // профілі за пріоритетом
static const uint16_t need_ma      = 2000;             // потрібний струм

static state_t st = VBUS_5V;   // старт: на шині лише безпечні 5 В

// ПОЛІТИКА — чиста функція: з меню обрати профіль під нашу потребу.
// Жодних побічних дій, лише повертає індекс PDO (або -1).
static int pick_pdo(const pdo_t *pdo, int n) {
    for (unsigned k = 0; k < sizeof desired_mv / sizeof *desired_mv; k++)
        for (int i = 0; i < n; i++)
            if (pdo[i].fixed && pdo[i].mv == desired_mv[k]
                             && pdo[i].max_ma >= need_ma)
                return i;          // цей профіль дає і вольти, і ампери
    return -1;                     // нічого не підходить
}

// ЄДИНИЙ безпечний вихід. Сюди веде будь-яка біда.
static void fall_to_safe(const char *why) {
    disable_load();                // навантаження геть — ПЕРШОЮ дією
    tim_stop(TIM_PD);              // знімаємо зведений дедлайн
    st = VBUS_5V;                  // лишаємось на безпечних 5 В
    notify(why);                   // блимнути світлодіодом / записати причину
}

// Побачили джерело по CC — стартуємо розмову.
static void on_attach(void) {
    st = WAIT_CAPS;
    tim_oneshot(TIM_PD, T_WAIT_CAP);   // не прийде меню → відкат
}

// Прийшло розкодоване повідомлення (pdo/n дійсні лише для MSG_SRC_CAPS).
static void on_message(msg_t msg, const pdo_t *pdo, int n) {
    switch (msg) {

    case MSG_SRC_CAPS: {                     // меню прийшло (чи оновилось на ходу)
        int i = pick_pdo(pdo, n);
        if (i < 0) { fall_to_safe("нема потрібного профілю"); return; }
        pd_send_request(i);                  // просимо саме цей PDO
        st = REQ_SENT;
        tim_oneshot(TIM_PD, T_SENDER_RESP);  // нема відповіді → відкат
        break;
    }

    case MSG_ACCEPT:
        if (st != REQ_SENT) break;
        st = WAIT_PSRDY;
        tim_oneshot(TIM_PD, T_PS_TRANS);     // напруга не встане → відкат
        break;

    case MSG_REJECT:
        if (st != REQ_SENT) break;
        fall_to_safe("Reject — цей профіль не дадуть");
        break;

    case MSG_WAIT:
        if (st != REQ_SENT) break;
        fall_to_safe("Wait — джерело зайняте, спробую пізніше");
        break;

    case MSG_PS_RDY:
        if (st != WAIT_PSRDY) break;
        tim_stop(TIM_PD);                    // дочекались — дедлайн уже не треба
        st = CONTRACT;
        enable_load();                       // АЖ ТЕПЕР вмикаємо навантаження
        break;
    }
}
