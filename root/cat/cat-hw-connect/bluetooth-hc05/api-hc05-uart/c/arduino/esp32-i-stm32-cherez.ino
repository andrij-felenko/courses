// ESP32: Serial → монітор по USB, Serial2 → модуль.
// Serial2 типово на GPIO16 (RX2) і GPIO17 (TX2).
//   GPIO16 ← TXD модуля (напряму, обидва 3.3 В)
//   GPIO17 → RXD модуля (напряму, TX уже 3.3 В — дільник НЕ потрібен)
void setup() {
    Serial.begin(115200);                          // монітор
    Serial2.begin(9600, SERIAL_8N1, 16, 17);       // модуль: 9600, 8 біт, без парності, 1 стоп
    //           швидкість  формат      RX  TX
    Serial.println("ESP32 ↔ HC-05 через апаратний UART2");
}

void loop() {
    while (Serial2.available()) Serial.write(Serial2.read());  // модуль → монітор
    while (Serial.available())  Serial2.write(Serial.read());  // монітор → модуль
}
