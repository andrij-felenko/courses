#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    float    min, max;       // фізичні межі величини
    float    max_step;       // найбільша правдоподібна зміна за крок
    uint32_t timeout_ms;     // як довго мовчання вважати відмовою
    float    last;           // останнє прийняте значення
    uint32_t last_ms;        // коли воно прийшло
    bool     primed;         // чи вже є з чим порівнювати
} sensor_gate_t;

// true — числу можна вірити; false — давач під підозрою
bool gate_check(sensor_gate_t *g, float x, uint32_t now_ms) {
    if (isnan(x) || isinf(x)) return false;            // пропадання / NaN
    if (x < g->min || x > g->max) return false;        // виліт за межу
    if (g->primed && fabsf(x - g->last) > g->max_step)
        return false;                                  // нереальний стрибок
    if (g->primed && (now_ms - g->last_ms) > g->timeout_ms)
        return false;                                  // завмер / мовчання
    g->last = x; g->last_ms = now_ms; g->primed = true;
    return true;
}
