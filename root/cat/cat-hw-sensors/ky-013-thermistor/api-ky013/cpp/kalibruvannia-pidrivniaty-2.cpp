// Дві калібрувальні пари (виміряне KY-013 → справжнє з еталона):
const float M1 =  1.5f, R1 =  0.0f;    // крижана вода: KY-013 дав 1.5, правда 0.0
const float M2 = 24.8f, R2 = 23.0f;    // кімната:      KY-013 дав 24.8, правда 23.0

float applyTwoPoint(float m) {
  // пряма r = a·m + b через дві точки (M1,R1) і (M2,R2)
  float a = (R2 - R1) / (M2 - M1);     // нахил
  float b = R1 - a * M1;               // зсув
  return a * m + b;
}

float readTempCalibrated2() {
  float m = resistanceToTempC(rawToResistance(readRawAveraged(16)));
  return applyTwoPoint(m);
}
