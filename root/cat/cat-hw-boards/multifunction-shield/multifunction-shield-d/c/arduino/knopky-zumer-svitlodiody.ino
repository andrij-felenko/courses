const byte S1  = A1;   // кнопка 1
const byte LED1 = 13;  // світлодіод 1 (активний низьким!)

void setup() {
  pinMode(S1, INPUT_PULLUP);   // у спокої HIGH, натиснута — LOW
  pinMode(LED1, OUTPUT);
  digitalWrite(LED1, HIGH);    // HIGH = згашено
}

void loop() {
  if (digitalRead(S1) == LOW)  // кнопку натиснуто
    digitalWrite(LED1, LOW);   // LOW = світиться
  else
    digitalWrite(LED1, HIGH);  // відпустив — гасне
}
