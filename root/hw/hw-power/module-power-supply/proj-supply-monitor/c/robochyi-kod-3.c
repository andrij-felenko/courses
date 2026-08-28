typedef enum { PWR_OK, PWR_SAG, PWR_RECOVER } pwr_state_t;

static pwr_state_t pwr_state = PWR_OK;
static uint16_t    recover_cnt = 0;     // скільки поспіль добрих замірів у RECOVER

// Викликати періодично (напр. з таймера раз на 5 мс) зі свіжим кодом VREFINT.
// Уся логіка порогів + гістерезис зібрана тут.
void pwr_monitor_step(uint16_t vref_raw) {
    uint16_t vdd = read_vdd_mv(vref_raw);

    switch (pwr_state) {
    case PWR_OK:
        if (vdd < V_SAG_MV)                 // провалилось нижче нижнього порога
            pwr_state = PWR_SAG;            // → важкі дії заборонені
        break;

    case PWR_SAG:
        if (vdd > V_OK_MV) {                // піднялось вище ВЕРХНЬОГО порога
            pwr_state = PWR_RECOVER;        // → карантин, ще не довіряємо
            recover_cnt = 0;
        }
        break;

    case PWR_RECOVER:
        if (vdd < V_SAG_MV) {               // знову провалилось, поки чекали
            pwr_state = PWR_SAG;            // → назад у SAG, лічильник скинути
        } else if (++recover_cnt >= RECOVER_HOLD) {
            pwr_state = PWR_OK;             // протрималось стабільно → повна довіра
        }
        break;
    }
}

// Єдине вікно у світ для решти прошивки: чи безпечні зараз важкі дії?
bool pwr_heavy_ok(void) { return pwr_state == PWR_OK; }
