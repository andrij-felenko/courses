#define PDM_BYTES  256                 // байтів PDM у блоці з DMA
#define PCM_OUT    (PDM_BYTES * 8 / CIC_D)   // 256·8/64 = 32 відліки PCM

static uint8_t pdm_buf[PDM_BYTES];
static int16_t pcm_buf[PCM_OUT];

void audio_task_pdm(void) {
    for (;;) {
        size_t got = pdm_read_block(pdm_buf, PDM_BYTES);  // блок 1-бітного потоку
        if (got == PDM_BYTES) {
            int n = pdm_decimate_cic(pdm_buf, PDM_BYTES, pcm_buf);  // ← PDM → PCM
            dc_block(pcm_buf, n);        // прибрали залишковий зсув
            process(pcm_buf, n);         // рівень, фільтр, детекція — як завжди
        }
    }
}
