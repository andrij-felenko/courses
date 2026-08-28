const float VREF   = 3.3f;    // опора АЦП = живлення давача (ратіометрично)
const float BIAS   = 1.65f;   // 0g при 3.3 В ≈ половина живлення
const float SENS   = 0.330f;  // чутливість при 3.3 В ≈ 330 мВ/g

float readAxisG(int pin) {
    int   raw = analogRead(pin);          // 0..1023 (10 біт)
    float u   = raw * VREF / 1023.0f;     // код → вольти
    return (u - BIAS) / SENS;             // вольти → g
}

void setup() {
    Serial.begin(115200);
}

void loop() {
    float ax = readAxisG(A0);
    float ay = readAxisG(A1);
    float az = readAxisG(A2);
    Serial.print(ax); Serial.print('\t');
    Serial.print(ay); Serial.print('\t');
    Serial.println(az);
    delay(50);
}
