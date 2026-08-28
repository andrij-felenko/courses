#include <stdbool.h>

static bool clk_prev = false;
static bool q_ff     = false;

// тригер: одна-єдина мить захоплення
void ff_capture(bool data, bool clk) {
    bool rising = clk && !clk_prev;   // фронт саме зараз?
    if (rising) {
        q_ff = data;                  // взяли рівно те, що є на фронті
    }
    clk_prev = clk;
    // після фронту data хоч як міняйся — q_ff не зрушиться (стіна)
}
