#include <stdbool.h>

static bool clk_prev = false;   // такт на попередній ітерації
static bool q        = false;   // вихід тригера

// викликається часто (в циклі або по таймеру)
void dff_step(bool d, bool clk) {
    bool rising = clk && !clk_prev;   // фронт 0→1 саме зараз?
    if (rising) {
        q = d;                        // «фотографуємо» D у мить фронту
    }
    clk_prev = clk;                   // запам'ятати такт для наступного кроку
    // поза фронтом q не чіпаємо — між фронтами D ігнорується
}
