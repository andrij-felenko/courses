const uint8_t PIN_AO   = A0;
const int      THRESH  = 300;    // поріг у сирих одиницях — підбери під свою сцену

void setup() {
  Serial.begin(9600);
}

void loop() {
  int ir = analogRead(PIN_AO);   // 0..1023: більше ІЧ (ближче/сильніше вогонь) — інше число
  Serial.println(ir);            // дивись у монітор порту, підбери THRESH під свій вогонь
  if (ir > THRESH) {
    // тут — «жару достатньо»: у робота це «повертай на найяскравіше й гаси»
  }
  delay(50);
}
