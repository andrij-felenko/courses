// «теплий старт»: наводимо bias на середнє першого блоку, щоб не чекати усталення
static int32_t bias = 0;
static int primed = 0;

void dc_block_primed(int16_t *samples, int n) {
    if (!primed) {
        int32_t acc = 0;
        for (int i = 0; i < n; i++) acc += samples[i];
        bias = (acc / n) << 16;   // одразу ставимо оцінку в середину першого блоку
        primed = 1;
    }
    for (int i = 0; i < n; i++) {
        int32_t x = (int32_t)samples[i] << 16;
        bias += (x - bias) >> 10;
        samples[i] = (int16_t)((x - bias) >> 16);
    }
}
