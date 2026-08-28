const uint8_t SOIL = A0;         // штир AO давача
const int DRY = 700;             // сухіше за це — вмикаємо полив
const int WET = 450;             // вологіше за це — вимикаємо
bool watering = false;           // поточний стан насоса

int readSoil() {                 // середнє з 8 замірів — глушимо шум
    long sum = 0;
    for (int i = 0; i < 8; i++) { sum += analogRead(SOIL); delay(2); }
    return sum / 8;
}

void setup() {
    Serial.begin(9600);
}

void loop() {
    int v = readSoil();          // більше = сухіше
    if (!watering && v > DRY) watering = true;   // пересохло → полив
    if ( watering && v < WET) watering = false;  // зволожилось → стоп

    Serial.print("вологість(АЦП)="); Serial.print(v);
    Serial.println(watering ? "  [полив]" : "  [сухо стоїть]");
    delay(1000);
}
