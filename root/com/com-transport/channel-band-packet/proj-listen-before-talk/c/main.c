#define SLOT_US     9      // тривалість одного "слота" тиші, мкс
#define DIFS_US     34     // канал має бути вільним стільки перед стартом
#define CW_MIN      15     // початковий діапазон відступу (слотів)
#define CW_MAX      1023   // стеля діапазону

// апаратне: чи зайнятий ефір просто зараз
extern bool channel_busy(void);

// чекати, доки канал не буде вільним суцільно gap_us мікросекунд
static void wait_idle_for(uint32_t gap_us) {
    for (;;) {
        while (channel_busy()) { /* зайнято — чекаємо звільнення */ }
        uint32_t t0 = micros();
        while (!channel_busy()) {
            if (micros() - t0 >= gap_us) return;   // витримали всю тишу
        }
        // хтось заговорив посеред паузи — починаємо відлік тиші наново
    }
}

// одна спроба надіслати кадр; повертає true, якщо прийшов ACK
bool csma_send(const uint8_t *frame, size_t len) {
    uint32_t cw = CW_MIN;

    for (int attempt = 0; attempt < 7; attempt++) {
        wait_idle_for(DIFS_US);                 // 1. канал вільний DIFS?

        // 2. випадковий відступ у слотах із поточного діапазону
        int backoff = rand() % (cw + 1);
        while (backoff > 0) {
            if (channel_busy()) {               //   хтось зайняв ефір —
                wait_idle_for(DIFS_US);         //   заморозити лічильник,
                continue;                       //   доерахувати після тиші
            }
            delay_us(SLOT_US);
            backoff--;                          //   тихий слот — крок вниз
        }

        radio_transmit(frame, len);             // 3. лічильник 0 → передаємо
        if (wait_for_ack())                     // 4. дочекалися ACK?
            return true;                        //    доставлено

        cw = (cw * 2 + 1);                       // 5. зіткнення: подвоїти діапазон
        if (cw > CW_MAX) cw = CW_MAX;
    }
    return false;                               // здалися після кількох спроб
}
