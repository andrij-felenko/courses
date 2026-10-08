#include <Wire.h>
#include <HardwareSerial.h>

// Визначення безпечних контактів для плати ESP32-S3 SuperMini/Zero
const int SDA_PIN = 2;
const int SCL_PIN = 1;

const int TX_PIN  = 43;
const int RX_PIN  = 44;

HardwareSerial CustomSerial(1);

void setup() {
  // Ініціалізація I2C на безпечних виводах (уникаючи GPIO0, GPIO45, GPIO46)
  Wire.begin(SDA_PIN, SCL_PIN, 400000);
  
  // Ініціалізація UART1 на призначених контактах
  CustomSerial.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN);
  
  CustomSerial.println(F("Периферію ініціалізовано без конфліктів зі страповими лініями"));
}

void loop() {
  // Основний цикл виконання коду
  delay(1000);
}
