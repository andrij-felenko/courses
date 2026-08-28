// Термінація Li-ion за спадом струму у фазі сталої напруги.
#define CAP_MAH        2000      // ємність комірки, мА·год
#define I_TERM_MA      (CAP_MAH / 10)   // поріг C/10 = 200 мА
#define V_CV_MV        4200      // стеля напруги фази CV
#define DEBOUNCE_N     3         // скільки вимірів поспіль під порогом

static uint8_t below_cnt = 0;

// Повертає true, коли заряд треба зупинити.
bool charge_done(uint16_t vcell_mv, uint16_t icharge_ma) {
    // Термінація за струмом чинна ЛИШЕ у фазі CV: напруга вже на стелі.
    if (vcell_mv < V_CV_MV - 20)         // ще у фазі CC — рано
        return false;
    if (icharge_ma < I_TERM_MA) {
        if (++below_cnt >= DEBOUNCE_N)   // стабільно нижче порога
            return true;                 // → повна, вимикаємо
    } else {
        below_cnt = 0;                   // струм підскочив — лічильник назад
    }
    return false;
}
