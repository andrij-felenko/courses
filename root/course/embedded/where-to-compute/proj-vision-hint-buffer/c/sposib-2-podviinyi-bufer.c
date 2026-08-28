#include <stdint.h>
#include <stdbool.h>

typedef struct {
    float    target_angle;
    uint32_t stamp_ms;
    bool     valid;
    // …тут може бути скільки завгодно полів: буфер копіюється не читачем…
} vision_hint_t;

static vision_hint_t   g_buf[2];             // два екземпляри: ping і pong
static volatile uint8_t g_ready = 0;         // індекс ГОТОВОГО буфера (0 або 1)

// ── писар: у перерві. Пише в НЕактивний буфер, тоді перемикає індекс ──
void on_vision_msg(float angle, uint32_t now_ms) {
    uint8_t back = g_ready ^ 1u;             // «задній» буфер — той, що НЕ читається
    g_buf[back].target_angle = angle;        // спокійно заповнюємо його цілком:
    g_buf[back].stamp_ms     = now_ms;       // читач зараз дивиться в ІНШИЙ буфер
    g_buf[back].valid        = true;

    g_ready = back;                          // ← АТОМАРНЕ перемикання: один запис байта
}

// ── читач: у витку контуру. Читає активний буфер, НЕ блокуючи перерву ──
vision_hint_t hint_read_pingpong(void) {
    uint8_t idx = g_ready;                    // зафіксували, котрий читати
    return g_buf[idx];                        // копіюємо готовий буфер
}
