void pm_poll(pm_channel_t *ch, pm_read_adc_t read, const pm_actions_t *act) {
    const pm_config_t *c = ch->cfg;

    uint16_t code = read();                    // один сирий відлік
    uint16_t avg  = ring_avg(ch, code);        // усереднений код
    ch->bus_mv    = code_to_bus_mv(c, avg);    // напруга шини, мВ

    pm_class_t want = classify(c, ch->bus_mv, ch->st);

    // Підтвердження серією: різні класи мають різну «терплячість».
    // OK — це «добре», будь-яка аварія — «погано».
    if (want == PM_OK) {
        ch->bad_run = 0u;
        if (ch->good_run < 0xFFu) ch->good_run++;
    } else {
        ch->good_run = 0u;
        if (ch->bad_run < 0xFFu) ch->bad_run++;
    }

    // Скільки підтверджень треба саме для ЦЬОГО переходу.
    uint8_t need;
    switch (want) {
        case PM_DEAD:     need = c->confirm_dead; break;  // мертву ловимо швидко
        case PM_BODYDIODE:need = c->confirm_dead; break;  // так само швидко
        case PM_SAG:      need = c->confirm_sag;  break;  // просад — терплячіше
        default:          need = c->confirm_ok;   break;  // назад у норму — нехотя
    }

    // Перехід стається лише коли серія добігла потрібної довжини
    // І новий клас відрізняється від поточного.
    bool enough = (want == PM_OK) ? (ch->good_run >= need)
                                  : (ch->bad_run  >= need);
    if (!enough || want == ch->st) return;     // ще не впевнені або нема зміни

    // ── ПЕРЕХІД: тут і тільки тут смикаємо реакції ──────────────────────────
    pm_class_t prev = ch->st;
    ch->st = want;

    if (want != PM_OK) {
        // Входимо в будь-яку аварію: спершу — рятуємо, тоді роз'єднуємо.
        ch->flag_latched = true;               // липкий прапорець для сервісу
        if (act && act->save_state) act->save_state();   // поки є заряд у C
        if (act && act->set_load)   act->set_load(false);// зняти навантаження
    } else {
        // Повертаємось у норму з аварії: знову дозволяємо навантаження.
        if (act && act->set_load)   act->set_load(true);
    }
    if (act && act->on_class) act->on_class(want);       // індикація/лог завжди

    (void)prev;   // (за потреби — журналювати перехід prev→want)
}

pm_class_t pm_class(const pm_channel_t *ch)        { return ch->st; }
uint16_t   pm_bus_mv(const pm_channel_t *ch)       { return ch->bus_mv; }
bool       pm_fault_latched(const pm_channel_t *ch){ return ch->flag_latched; }
