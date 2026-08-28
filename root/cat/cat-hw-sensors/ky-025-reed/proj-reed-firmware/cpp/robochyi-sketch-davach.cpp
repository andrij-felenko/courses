const uint8_t REED   = 2;        // D0 давача
const uint8_t LED    = 13;       // «двері відчинені» — індикатор
const int     ACTIVE = LOW;      // рівень, коли магніт поруч = двері ЗАЧИНЕНІ

const uint32_t DEBOUNCE_MS = 30;

bool     closed   = true;        // поточний стан: true = зачинено
bool     was_closed = true;
uint32_t opens    = 0;           // скільки разів відчиняли
uint32_t t_edge   = 0;

void setup() {
    pinMode(REED, INPUT);
    pinMode(LED, OUTPUT);
    Serial.begin(9600);

    closed = (digitalRead(REED) == ACTIVE);   // початковий стан — як є при старті
    was_closed = closed;
    digitalWrite(LED, closed ? LOW : HIGH);
    Serial.println(closed ? "старт: двері зачинені" : "старт: двері ВІДЧИНЕНІ");
}

void loop() {
    bool now_closed = (digitalRead(REED) == ACTIVE);
    uint32_t now = millis();

    if (now_closed != was_closed && (now - t_edge) >= DEBOUNCE_MS) {
        t_edge = now;
        was_closed = now_closed;
        closed = now_closed;

        if (!closed) {                 // край «зачинено → відчинено» — це відкривання
            opens++;
            digitalWrite(LED, HIGH);
            Serial.print("ВІДЧИНИЛИ (разів: ");
            Serial.print(opens);
            Serial.println(")");
        } else {                       // край «відчинено → зачинено»
            digitalWrite(LED, LOW);
            Serial.println("зачинили");
        }
    }
}
