const int BUZ = 4;
void setup() {
    ledcAttach(BUZ, 2000, 10);   // ніжка; стартова частота 2000 Гц; 10 біт
}
void loop() {
    ledcWriteTone(BUZ, 440);     // нота «ля» — 440 Гц
    delay(300);
    ledcWriteTone(BUZ, 880);     // на октаву вище
    delay(300);
    ledcWriteTone(BUZ, 0);       // 0 Гц = тиша
    delay(400);
}
