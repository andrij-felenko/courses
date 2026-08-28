// у кожного веденого — своя ніжка CS і свої параметри
const int CS_DISP = 10, CS_ADC = 9, CS_FLASH = 8;
SPISettings disp (20000000, MSBFIRST, SPI_MODE0);   // дисплей: швидко
SPISettings adc  ( 1000000, MSBFIRST, SPI_MODE3);   // АЦП: повільніше

void setup() {
  pinMode(CS_DISP, OUTPUT);  digitalWrite(CS_DISP, HIGH);  // усі CS —
  pinMode(CS_ADC,  OUTPUT);  digitalWrite(CS_ADC,  HIGH);  // високі ще
  pinMode(CS_FLASH,OUTPUT);  digitalWrite(CS_FLASH,HIGH);  // до обміну
  SPI.begin();
}

uint16_t readAdc() {
  SPI.beginTransaction(adc);          // режим і швидкість саме АЦП
  digitalWrite(CS_ADC, LOW);          // обрали його: активний нуль
  uint16_t v = SPI.transfer16(0x0000);// обмін (пише й читає водночас)
  digitalWrite(CS_ADC, HIGH);         // відпустили — підняли одразу
  SPI.endTransaction();
  return v;
}
