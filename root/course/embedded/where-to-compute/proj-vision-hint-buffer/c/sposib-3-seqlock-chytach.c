#include <stdint.h>
#include <stdbool.h>

typedef struct {
    float    target_angle;
    uint32_t stamp_ms;
    bool     valid;
} vision_hint_t;

static vision_hint_t    g_hint;
static volatile uint32_t g_seq = 0;   // парний = стабільно, непарний = триває запис

// ── писар: у перерві. Обгортає запис збільшенням лічильника ──
void on_vision_msg(float angle, uint32_t now_ms) {
    g_seq++;                           // → непарний: «увага, я пишу»
    __asm volatile ("dmb" ::: "memory");  // бар'єр: лічильник змінився ДО даних

    g_hint.target_angle = angle;
    g_hint.stamp_ms     = now_ms;
    g_hint.valid        = true;

    __asm volatile ("dmb" ::: "memory");  // бар'єр: дані записані ДО лічильника
    g_seq++;                           // → знову парний: «готово, дані цілі»
}

// ── читач: у витку контуру. Перечитує, поки не впіймає стабільний знімок ──
vision_hint_t hint_read_seqlock(void) {
    vision_hint_t snap;
    uint32_t before, after;

    do {
        before = g_seq;                     // 1) зчитали лічильник…
        while (before & 1u)                 //    непарний → писар саме пише:
            before = g_seq;                 //    крутимось, доки не стане парним
        __asm volatile ("dmb" ::: "memory");

        snap = g_hint;                      // 2) скопіювали дані

        __asm volatile ("dmb" ::: "memory");
        after = g_seq;                      // 3) …і зчитали лічильник ЗНОВУ
    } while (before != after);              // змінився? писар вклинився → наново

    return snap;                            // before == after (парні) → знімок чистий
}
