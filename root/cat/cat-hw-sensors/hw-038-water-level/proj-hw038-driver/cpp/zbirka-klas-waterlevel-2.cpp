// таблиця — під СВОЮ воду; ці числа лише приклад
const CalPoint TABLE[] = {
  {30, 0}, {210, 25}, {430, 50}, {660, 75}, {840, 100}
};

WaterLevel sensor(7, A0, 8,        // живлення D7, сигнал A0, помпа D8
                  TABLE, 5,        // таблиця з 5 точок
                  80, 60);         // помпа: ON вище 80 %, OFF нижче 60 %

void setup() {
  Serial.begin(9600);
  sensor.begin();
}

void loop() {
  int level = sensor.update();     // зміряв, переклав, оновив помпу
  Serial.print("рівень "); Serial.print(level); Serial.print(" %  ");
  Serial.println(sensor.isPumpOn() ? "ПОМПА ON" : "помпа off");
  delay(2000);                     // раз на 2 с — гребінку між вимірами не живимо
}
