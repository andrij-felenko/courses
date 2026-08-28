// STM32 (напр. Blue Pill / Nucleo): модуль на USART1 (типово PA9=TX, PA10=RX).
// Плата на 3.3 В → з'єднання з модулем напряму, без дільника.
HardwareSerial &bt = Serial1;   // псевдонім для читабельності

void setup() {
    Serial.begin(115200);       // монітор (USB або ST-Link VCP)
    bt.begin(9600);             // модуль на робочій швидкості
}

void loop() {
    while (bt.available())     Serial.write(bt.read());   // модуль → монітор
    while (Serial.available()) bt.write(Serial.read());   // монітор → модуль
}
