// LOAD_PIN кермує MOSFET, що підмикає резистор-«гирю» до виходу.
// TRIG_PIN іде на зовнішній запуск осцилографа — фронт співпадає зі стрибком.
#define LOAD_PIN  5
#define TRIG_PIN  6

void load_step(void) {
    digitalWrite(TRIG_PIN, HIGH);   // спершу армуємо запуск осцилографа
    digitalWrite(LOAD_PIN, HIGH);   // тим самим тактом — різко даємо повне навантаження
    delayMicroseconds(500);         // тримаємо, поки контур відпрацює провал і дзвін
    digitalWrite(LOAD_PIN, LOW);    // знімаємо навантаження
    digitalWrite(TRIG_PIN, LOW);
}
