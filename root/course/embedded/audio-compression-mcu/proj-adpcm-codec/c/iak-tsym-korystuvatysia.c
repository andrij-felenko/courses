#define FRAME 512   // відліків у кадрі (парне число — рівно FRAME/2 байтів)

int16_t  pcm_in[FRAME];              // з мікрофона (DMA-буфер)
uint8_t  packed[FRAME / 2];          // стиснене — рівно вчетверо менше
int16_t  pcm_out[FRAME];             // відновлене (для перевірки / відтворення)

void demo(void) {
    adpcm_state enc = { .predict = 0, .index = 0 };   // стан кодера
    adpcm_state dec = { .predict = 0, .index = 0 };   // стан декодера — окремий!

    // ... сюди DMA поклав FRAME свіжих відліків у pcm_in ...

    adpcm_encode(&enc, pcm_in, packed, FRAME);   // 512 відліків -> 256 байтів
    // packed тепер можна писати на SD або слати по радіо

    adpcm_decode(&dec, packed, pcm_out, FRAME);  // 256 байтів -> 512 відліків
    // pcm_out ≈ pcm_in (з невеликою похибкою квантування)
}
