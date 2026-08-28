const uint8_t AO_PIN = A0;

int  warmS = 0;              // згладжене «тепло» (більше = тепліше)
int  prevWarm = 0;          // попереднє згладжене — для швидкості
unsigned long tPrev = 0;

void setup() {
    Serial.begin(9600);
    warmS = prevWarm = 1023 - analogRead(AO_PIN);
    tPrev = millis();
}

void loop() {
    int warm = 1023 - analogRead(AO_PIN);      // інверсія: більше = тепліше
    warmS += (warm - warmS) / 8;               // сильніше згладжування для тренду

    if (millis() - tPrev >= 500) {             // раз на пів секунди рахуємо швидкість
        int rate = warmS - prevWarm;           // зміна за інтервал (відносна!)
        const char* dir = rate > 2 ? "тепліє"
                        : rate < -2 ? "холоне"
                        : "стабільно";
        Serial.print("тренд: "); Serial.print(dir);
        Serial.print("   швидкість (відносна): "); Serial.println(rate);
        prevWarm = warmS;
        tPrev = millis();
    }
}
