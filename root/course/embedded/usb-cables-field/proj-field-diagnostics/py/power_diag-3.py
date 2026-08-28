# power_diag.py (продовження)

# Класифікація за матрицею напруга×струм (ядро з детального кроку).
# Чиста функція: тільки цифри → діагноз, без жодного стану.
def classify(cfg: PwrCfg, vbus_mv: int, i_ma: int) -> PwrDiag:
    if vbus_mv < cfg.vbus_dead_mv:               # майже нуль — шукай контакт
        return PwrDiag.NO_POWER

    sag   = vbus_mv < cfg.vbus_sag_mv            # напруга просіла?
    low_i = i_ma < cfg.i_expect_ma // 2          # струм сильно малий?

    if sag and not low_i: return PwrDiag.CABLE_DROP   # тягнемо, а напруга падає → кабель
    if sag and low_i:     return PwrDiag.SOFT_SOURCE  # і те, і те → м'який блок
    if not sag and low_i: return PwrDiag.NEGOTIATION  # напруга є, струму нема → переговори
    return PwrDiag.OK                                 # тримається й тягне → усе добре


# --- далі методи класу PwrDiagCtx (той самий клас, що з __init__ вище) ---

    def step(self) -> PwrDiag:
        cfg = self.cfg

        # 1. Виміряти. VBUS усереднюємо ЗАВЖДИ (для brownout він потрібен і на холостому).
        vbus = vbus_averaged(cfg.adc_avg_log2)
        i_ma = hw_charge_current_ma()
        self.vbus_mv     = vbus
        self.i_charge_ma = i_ma

        # 2. Гістерезис brownout — його рахуємо КОЖЕН цикл, він не залежить від струму.
        #    Падаємо в стишення на TRIP, вертаємось лише на CLEAR (вище, із запасом).
        if not self.low_power and vbus < cfg.brownout_trip_mv:
            self.low_power = True     # просіли — стишуємо апетит, а не падаємо
        elif self.low_power and vbus > cfg.brownout_clear_mv:
            self.low_power = False    # повернулось із запасом — знову повний режим
        # проміжок TRIP..CLEAR — «мертва зона»: нічого не міняємо (проти дрижання)

        # 3. Класифікацію робимо ЛИШЕ під навантаженням: на холостому падіння=0,
        #    і будь-який діагноз, крім OK, там просто неможливий і безглуздий.
        if i_ma < cfg.i_load_min_ma:
            self.pending_run = 0      # скинути дебаунс: без навантаження не судимо
            return self.diag          # віддаємо останній стабільний діагноз
        self.valid = True             # був хоч один вимір під навантаженням

        # 4. Сирий діагноз цього циклу.
        raw = classify(cfg, vbus, i_ma)

        # 5. Дебаунс: новий діагноз мусить вистоятися debounce_cycles поспіль,
        #    перш ніж стати ПРИЙНЯТИМ. Це той самий гістерезис, що й у brownout,
        #    але на дискретному стані замість напруги.
        if raw == self.pending:
            self.pending_run += 1
        else:
            self.pending     = raw    # з'явився новий кандидат — рахуємо з нуля
            self.pending_run = 1
        if self.pending_run >= cfg.debounce_cycles:
            self.diag = self.pending  # кандидат вистояв — приймаємо
        return self.diag

    def pwr_low_power(self) -> bool:
        return self.low_power
