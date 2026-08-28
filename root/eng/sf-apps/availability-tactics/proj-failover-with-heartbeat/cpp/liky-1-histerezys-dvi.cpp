#define HEAL_LIMIT   5u    // стільки ДОБРИХ ударів підряд, щоб визнати одужання
                           // (свідомо БІЛЬШЕ за MISS_LIMIT: падати легко, вставати важко)

typedef struct {
    NodeHealth base;         // звичайний монітор із MISS_LIMIT
    uint32_t   healthy_run;  // скільки добрих ударів підряд уже назбирано
    bool       eligible;     // чи вузол ЗНОВУ придатний бути в ротації
    uint32_t   eligible_since_ms;  // коли ЗНОВУ став придатним (для карантину)
} Hysteretic;

void hys_init(Hysteretic *h, uint32_t now_ms) {
    health_init(&h->base, now_ms);
    h->healthy_run = 0;
    h->eligible = true;
    h->eligible_since_ms = now_ms;
}

// Той самий тик, але з РІЗНИМИ порогами вниз і вгору.
void hys_tick(Hysteretic *h, uint32_t now_ms, bool beat) {
    if (beat) {
        health_on_beat(&h->base, now_ms);
        if (h->healthy_run < HEAL_LIMIT) h->healthy_run++;
    }
    health_tick(&h->base, now_ms);

    if (h->base.health == NODE_DOWN) {
        h->eligible = false;      // впав — і придатність знімаємо одразу
        h->healthy_run = 0;       // рахунок одужання починаємо з нуля
    } else if (!h->eligible && h->healthy_run >= HEAL_LIMIT) {
        h->eligible = true;              // придатний ЛИШЕ після стійкої серії
        h->eligible_since_ms = now_ms;   // звідси відлічуємо карантин повернення
    }
}
