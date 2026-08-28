#define FRAME 256                        // PCM-відліків у кадрі
int16_t pcm[FRAME];                      // свіжі відліки (WAV, тон, радіо…)
uint8_t pdm[FRAME * OSR / 8];            // спакований однобітний потік

void play_block(void) {
    static pdm_state st = { .accum = 0 };   // стан ЖИВЕ між блоками — static!

    // ... сюди джерело поклало FRAME відліків у pcm ...

    pcm_to_pdm(&st, pcm, pdm, FRAME);       // 256 відліків → 1024 байти потоку
    // pdm тепер виштовхуємо в дріт: SPI, I2S-DMA чи біт-бенг у таймері.
    // Далі — обов'язкове усереднення на виході (RC або PDM-підсилювач).
}
