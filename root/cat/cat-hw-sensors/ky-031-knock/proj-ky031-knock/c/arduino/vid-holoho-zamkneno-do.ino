const uint8_t KNOCK = 2;
const unsigned long LOCKOUT   = 60;    // придушення торохтіння, мс
const unsigned long GAP_END   = 800;   // тиша, що означає «серія скінчилась», мс
const uint8_t MAX_KNOCKS      = 12;    // стелю візерунка обмежуємо

volatile bool knockFlag = false;
void onKnock() { knockFlag = true; }

unsigned long lastKnock = 0;           // час останнього зарахованого стуку
unsigned long gaps[MAX_KNOCKS];        // проміжки між сусідніми стуками, мс
uint8_t nGaps  = 0;                    // скільки проміжків набралось
uint8_t nHits  = 0;                    // скільки стуків у поточній серії
bool inSeries  = false;                // чи йде набір серії

void setup() {
    pinMode(KNOCK, INPUT_PULLUP);
    Serial.begin(9600);
    attachInterrupt(digitalPinToInterrupt(KNOCK), onKnock, FALLING);
}

void loop() {
    unsigned long now = millis();

    // 1) зафіксувати новий стук (з локаутом проти торохтіння)
    if (knockFlag) {
        knockFlag = false;
        if (now - lastKnock > LOCKOUT) {
            if (inSeries && nGaps < MAX_KNOCKS) {
                gaps[nGaps++] = now - lastKnock;   // проміжок від попереднього стуку
            }
            lastKnock = now;
            nHits++;
            inSeries = true;
        }
    }

    // 2) достатньо довга тиша після стуку → серія скінчилась, розбираємо
    if (inSeries && now - lastKnock > GAP_END) {
        Serial.print("серія: ");
        Serial.print(nHits);
        Serial.print(" стук(и), проміжки[мс]:");
        for (uint8_t i = 0; i < nGaps; i++) {
            Serial.print(' ');
            Serial.print(gaps[i]);
        }
        Serial.println();
        // скидаємо стан під наступну серію
        nGaps = 0;
        nHits = 0;
        inSeries = false;
    }
}
