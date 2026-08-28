const uint8_t PIN_PIR = 2;
const uint8_t PIN_LED = 13;

const uint32_t WARMUP_MS = 60000UL;   // прогрів
const uint32_t LOCKOUT_MS = 3000UL;   // не приймати нову подію раніше, ніж мине стільки

uint32_t t_boot;
uint32_t t_last_event;   // коли зафіксували останню подію
int      pir_prev;       // попередній рівень OUT (для виявлення фронту)
uint32_t counter;        // скільки подій нарахували

void alarm_event() {
    counter++;
    Serial.print("ТРИВОГА, подія #");
    Serial.println(counter);
    // тут: надіслати пакет, зробити кадр, увімкнути сирену на мить тощо
    digitalWrite(PIN_LED, HIGH);
    delay(100);                 // коротке блимання — для наочності
    digitalWrite(PIN_LED, LOW);
}

void setup() {
    pinMode(PIN_PIR, INPUT);
    pinMode(PIN_LED, OUTPUT);
    Serial.begin(9600);

    t_boot   = millis();
    pir_prev = digitalRead(PIN_PIR);
    t_last_event = 0;
    counter  = 0;
}

void loop() {
    uint32_t now = millis();

    if (now - t_boot < WARMUP_MS) return;   // гасіння прогріву

    int pir = digitalRead(PIN_PIR);

    // Виявлення переднього фронту: було 0, стало 1 — це нова поява руху.
    if (pir == HIGH && pir_prev == LOW) {
        if (now - t_last_event >= LOCKOUT_MS) {   // не частіше, ніж LOCKOUT_MS
            t_last_event = now;
            alarm_event();
        }
    }
    pir_prev = pir;

    delay(20);   // грубий дебаунс краю: досить, щоб не ловити брязкіт
}
