// Класифікація за матрицею напруга×струм (ядро з детального кроку).
// Чиста функція: тільки цифри → діагноз, без жодного стану.
static pwr_diag_t classify(const pwr_cfg_t *cfg,
                           uint16_t vbus_mv, uint16_t i_ma) {
    if (vbus_mv < cfg->vbus_dead_mv)          // майже нуль — шукай контакт
        return PWR_NO_POWER;

    bool sag = (vbus_mv < cfg->vbus_sag_mv);           // напруга просіла?
    bool low_i = (i_ma < cfg->i_expect_ma / 2);        // струм сильно малий?

    if ( sag && !low_i) return PWR_CABLE_DROP;   // тягнемо, а напруга падає → кабель
    if ( sag &&  low_i) return PWR_SOFT_SOURCE;  // і те, і те → м'який блок
    if (!sag &&  low_i) return PWR_NEGOTIATION;  // напруга є, струму нема → переговори
    return PWR_OK;                               // тримається й тягне → усе добре
}

void pwr_diag_init(pwr_diag_ctx_t *c, const pwr_cfg_t *cfg) {
    c->cfg         = cfg;
    c->diag        = PWR_OK;      // доки не виміряли — підстав тривожити нема
    c->pending     = PWR_OK;
    c->pending_run = 0u;
    c->low_power   = false;
    c->vbus_mv     = cfg->vbus_nominal_mv;
    c->i_charge_ma = 0u;
    c->valid       = false;
}

pwr_diag_t pwr_diag_step(pwr_diag_ctx_t *c) {
    const pwr_cfg_t *cfg = c->cfg;

    // 1. Виміряти. VBUS усереднюємо ЗАВЖДИ (для brownout він потрібен і на холостому).
    uint16_t vbus = vbus_averaged(cfg->adc_avg_log2);
    uint16_t i_ma = hw_charge_current_ma();
    c->vbus_mv     = vbus;
    c->i_charge_ma = i_ma;

    // 2. Гістерезис brownout — його рахуємо КОЖЕН цикл, він не залежить від струму.
    //    Падаємо в стишення на TRIP, вертаємось лише на CLEAR (вище, із запасом).
    if (!c->low_power && vbus < cfg->brownout_trip_mv) {
        c->low_power = true;      // просіли — стишуємо апетит, а не падаємо
    } else if (c->low_power && vbus > cfg->brownout_clear_mv) {
        c->low_power = false;     // повернулось із запасом — знову повний режим
    }
    // проміжок TRIP..CLEAR — «мертва зона»: нічого не міняємо (проти дрижання)

    // 3. Класифікацію робимо ЛИШЕ під навантаженням: на холостому падіння=0,
    //    і будь-який діагноз, крім OK, там просто неможливий і безглуздий.
    if (i_ma < cfg->i_load_min_ma) {
        c->pending_run = 0u;     // скинути дебаунс: без навантаження не судимо
        return c->diag;          // віддаємо останній стабільний діагноз
    }
    c->valid = true;             // був хоч один вимір під навантаженням

    // 4. Сирий діагноз цього циклу.
    pwr_diag_t raw = classify(cfg, vbus, i_ma);

    // 5. Дебаунс: новий діагноз мусить вистоятися debounce_cycles поспіль,
    //    перш ніж стати ПРИЙНЯТИМ. Це той самий гістерезис, що й у brownout,
    //    але на дискретному стані замість напруги.
    if (raw == c->pending) {
        if (c->pending_run < 0xFFu) c->pending_run++;
    } else {
        c->pending     = raw;    // з'явився новий кандидат — рахуємо з нуля
        c->pending_run = 1u;
    }
    if (c->pending_run >= cfg->debounce_cycles) {
        c->diag = c->pending;    // кандидат вистояв — приймаємо
    }
    return c->diag;
}

bool pwr_low_power(const pwr_diag_ctx_t *c) { return c->low_power; }
