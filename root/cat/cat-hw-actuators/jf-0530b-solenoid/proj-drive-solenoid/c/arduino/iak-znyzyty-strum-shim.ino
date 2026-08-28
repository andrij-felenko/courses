const uint8_t  SOL_PIN    = 5;     // МУСИТЬ бути ШІМ-здатна ніжка!
const uint16_t PEAK_MS    = 60;    // повний струм: тривалість кидка на втягування
const uint8_t  HOLD_DUTY  = 90;    // утримання: шпаруватість 0..255 (~35% повного струму)

enum SolState { SOL_IDLE, SOL_PEAK, SOL_HOLD };
SolState solState = SOL_IDLE;
uint32_t solStart = 0;

void solenoidEngage() {            // почати «втягнути й тримати»
    digitalWrite(SOL_PIN, HIGH);   // ФАЗА 1: повний струм — рвемо осердя через щілину
    solState = SOL_PEAK;
    solStart = millis();
}

void solenoidRelease() {           // відпустити зовсім
    analogWrite(SOL_PIN, 0);       // знімаємо ШІМ
    digitalWrite(SOL_PIN, LOW);    // і чисто гасимо ніжку
    solState = SOL_IDLE;
}

void solenoidUpdate() {
    if (solState == SOL_PEAK && (millis() - solStart >= PEAK_MS)) {
        analogWrite(SOL_PIN, HOLD_DUTY);  // ФАЗА 2: осердя вже втягнуте — переходимо на знижений струм
        solState = SOL_HOLD;              // тепер тримаємо холодно, скільки треба
    }
}
