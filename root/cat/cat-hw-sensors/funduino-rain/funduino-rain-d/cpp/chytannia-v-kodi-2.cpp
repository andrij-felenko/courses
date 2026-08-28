const uint8_t AO = A0;

void setup() {
    Serial.begin(9600);
}

void loop() {
    int v = analogRead(AO);        // 0..1023; менше = мокріше
    Serial.print("AO = ");
    Serial.print(v);

    if (v > 800)       Serial.println("  сухо");
    else if (v > 400)  Serial.println("  волого");
    else               Serial.println("  залито");

    delay(300);
}
