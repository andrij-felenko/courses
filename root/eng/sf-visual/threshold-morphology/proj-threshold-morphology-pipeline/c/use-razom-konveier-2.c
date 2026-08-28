static uint8_t gray[H][W];      // заповнюється з камери (DMA/опитування)
static uint8_t mask[H][W];      // вихід

void on_frame(void) {
    // gray[][] уже містить свіжий сірий кадр
    uint32_t area = pipeline(gray, mask);

    // частка кадру, зайнята виділеним
    float frac = (float)area / (float)(H * W);

    if (frac > 0.03f) {
        // об'єкт у кадрі — реагуємо (лічильник, тривога, наведення…)
    }
    // mask[][] тепер чиста бінарна маска, готова до пошуку об'єктів
}
