// ─── власний пул фіксованих буферів (краще за malloc/free —
//     причини: фрагментація купи) ────────────────────────────────
struct Frame { uint8_t data[256]; uint16_t len; };
static StaticQueue_t   poolSQ;
static uint8_t         poolBuf[4 * sizeof(Frame*)];
static QueueHandle_t   framePool;   // черга вільних вказівників

// PRODUCER: взяти з пулу, заповнити, передати
void taskADC(void*) {
    for (;;) {
        Frame* f = NULL;
        xQueueReceive(framePool, &f, portMAX_DELAY); // чекаємо вільний слот
        // заповнюємо буфер
        f->len = spi_read(f->data, sizeof(f->data));
        // send ТІЛЬКИ вказівника — копіювання 256 байт не відбувається
        xQueueSend(qFrames, &f, portMAX_DELAY);
        f = NULL;   // ← виробник «забуває» вказівник: більше не торкається
    }
}

// CONSUMER: прийняти вказівник, вжити, повернути у пул
void taskProcessor(void*) {
    for (;;) {
        Frame* f = NULL;
        xQueueReceive(qFrames, &f, portMAX_DELAY);
        process(f->data, f->len);
        xQueueSend(framePool, &f, 0); // повернули у пул; f тепер NULL у нас
    }
}
