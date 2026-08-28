const uint8_t MIC = A0;
const unsigned long WINDOW = 50;

float measureRMS() {
    // --- прохід 1: середнє (робоча точка) за вікно ---
    unsigned long t0 = millis();
    long sum = 0;
    int  n = 0;
    while (millis() - t0 < WINDOW) {
        sum += analogRead(MIC);
        n++;
    }
    float mean = (float)sum / n;

    // --- прохід 2: сума квадратів відхилень від середнього ---
    t0 = millis();
    float sumSq = 0;
    int  n2 = 0;
    while (millis() - t0 < WINDOW) {
        float d = analogRead(MIC) - mean;
        sumSq += d * d;
        n2++;
    }
    return sqrt(sumSq / n2);          // RMS-відхилення в одиницях АЦП
}

void setup() { Serial.begin(9600); }

void loop() {
    Serial.println(measureRMS(), 1);  // одна цифра після коми
}
