#include <stdint.h>
#include <string.h>

#define FS         48000u        // частота відліків, Гц
#define CHANNELS   2u            // стерео
#define FRAMES     256u          // стереовідліків у одному буфері (див. розрахунок нижче)
#define WORDS      (FRAMES * CHANNELS)   // слів int16 у буфері: L,R × FRAMES

// Два буфери в RAM, доступній DMA. Живуть увесь час роботи → static.
static int16_t buf_a[WORDS];
static int16_t buf_b[WORDS];

// Два DMA-дескриптори, зчеплені в кільце: A → B → A → ...
static dma_desc_t desc[2];

// Прапорець «який буфер щойно звільнив DMA» — виставляє ISR, читає main-цикл.
static volatile int free_idx = -1;

void i2s_stream_start(void) {
    // 1) частоти й формат — з попередніх кроків
    i2s_format_t fmt = { .sample_rate = FS, .bits = 16,
                         .channels = CHANNELS, .need_mclk = 1 };
    i2s_tx_set_clocks(&fmt);
    i2s_tx_set_format(I2S_FMT_PHILIPS, 16, CHANNELS);

    // 2) заповнити ОБИДВА буфери наперед, поки DMA ще стоїть, — щоб на
    //    старті вже було що лити (інакше перший же кадр буде тишею)
    fill_sine(buf_a, FRAMES, FS, 440.0, 0.5);
    fill_sine(buf_b, FRAMES, FS, 440.0, 0.5);

    // 3) описати буфери вузлами й замкнути в кільце (next останнього → перший)
    desc[0] = (dma_desc_t){ .buf = (uint8_t*)buf_a, .length = sizeof(buf_a),
                            .size = sizeof(buf_a), .owner = 1, .eof = 1,
                            .next = &desc[1] };
    desc[1] = (dma_desc_t){ .buf = (uint8_t*)buf_b, .length = sizeof(buf_b),
                            .size = sizeof(buf_b), .owner = 1, .eof = 1,
                            .next = &desc[0] };   // ← кільце: назад на перший

    // 4) один старт: даємо адресу першого вузла, вмикаємо переривання «вузол
    //    доллято», пускаємо передавач — далі DMA крутить кільце сам
    i2s_tx_enable_irq(I2S_TX_EOF);      // переривання на межі кожного буфера
    dma_start_tx(&desc[0]);
    i2s_tx_start();
}

// Переривання: DMA доллято черговий буфер. Кажемо main-циклу, який саме
// звільнився, щоб той його наповнив. У самій ISR НІЧОГО важкого не рахуємо.
void i2s_tx_isr(void) {
    dma_desc_t *done = dma_current_eof_desc();   // який вузол щойно доллято
    free_idx = (done == &desc[0]) ? 0 : 1;       // 0 → buf_a вільний, 1 → buf_b
    dma_clear_eof_flag();
}

// Головний цикл: наповнює той буфер, що звільнився. Устигнути треба ДО того,
// як DMA доллє інший буфер, — у цьому весь запас часу подвійної буферизації.
void i2s_stream_service(void) {
    if (free_idx == 0) { fill_sine(buf_a, FRAMES, FS, 440.0, 0.5); free_idx = -1; }
    if (free_idx == 1) { fill_sine(buf_b, FRAMES, FS, 440.0, 0.5); free_idx = -1; }
}
