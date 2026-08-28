typedef enum { ST_RUN, ST_SAVING, ST_SLEEP } power_state_t;

// Пороги в мілівольтах (для випадку «контролер живиться прямо від Li-ion»).
#define V_WARN_MV      3400U   // нижче — тривога (починаємо згортатися)
#define V_CRIT_MV      3150U   // нижче — критично (останній флаш і сон)
#define V_RESUME_MV    3550U   // вище — назад у норму (гістерезис проти торохтіння)
#define CONFIRM_N      3U      // стільки вимірів поспіль має підтвердити падіння

static power_state_t state = ST_RUN;
static uint8_t low_count = 0;   // лічильник підтвердження «стало низько»

void power_fsm_tick(void) {
    uint16_t v = read_vcc_filtered_mv();   // згладжений вимір, мВ

    switch (state) {
    case ST_RUN:
        if (v < V_WARN_MV) {
            if (++low_count >= CONFIRM_N) {   // не сплеск, а стале падіння
                begin_graceful_save();        // почати згортання (див. нижче)
                state = ST_SAVING;
                low_count = 0;
            }
        } else {
            low_count = 0;                    // напруга ще здорова — скидаємо лічильник
        }
        break;

    case ST_SAVING:
        if (v < V_CRIT_MV) {
            final_flush_and_park();           // останній обов'язковий флаш
            enter_deep_sleep();               // або вимкнення живлення
            state = ST_SLEEP;
        } else if (v > V_RESUME_MV) {
            resume_normal_operation();        // батарея відновилась (напр., підзарядка)
            state = ST_RUN;
        }
        // між V_CRIT і V_RESUME лишаємось у SAVING — та сама «мертва зона»
        break;

    case ST_SLEEP:
        // Прокидаємось лише за зовнішньою подією (підзарядка/скид).
        if (v > V_RESUME_MV) { resume_normal_operation(); state = ST_RUN; }
        break;
    }
}
