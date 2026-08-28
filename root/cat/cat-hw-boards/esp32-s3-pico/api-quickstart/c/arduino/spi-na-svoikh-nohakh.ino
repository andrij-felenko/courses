#include <SPI.h>

static const int PIN_SCK = 12, PIN_MISO = 13, PIN_MOSI = 11, PIN_CS = 10;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_CS, OUTPUT);
  digitalWrite(PIN_CS, HIGH);          // CS у спокої — високий
  SPI.begin(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS);
}

// один обмін байтом з веденим пристроєм
uint8_t spiExchange(uint8_t out) {
  SPI.beginTransaction(SPISettings(10000000, MSBFIRST, SPI_MODE0)); // 10 МГц
  digitalWrite(PIN_CS, LOW);           // вибрали пристрій
  uint8_t in = SPI.transfer(out);      // одночасно шлемо out і читаємо in
  digitalWrite(PIN_CS, HIGH);          // відпустили
  SPI.endTransaction();
  return in;
}

void loop() {}
