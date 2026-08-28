// Один сторож на весь час роботи; свій контекст, без malloc.
static vad_t g_vad;

void audio_task_init(void)
{
    vad_config_t cfg;
    vad_config_default(&cfg);          // або заповни під свій мікрофон
    vad_init(&g_vad, &cfg);
}

// Головний цикл захоплення: забрали кадр із кільця → згодували сторожу →
// на прапорці підняли/тримаємо важкий модуль.
void audio_task_step(void)
{
    int16_t frame[256];

    // Забрати наступний готовий кадр із кільцевого буфера захоплення.
    // (ring_pop блокує рівно доти, доки кадр не готовий, або віддає false.)
    if (!capture_ring_pop(frame, 256))
        return;                        // кадру ще нема — вийти, не крутити цикл

    bool event = vad_feed(&g_vad, frame);

    if (event) {
        heavy_consumer_feed(frame);    // запис / стиснення / KWS — на живому кадрі
    } else {
        heavy_consumer_idle();         // прибрати важке в сон до наступної події
    }
}
