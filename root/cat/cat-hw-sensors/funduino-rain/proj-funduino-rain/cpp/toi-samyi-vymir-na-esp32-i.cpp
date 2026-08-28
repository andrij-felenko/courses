const uint8_t AO = 34;              // ADC1! GPIO34 безпечний при Wi-Fi
const int DRY_ENTER_MV = 2400;      // пороги — тепер у мілівольтах
const int WET_ENTER_MV = 1500;

bool raining = false;

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);       // 0..4095, якщо читати сирий analogRead
}

void loop() {
    int mv = analogReadMilliVolts(AO);   // відкалібровані мілівольти

    if (!raining && mv < WET_ENTER_MV) raining = true;
    if ( raining && mv > DRY_ENTER_MV) raining = false;

    Serial.print("AO = "); Serial.print(mv); Serial.print(" мВ");
    Serial.println(raining ? "  → дощ" : "  → сухо");
    delay(200);
}
