#include <stdbool.h>

static bool clk_prev = false;   // такт на попередній ітерації
static bool q        = false;   // вихід тригера

// викликається часто (в циклі або по таймеру)
void jk_step(bool j, bool k, bool clk) {
    bool rising = clk && !clk_prev;   // фронт 0→1 саме зараз?
    if (rising) {
        if      ( j && !k) q = true;      // set
        else if (!j &&  k) q = false;     // reset
        else if ( j &&  k) q = !q;        // перекинути (toggle)
        // j==0 && k==0 → тримати: q не чіпаємо
    }
    clk_prev = clk;                    // запам'ятати такт для наступного кроку
    // поза фронтом q лишається як був
}
