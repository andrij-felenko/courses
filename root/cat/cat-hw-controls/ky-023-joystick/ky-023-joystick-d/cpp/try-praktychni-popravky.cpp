const uint8_t PIN_VRX = A0;
const int DEADZONE = 24;          // напівширина мертвої зони, одиниць АЦП
int centerX = 512;                // уточнимо у setup()

void setup() {
    long acc = 0;
    for (int i = 0; i < 32; i++) { acc += analogRead(PIN_VRX); delay(4); }
    centerX = acc / 32;           // справжній центр саме цього екземпляра
    Serial.begin(9600);
}

int axis(int raw, int center) {
    int d = raw - center;                     // відхилення від центру
    if (d > -DEADZONE && d < DEADZONE) return 0;  // у мертвій зоні — нуль
    // масштабуємо решту ходу (center..крайнє) у зручні −100..+100
    if (d > 0) return map(d,  DEADZONE,  1023 - center, 0,  100);
    else       return map(d, -DEADZONE,       -center,  0, -100);
}

void loop() {
    int vx = axis(analogRead(PIN_VRX), centerX);   // −100..+100, 0 у спокої
    Serial.println(vx);
    delay(50);
}
