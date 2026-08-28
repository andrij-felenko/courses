// Практичний варіант: тримаємо поточний (кадр, стан) і докручуємо вперед.
static uint16_t g_state;
static uint32_t g_frame;

uint8_t channel_advance(uint16_t seed, uint32_t target_frame) {
    if (target_frame < g_frame) {               // рідко: стрибок назад/скидання
        g_state = lfsr16_seed(seed);
        g_frame = 0;
    }
    while (g_frame < target_frame) {            // докрутити лише різницю
        g_state = lfsr16_step(g_state);
        g_frame++;
    }
    return chan_perm[g_state % N_CH];
}
