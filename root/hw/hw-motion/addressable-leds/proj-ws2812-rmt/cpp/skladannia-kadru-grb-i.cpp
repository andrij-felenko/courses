#define N_PIXELS  60
#define DATA_PIN  5       // ніжка даних стрічки

struct RGB { uint8_t r, g, b; };   // буфер кольорів у логіці програми
RGB pix[N_PIXELS];

rmt_data_t sym[N_PIXELS * 24];     // 24 символи на піксель

void ws2812_setup() {
    // tick = 1/10_000_000 = 0.1 мкс
    rmtInit(DATA_PIN, RMT_TX_MODE, RMT_MEM_NUM_BLOCKS_1, 10000000);
}

void ws2812_show() {
    for (int i = 0; i < N_PIXELS; i++) {
        // GRB — НЕ RGB! (типова пастка WS2812)
        encodeByte(pix[i].g, &sym[i * 24 + 0]);   // G першим
        encodeByte(pix[i].r, &sym[i * 24 + 8]);   // R другим
        encodeByte(pix[i].b, &sym[i * 24 + 16]);  // B третім
    }
    // RMT жене всі N*24 символи; CPU вільний одразу після виклику
    rmtWrite(DATA_PIN, sym, N_PIXELS * 24, RMT_WAIT_TX_DONE);
    // Скидання ≥50 мкс — зазвичай вистачає паузи між двома викликами ws2812_show();
    // якщо треба явно — delayMicroseconds(60)
}
