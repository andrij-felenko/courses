// вагові коефіцієнти вразливості каналів: синій старіє ~3× швидше
// (порядкова оцінка; точні числа залежать від матеріалу панелі)
#define WEAR_W_R  10u
#define WEAR_W_G  10u
#define WEAR_W_B  30u   // ~3× за R/G

// накопичити знос за один інтервал dt_ms.
// avg_r/g/b — середня яскравість каналу по екрану за цей інтервал (0..255)
void wear_accumulate(disp_guard_t *g,
                     uint8_t avg_r, uint8_t avg_g, uint8_t avg_b,
                     uint32_t dt_ms) {
    // одиниця зносу = яскравість × вага × час; масштаб умовний, важлива лише пропорція
    g->wear_r += (uint64_t)avg_r * WEAR_W_R * dt_ms;
    g->wear_g += (uint64_t)avg_g * WEAR_W_G * dt_ms;
    g->wear_b += (uint64_t)avg_b * WEAR_W_B * dt_ms;
}
