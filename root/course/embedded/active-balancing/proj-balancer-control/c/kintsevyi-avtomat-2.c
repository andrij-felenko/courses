// Платформозалежні заглушки — реалізуєш під свій вузол:
extern void     read_pack(pack_state_t *p);          // зняти напруги + оновити SOC
extern bool     protection_ok(void);                 // монітор-захист НЕ заперечує?
extern bool     power_node_too_hot(void);            // датчик температури силового вузла
extern void     balancer_off(void);                  // зняти всі ключі/розряди
extern void     transfer_begin(int src, int dst);    // почати перенос (актив) / розряд src (пасив)
extern void     transfer_hold(void);                 // підтримати заданий струм цей такт

// Те саме find_imbalance, що в темі (структура imbalance_t { int hi, lo; uint16_t spread_mv; }),
// але порівнює комірки за cell_metric() — тобто за ПРАВИЛЬНИМ для хімії критерієм, не за сирою mv[].
static imbalance_t find_imbalance_metric(const balancer_t *b, const pack_state_t *p);

void balancer_tick(balancer_t *b)
{
    b->t_state_ms += TICK_MS;

    // ── НУЛЬОВИЙ пріоритет: захист над усім ───────────────────────────────
    // Будь-яке вето монітора-захисту — миттєвий безумовний відкат у спокій.
    if (!protection_ok()) {
        balancer_off();
        b->state = BAL_IDLE;
        b->t_state_ms = 0;
        b->t_balance_ms = 0;
        return;
    }

    switch (b->state) {

    case BAL_IDLE:
        // Чекаємо період, тоді йдемо знімати виміри.
        if (b->t_state_ms >= MEASURE_PERIOD_MS) {
            b->state = BAL_MEASURE;
            b->t_state_ms = 0;
        }
        break;

    case BAL_MEASURE: {
        pack_state_t p;
        read_pack(&p);                              // свіжі напруги + SOC
        imbalance_t im = find_imbalance_metric(b, &p);
        b->spread_mv = im.spread_mv;

        if (im.spread_mv >= b->chem->start_mv) {       // є за що балансувати
            b->src = im.hi;                         // з найповнішої…
            b->dst = im.lo;                         // …у найбіднішу
            transfer_begin(b->src, b->dst);
            b->state = BAL_BALANCE;
            b->t_state_ms = 0;
            b->t_balance_ms = 0;
        } else {
            b->state = BAL_IDLE;                    // розкид < start — нема за що
            b->t_state_ms = 0;
        }
        break;
    }

    case BAL_BALANCE: {
        b->t_balance_ms += TICK_MS;

        // Перегрів силового вузла АБО вичерпаний бюджет часу → остигати.
        if (power_node_too_hot() || b->t_balance_ms >= BAL_MAX_MS) {
            balancer_off();
            b->state = BAL_COOLDOWN;
            b->t_state_ms = 0;
            break;
        }

        // Переміряти й перевірити, чи вже зійшлись (гістерезис: stop < start).
        pack_state_t p;
        read_pack(&p);
        imbalance_t im = find_imbalance_metric(b, &p);
        b->spread_mv = im.spread_mv;

        if (im.spread_mv <= b->chem->stop_mv) {        // зійшлись тісно
            balancer_off();
            b->state = BAL_COOLDOWN;
            b->t_state_ms = 0;
            break;
        }

        // Найбідніша могла змінитись (особливо під розрядом) — переадресуємо.
        if (im.hi != b->src || im.lo != b->dst) {
            b->src = im.hi;
            b->dst = im.lo;
            transfer_begin(b->src, b->dst);         // перенаціляємо перенос
        }
        transfer_hold();                            // тримаємо струм цей такт
        break;
    }

    case BAL_COOLDOWN:
        // Силова частина вже знята; просто остигаємо потрібний час.
        if (b->t_state_ms >= COOLDOWN_MS) {
            b->state = BAL_IDLE;
            b->t_state_ms = 0;
        }
        break;
    }
}
