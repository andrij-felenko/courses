const uint8_t AO_PIN = A0;
const uint8_t LOAD   = 13;

// Пороги в одиницях (1023 - analogRead): БІЛЬШЕ = тепліше.
// Верхній > нижній; зазор між ними — і є гістерезис.
// Підібрати під свою намистину, дивлячись на друк `warm` нижче.
const int WARM_ON  = 640;    // вище цього — вмикаємо («гаряче»)
const int WARM_OFF = 600;    // нижче цього — вимикаємо (мертва зона: 600..640)

bool state = false;          // true = навантаження ввімкнене
int  warmS = 0;              // згладжене значення (проти дрібного шуму АЦП)

void setup() {
    pinMode(LOAD, OUTPUT);
    Serial.begin(9600);
    warmS = 1023 - analogRead(AO_PIN);        // початкове наповнення фільтра
}

void loop() {
    int warm = 1023 - analogRead(AO_PIN);     // інвертуємо: більше = тепліше
    warmS += (warm - warmS) / 4;              // проста згладжувальна ланка (шум АЦП)

    // Гістерезис ЗА РІВНЕМ: два різні пороги вгору й униз.
    if (!state && warmS >= WARM_ON) {         // піднявся вище верхнього → вмикаємо
        state = true;
        digitalWrite(LOAD, HIGH);
        Serial.println(">> ГАРЯЧЕ (warm вище верхнього порогу)");
    } else if (state && warmS <= WARM_OFF) {  // впав нижче нижнього → вимикаємо
        state = false;
        digitalWrite(LOAD, LOW);
        Serial.println("<< норма (warm нижче нижнього порогу)");
    }
    // у зоні WARM_OFF..WARM_ON стан НЕ міняється — тремтіння погашене

    Serial.print("warm = "); Serial.println(warmS);   // для підбору порогів
    delay(50);
}
