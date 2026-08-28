// Еталон: разова causal-згортка по цілому вікну in[T][cin] → out[T][cout].
// Та сама арифметика, що в conv_step, але «розкотана» на всі T колонок.
static void conv_batch(const ConvLayer *L, int T,
                       const int8_t in[/*T*/][CIN_MAX],
                       int8_t out[/*T*/][COUT_MAX]) {
    for (int t = 0; t < T; t++) {
        for (int oc = 0; oc < L->cout; oc++) {
            int32_t acc = L->bias[oc];
            for (int i = 0; i < L->kt; i++) {
                int ti = t - (L->kt - 1) + i;          // causal-віконце: назад у часі
                if (ti < 0) continue;                  // ліворуч від початку — нулі (padding)
                const int8_t *wij = &L->w[(oc * L->kt + i) * L->cin];
                for (int c = 0; c < L->cin; c++)
                    acc += (int32_t)wij[c] * ((int32_t)in[ti][c] - L->in_zp);
            }
            int32_t q = (int32_t)lroundf(acc * L->out_scale) + L->out_zp;
            if (q < L->out_zp) q = L->out_zp;
            if (q < -128) q = -128;
            if (q >  127) q =  127;
            out[t][oc] = (int8_t)q;
        }
    }
}
