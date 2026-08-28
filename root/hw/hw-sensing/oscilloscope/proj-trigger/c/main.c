// Тригер по фронту з гістерезисом і голдоффом.
// trigger_feed() викликають на КОЖЕН новий відлік АЦП (рівний темп вибірки).
#include <stdbool.h>
#include <stdint.h>

#define BUF_LEN   4096u     // кільцевий буфер; степінь двійки → дешеве обгортання
#define POST_LEN  2048u     // скільки відліків дописати ПІСЛЯ точки тригера
#define HOLDOFF   3000u     // голдофф: пауза після спрацювання, у відліках

static uint16_t buf[BUF_LEN];   // безперервний потік відліків (дає pre-trigger)
static uint32_t head;           // індекс, куди ляже наступний відлік

// Налаштування тригера (задають з UI при зміні рівня/фронту):
static uint16_t level;          // рівень L (у кодах АЦП)
static uint16_t hyst;           // напівширина смуги гістерезису h
static bool     rising = true;  // true — висхідний фронт, false — нисхідний

// Робочий стан стан-машини:
static bool     armed   = true; // курок зведено (готові спрацювати)
static uint32_t hold    = 0;    // лічильник голдоффа
static uint16_t prev    = 0;    // попередній відлік
static bool     filling = false;// t0 знайдено, добираємо post-trigger
static uint32_t post    = 0;    // скільки ще відліків дописати після t0

// Перетин крізь ДАЛЬНІЙ край смуги в обраний бік: L+h вгору / L−h вниз.
// Рахуємо через int32_t, щоб L±h не переповнило uint16_t на краях шкали.
static bool crossed(uint16_t p, uint16_t c) {
    int32_t hi = (int32_t)level + hyst;
    int32_t lo = (int32_t)level - hyst;
    if (rising) return (int32_t)p <  hi && (int32_t)c >= hi;
    else        return (int32_t)p >  lo && (int32_t)c <= lo;
}

// Повернення за ПРОТИЛЕЖНИЙ край смуги знову «зводить курок» (гістерезис).
static bool rearmed(uint16_t c) {
    int32_t hi = (int32_t)level + hyst;
    int32_t lo = (int32_t)level - hyst;
    return rising ? ((int32_t)c < lo) : ((int32_t)c > hi);
}

// Повертає true у мить, коли кадр [PRE | t0 | POST] повністю захоплено.
bool trigger_feed(uint16_t cur) {
    buf[head] = cur;                       // пишемо відлік у кільцевий буфер
    head = (head + 1u) & (BUF_LEN - 1u);   // обгортання (BUF_LEN — степінь 2)

    if (filling) {                         // уже добираємо хвіст після t0
        if (--post == 0u) {                // зібрано POST відліків
            filling = false;               // кадр готовий; далі — голдофф і re-arm
            return true;                   // сигнал: можна показувати [PRE | t0 | POST]
        }
        return false;
    }
    if (hold > 0u) {                       // ще в зоні голдоффа — мовчимо
        --hold;
    } else if (armed && crossed(prev, cur)) {  // умова тригера виконана
        post    = POST_LEN;                // зафіксувати t0, добрати POST відліків
        filling = true;
        hold    = HOLDOFF;                 // пауза: не тригерити N відліків
        armed   = false;
    } else if (rearmed(cur)) {             // вийшли за протилежний поріг
        armed = true;                      // курок знову зведено
    }
    prev = cur;
    return false;
}
