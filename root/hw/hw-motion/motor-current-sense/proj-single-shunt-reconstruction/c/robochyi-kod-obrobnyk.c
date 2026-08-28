// Планування відліків для реконструкції з одного DC-link-шунта.
// Викликати раз за період ШІМ, отримавши нові шпаруватості d_a,d_b,d_c ∈ [0..1].
// PWM центрований; ARR — період таймера в тіках; канали CCR1..3 — самі імпульси,
// CCR4/CCR5 — два моменти запуску АЦП.

#define PWM_ARR        4199u        // період таймера (тіків до вершини)
#define T_MIN_TICKS      80u        // T_min = dead+settle+sample у тіках таймера
#define HALF_SAMPLE      (T_MIN_TICKS / 2u)

// Впорядковані фази за спаданням шпаруватості: max, mid, min.
typedef struct { uint8_t hi, mid, lo; } phase_order_t;

// Стан для обробника АЦП: які дві фази читаємо цього періоду і в якому знаку.
typedef struct {
    int8_t  ph1, sgn1;   // перший відлік: індекс фази (0=A,1=B,2=C) і знак
    int8_t  ph2, sgn2;   // другий відлік
    uint8_t blind;       // 1 — вікон не вистачило, добираємо із сусіднього періоду
} recon_plan_t;

static volatile recon_plan_t g_plan;

// Відсортувати три шпаруватості, повернути порядок індексів (hi,mid,lo).
static phase_order_t order3(uint16_t da, uint16_t db, uint16_t dc) {
    uint16_t d[3] = { da, db, dc };
    uint8_t  idx[3] = { 0, 1, 2 };
    for (uint8_t i = 0; i < 2; i++)            // проста сортування трьох
        for (uint8_t j = 0; j < 2 - i; j++)
            if (d[idx[j]] < d[idx[j + 1]]) {
                uint8_t t = idx[j]; idx[j] = idx[j + 1]; idx[j + 1] = t;
            }
    phase_order_t o = { idx[0], idx[1], idx[2] };
    return o;
}

// Головне: розрахувати вікна, за потреби розсунути фронти, спланувати відліки.
void ss_plan_period(uint16_t ccr_a, uint16_t ccr_b, uint16_t ccr_c) {
    // ccr_* — тіки «верхній ключ увімкнено» для кожної фази (більше = довша шпаруватість).
    phase_order_t o = order3(ccr_a, ccr_b, ccr_c);
    uint16_t ccr[3] = { ccr_a, ccr_b, ccr_c };

    // Ширини двох активних вікон = різниці сусідніх (упорядкованих) шпаруватостей.
    // Для центрованого ШІМ фронти симетричні, тож у тіках півперіоду це просто різниці.
    int32_t w1 = (int32_t)ccr[o.hi]  - (int32_t)ccr[o.mid];   // вікно «видно фазу hi»
    int32_t w2 = (int32_t)ccr[o.mid] - (int32_t)ccr[o.lo];    // вікно «видно фазу lo»

    // За таблицею вектора: у вікні, де відкритий лише верхній ключ фази hi,
    // у шунті тече +i_hi; у вікні, де відкриті hi та mid (закрита lo), тече −i_lo.
    recon_plan_t p;
    p.ph1 = o.hi; p.sgn1 = +1;   // перший активний вектор бачить +i_hi
    p.ph2 = o.lo; p.sgn2 = -1;   // другий активний вектор бачить −i_lo
    p.blind = 0;

    // Чи обидва вікна ширші за T_min? Якщо так — просто ставимо відліки в їхні центри.
    if (w1 >= T_MIN_TICKS && w2 >= T_MIN_TICKS) {
        // Момент відліку = центр вікна. Для центрованого ШІМ вікна лежать між
        // фронтами вимикання ключів; беремо середину відповідного інтервалу.
        uint16_t s1 = (uint16_t)((ccr[o.hi]  + ccr[o.mid]) / 2);
        uint16_t s2 = (uint16_t)((ccr[o.mid] + ccr[o.lo])  / 2);
        LL_TIM_OC_SetCompareCH4(TIM1, s1);   // запуск АЦП №1
        LL_TIM_OC_SetCompareCH5(TIM1, s2);   // запуск АЦП №2
    }
    // Одне вікно вузьке, друге широке: розсуваємо вузьке до T_min, зсунувши
    // фронт відповідної фази. Ширину імпульсу НЕ чіпаємо (середня напруга ціла) —
    // зсуваємо весь імпульс, компенсуючи протилежним зсувом у другій половині періоду.
    else if (w1 >= T_MIN_TICKS || w2 >= T_MIN_TICKS) {
        // Обидва вузькі вікна межують із СЕРЕДНЬОЮ фазою (mid), тож зсуваємо саме її
        // фронт — геть від того сусіда, до якого вона «прилипла».
        uint8_t victim = o.mid;
        uint16_t shifted;
        if (w1 < T_MIN_TICKS) {                 // прилипла до hi — відсунути вниз, розтягнути w1
            shifted = (uint16_t)(ccr[victim] - (T_MIN_TICKS - w1));
        } else {                                // прилипла до lo — посунути вгору, розтягнути w2
            shifted = (uint16_t)(ccr[victim] + (T_MIN_TICKS - w2));
        }
        apply_edge_shift(victim, shifted);   // оновити CCR + дзеркальну компенсацію
        ccr[victim] = shifted;
        uint16_t s1 = (uint16_t)((ccr[o.hi]  + ccr[o.mid]) / 2);
        uint16_t s2 = (uint16_t)((ccr[o.mid] + ccr[o.lo])  / 2);
        LL_TIM_OC_SetCompareCH4(TIM1, s1);
        LL_TIM_OC_SetCompareCH5(TIM1, s2);
    }
    // Обидва вікна вузькі: розсуванням не врятувати (немає куди). Беремо той
    // єдиний відлік, що вдасться, а другу фазу добираємо із сусіднього періоду.
    else {
        p.blind = 1;
        uint16_t s1 = (uint16_t)((ccr[o.hi] + ccr[o.mid]) / 2);
        LL_TIM_OC_SetCompareCH4(TIM1, s1);           // лишаємо один чесний відлік
        LL_TIM_OC_SetCompareCH5(TIM1, s1 + HALF_SAMPLE);  // другий — марний, ігноруємо
    }

    g_plan = p;
}
