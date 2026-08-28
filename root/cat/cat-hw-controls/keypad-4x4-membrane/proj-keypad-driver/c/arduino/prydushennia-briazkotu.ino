// антидеренч однієї клавіші на «таймері краю»:
const uint16_t DEBOUNCE_MS = 20;
bool     lastRaw   = false;   // сирий стан минулого разу
bool     stable    = false;   // стан, якому вже віримо
uint32_t tEdge     = 0;       // коли рівень востаннє смикнувся
bool     reported  = false;   // чи вже повідомили про це натискання

// raw — сирий результат сканування цієї клавіші (true = замкнено)
void debounceKey(bool raw) {
    uint32_t now = millis();
    if (raw != lastRaw) {          // рівень щойно змінився — перезапустити відлік
        tEdge = now;
        lastRaw = raw;
    }
    if (now - tEdge >= DEBOUNCE_MS) {   // протримався досить довго — вірити
        stable = raw;
    }
    if (stable && !reported) {          // стійке замикання, ще не повідомляли
        Serial.println("натиск (свій антидеренч)");
        reported = true;                // одна подія на натискання
    }
    if (!stable) reported = false;      // клавіша відпустилась — готові до нового
}
