#define BLOCK  256
static int16_t buf[BLOCK];

void audio_task(void) {
    for (;;) {
        size_t got = i2s_read_block(buf, BLOCK);   // блокує, поки блок не готовий
        if (got == BLOCK) {
            dc_block(buf, BLOCK);                   // прибрали постійний зсув
            process(buf, BLOCK);                    // рівень, фільтр, детекція...
        }
    }
}
