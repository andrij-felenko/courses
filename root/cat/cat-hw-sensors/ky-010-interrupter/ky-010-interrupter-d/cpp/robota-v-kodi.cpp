const int PIN_S = 2;   // сигнал KY-010 на цифровому вході D2

void setup() {
  pinMode(PIN_S, INPUT);
  Serial.begin(9600);
  Serial.println("Заводь щілину то вільною, то перекритою — дивись на рівень:");
}

void loop() {
  int level = digitalRead(PIN_S);
  Serial.println(level ? "HIGH" : "LOW");
  delay(200);
}
