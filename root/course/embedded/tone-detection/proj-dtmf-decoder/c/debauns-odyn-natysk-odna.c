typedef enum { ST_IDLE, ST_MATCHING, ST_PRESSED, ST_RELEASE } dtmf_state_t;

#define CONFIRM_BLOCKS   2     // M: стільки однакових блоків поспіль = натиск
#define SILENCE_BLOCKS   2     // K: стільки блоків тиші = цифру відпущено

typedef struct {
    dtmf_state_t state;
    char         cand;         // символ-кандидат, що його зараз підтверджуємо
    uint8_t      run;          // лічильник однакових / тихих блоків поспіль
} dtmf_fsm_t;

void dtmf_fsm_init(dtmf_fsm_t *f)
{
    f->state = ST_IDLE;
    f->cand  = 0;
    f->run   = 0;
}

// згодувати символ одного блоку (sym==0 — тиша/шум).
// Повертає символ, ЩОЙНО підтверджений у цьому блоці, або 0.
char dtmf_fsm_step(dtmf_fsm_t *f, char sym)
{
    switch (f->state) {

    case ST_IDLE:
        if (sym) {                       // з'явився валідний символ
            f->cand  = sym;
            f->run   = 1;
            f->state = ST_MATCHING;
        }
        break;

    case ST_MATCHING:
        if (sym == f->cand) {            // той самий символ — рахуємо далі
            if (++f->run >= CONFIRM_BLOCKS) {
                f->state = ST_PRESSED;
                return f->cand;          // <-- ЄДИНА точка видачі події
            }
        } else if (sym) {                // інший символ — починаємо лічбу з нього
            f->cand = sym;
            f->run  = 1;
        } else {                         // тиша до підтвердження — натиску не було
            f->state = ST_IDLE;
            f->run   = 0;
        }
        break;

    case ST_PRESSED:
        if (sym != f->cand) {            // тон зник або змінився — починаємо відпускати
            f->state = ST_RELEASE;
            f->run   = (sym == 0) ? 1 : 0;
        }
        // поки той самий символ — МОВЧИМО (подію вже видали)
        break;

    case ST_RELEASE:
        if (sym == 0) {                  // тиша — наближаємось до готовності
            if (++f->run >= SILENCE_BLOCKS) {
                f->state = ST_IDLE;      // пауза витримана — готові до нової цифри
                f->run   = 0;
            }
        } else {                         // знову тон, не дочекавшись тиші
            if (sym == f->cand) {
                f->state = ST_PRESSED;   // та сама цифра тримається далі — без події
            } else {
                f->cand  = sym;          // вже інша цифра — підтверджуємо її
                f->run   = 1;
                f->state = ST_MATCHING;
            }
        }
        break;
    }
    return 0;
}
