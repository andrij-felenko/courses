#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <string.h>

// припущення як дані: нижній кінець, номінал, верхній кінець і одиниця
typedef struct { const char *name; double lo, nom, hi; const char *unit; } Factor;

enum { DAU, SESSIONS, ACTIONS, REQ, PEAK_FRAC, NF };   // NF — скільки множників

// ── модель: піковий трафік (запитів/с) як добуток припущень ──
static double peak_rps(const double v[NF]) {
    double daily = v[DAU] * v[SESSIONS] * v[ACTIONS] * v[REQ];   // запитів на добу
    return daily * v[PEAK_FRAC] / 3600.0;                        // у пікову секунду
}

static const Factor FACTORS[NF] = {
    { "DAU",       180000, 200000, 220000, "корист./добу" },
    { "sessions",     2.5,    3.0,    3.5, "сеансів/корист." },
    { "actions",       15,     20,     25, "дій/сеанс" },
    { "req",            4,      4,      4, "запитів/дію" },
    { "peak_frac",   0.05,   0.10,   0.30, "частка в пік. годину" },
};
#define THRESHOLD 2000.0    // запитів/с — стеля одного сервера
