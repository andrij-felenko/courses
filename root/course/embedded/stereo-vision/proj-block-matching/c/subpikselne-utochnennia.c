// уточнення цілого диспаритету best_d до субпіксельного.
// c_lo, c_mid, c_hi — SAD на best_d−1, best_d, best_d+1.
// повертає диспаритет, помножений на 16 (формат Q4: 4 дробові біти),
// щоб лишитися в цілих числах — на МК це звично і швидко.
static int subpixel_refine(int best_d, uint32_t c_lo,
                           uint32_t c_mid, uint32_t c_hi)
{
    int num = (int)c_lo - (int)c_hi;             // перекіс плечей
    int den = (int)c_lo - 2 * (int)c_mid + (int)c_hi;  // кривина дна (>0)

    if (den <= 0)                  // дно не опукле — параболі нема за що зачепитися
        return best_d << 4;        // лишаємо ціле (·16)

    // поправка (num / (2·den)) у межах ±0.5; ведемо її в Q4 без float:
    //   correction_Q4 = round( 16 · num / (2·den) ) = (8·num) / den, з округленням
    int corr_q4 = (8 * num + (num >= 0 ? den : -den) / 2) / den;

    // страховка: поправка не може вийти за ±0.5 пікселя (±8 у Q4)
    if (corr_q4 >  8) corr_q4 =  8;
    if (corr_q4 < -8) corr_q4 = -8;

    return (best_d << 4) + corr_q4;
}
