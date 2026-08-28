const float STUCK_RH   = 99.0;   // «залипла» вологість — підозра на конденсат
const int   STUCK_HITS = 5;      // скільки вимірів поспіль, щоб повірити в конденсат
int stuck = 0;                    // лічильник підряд залиплих вимірів

void dry_sensor() {
  Serial.println(F(".. вмикаю нагрівач: схоже на конденсат"));
  sensor.heater(true);            // увімкнути вбудований нагрівач
  delay(60000);                   // гріємо ~хвилину (блокуюче — для наочності)
  sensor.heater(false);           // вимкнути
  Serial.println(F(".. нагрівач вимкнено, даю давачу охолонути"));
  delay(30000);                   // охолонути перед новим виміром
  stuck = 0;
}

// у loop(), одразу після читання rh:
//   if (rh >= STUCK_RH) { if (++stuck >= STUCK_HITS) dry_sensor(); }
//   else stuck = 0;
