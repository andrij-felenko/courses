// I2S-аудіо через DMA: ядро торкається не байтів, а готових блоків.
#define FRAME   256                 // вибірок на буфер
static int32_t buf[FRAME];          // приймач блоку від DMA

void audio_task(void) {
    size_t got = 0;
    while (1) {
        // Блокуємось, доки DMA НЕ наповнить буфер цілком.
        // Ядро тут спить — жодного байта воно не торкнулось.
        i2s_channel_read(rx, buf, sizeof(buf), &got, portMAX_DELAY);

        // Тепер маємо got/4 готових вибірок — одна корисна дія на цілий блок,
        // а не одне переривання на кожен відлік.
        process_block(buf, got / sizeof(int32_t));
    }
}
