// Приймає одну нову вхідну колонку (cin значень int8), кладе її в кільце й
// рахує ОДНУ нову вихідну колонку (cout значень int8) у out_col[].
// Повертає false, доки кільце ще не набралося kt колонок (causal-«прогрів»).
static bool conv_step(ConvLayer *L, const int8_t in_col[], int8_t out_col[]) {
    // 1. Заштовхнути свіжу колонку в кільце, затерши найстарішу.
    memcpy(L->ring[L->w_head], in_col, L->cin * sizeof(int8_t));
    L->w_head = (L->w_head + 1) % L->kt;
    if (L->filled < L->kt) { L->filled++; return false; }   // ще прогріваємось

    // 2. Порахувати одну вихідну колонку: для кожного вихідного каналу —
    //    сума по ЧАСОВОМУ віконцю (kt колонок) × вхідних каналах.
    for (int oc = 0; oc < L->cout; oc++) {
        int32_t acc = L->bias[oc];
        for (int i = 0; i < L->kt; i++) {
            // i-та за ЧАСОМ колонка кільця — ось де вирівнювання по w_head:
            const int8_t *col = L->ring[(L->w_head + i) % L->kt];
            const int8_t *wij = &L->w[(oc * L->kt + i) * L->cin];   // ваги цього (oc,час)
            for (int c = 0; c < L->cin; c++)
                acc += (int32_t)wij[c] * ((int32_t)col[c] - L->in_zp);
        }
        // 3. Квантувати суму назад у int8 виходу + ReLU (обрізання знизу нулем зсуву).
        //    (у справжньому TFLite тут requant цілим множником-зсувом; float — для ясності)
        int32_t q = (int32_t)lroundf(acc * L->out_scale) + L->out_zp;
        if (q < L->out_zp) q = L->out_zp;          // ReLU: нижче нуля-активації не пускаємо
        if (q < -128) q = -128;                     // ОБРІЗАННЯ int8, без нього зашкал
        if (q >  127) q =  127;                     //   обгорнеться по колу
        out_col[oc] = (int8_t)q;
    }
    return true;
}
