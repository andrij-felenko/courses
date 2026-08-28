const uint8_t PIN_DO  = 2;       // цифровий вихід KY-026
const uint8_t PIN_LED = 13;      // вбудований світлодіод

void setup() {
  pinMode(PIN_DO,  INPUT);       // поріг задано гвинтиком на платі
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // LOW = поріг перейдено = є вогонь;  HIGH = вогню немає (для інвертованого DO)
  bool flame = (digitalRead(PIN_DO) == LOW);
  digitalWrite(PIN_LED, flame ? HIGH : LOW);
  Serial.println(flame ? "ВОГОНЬ" : "спокійно");
  delay(50);
}
