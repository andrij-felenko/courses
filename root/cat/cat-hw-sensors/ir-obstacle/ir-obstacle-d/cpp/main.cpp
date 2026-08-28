const uint8_t PIN_OUT = 2;        // цифровий вихід давача (FC-51 OUT або KY-032 OUT)
const uint8_t PIN_LED = 13;       // вбудований світлодіод

void setup() {
  pinMode(PIN_OUT, INPUT_PULLUP); // підтяжка на випадок «плаваючої» лінії
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // LOW = перешкода є (активний нуль);  HIGH = вільно
  bool obstacle = (digitalRead(PIN_OUT) == LOW);
  digitalWrite(PIN_LED, obstacle ? HIGH : LOW);
  Serial.println(obstacle ? "ПЕРЕШКОДА" : "вільно");
  delay(30);
}
