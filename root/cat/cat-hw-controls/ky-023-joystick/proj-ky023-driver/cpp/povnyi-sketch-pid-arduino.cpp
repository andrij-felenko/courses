// ── KY-023 повний драйвер — Arduino Uno/Nano (10-бітний АЦП, 0..1023) ──
const int ADC_MAX = 1023;               // 10 біт

struct Axis {
    uint8_t pin; int center, lo, hi, deadzone; bool invert;
};
Axis vrx = { A0, 512, 0, ADC_MAX, 24, false };
Axis vry = { A1, 512, 0, ADC_MAX, 24, false };
Axis &horizontal = vrx;
Axis &vertical   = vry;

void calibrateCenter(Axis &a, uint8_t samples = 64) {
    long acc = 0;
    for (uint8_t i = 0; i < samples; i++) { acc += analogRead(a.pin); delay(3); }
    a.center = acc / samples;
}

int readAxis(const Axis &a) {
    int d = analogRead(a.pin) - a.center;
    if (d > -a.deadzone && d < a.deadzone) return 0;
    int out = (d > 0) ? map(d, a.deadzone, a.hi - a.center, 0,  100)
                      : map(d, -a.deadzone, a.lo - a.center, 0, -100);
    out = constrain(out, -100, 100);
    return a.invert ? -out : out;
}

// ── кнопка з неблокуючим гасінням ──
struct Button { uint8_t pin; bool stable, lastRead; uint32_t lastChange; bool ev; };
const uint32_t DEBOUNCE_MS = 25;
Button sw;

void buttonSetup(Button &b, uint8_t pin) {
    b.pin = pin; pinMode(pin, INPUT_PULLUP);
    b.stable = b.lastRead = true; b.lastChange = millis(); b.ev = false;
}
void buttonUpdate(Button &b) {
    b.ev = false;
    bool now = digitalRead(b.pin);
    if (now != b.lastRead) { b.lastChange = millis(); b.lastRead = now; }
    if (millis() - b.lastChange >= DEBOUNCE_MS && now != b.stable) {
        b.stable = now;
        if (b.stable == LOW) b.ev = true;
    }
}

long clicks = 0;

void setup() {
    Serial.begin(9600);
    calibrateCenter(vrx);               // ручку НЕ чіпати під час старту!
    calibrateCenter(vry);
    buttonSetup(sw, 2);
    Serial.print("Центр: X="); Serial.print(vrx.center);
    Serial.print(" Y=");       Serial.println(vry.center);
}

void loop() {
    buttonUpdate(sw);
    if (sw.ev) { clicks++; Serial.print("клік #"); Serial.println(clicks); }

    int vx = readAxis(horizontal);
    int vy = readAxis(vertical);

    // танкове змішування — приклад використання осей
    int left  = constrain(vy + vx, -100, 100);
    int right = constrain(vy - vx, -100, 100);

    Serial.print("X="); Serial.print(vx);
    Serial.print(" Y="); Serial.print(vy);
    Serial.print("  L="); Serial.print(left);
    Serial.print(" R=");  Serial.print(right);
    Serial.print(sw.stable == LOW ? "  [тримають]" : "");
    Serial.println();
    delay(30);                          // рівний темп циклу
}
