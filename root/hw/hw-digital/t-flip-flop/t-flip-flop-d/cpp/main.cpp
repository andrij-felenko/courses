#include <cstdbool>

static bool in_prev = false;   // вхід на попередній ітерації
static bool q       = false;   // вихід «тригера»

// викликається часто (в циклі або по перериванню)
bool tff_div2(bool in) {
    bool rising = in && !in_prev;   // фронт 0→1 саме зараз?
    if (rising) {
        q = !q;                     // toggle: перевернути вихід
    }
    in_prev = in;                   // запам'ятати вхід на наступний крок
    return q;                       // q міняється вдвічі рідше за in
}
