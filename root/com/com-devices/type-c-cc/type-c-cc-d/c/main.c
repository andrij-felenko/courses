// Пристрій лише міряє напругу на активному CC і вирішує стелю.
uint16_t v_cc = adc_read_mv(PIN_CC1);   // напр., 1680 мВ від джерела з Rp 10к

uint16_t budget_ma;
if      (v_cc < 200)   budget_ma = 0;     // нема джерела — CC «висить»
else if (v_cc < 660)   budget_ma = 500;   // ≈0.41 В → звичайний USB
else if (v_cc < 1230)  budget_ma = 1500;  // ≈0.92 В → 1.5 А
else                   budget_ma = 3000;  // ≈1.68 В → повні 3.0 А

set_input_current_limit(budget_ma);       // 1680 мВ → 3000 мА = 15 Вт при 5 В
