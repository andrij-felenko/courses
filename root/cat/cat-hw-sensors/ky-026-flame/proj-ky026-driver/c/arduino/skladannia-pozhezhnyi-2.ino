const float SEE_FIRE  = 200;   // сума жару, з якої робот починає їхати на вогонь
const float BURN_NEAR = 700;   // сума, з якої вважаємо, що впритул → гасити
const int   BASE_SPD  = 140;   // базова швидкість руху вперед
const float TURN_GAIN = 0.6f;  // наскільки різко кермувати за різницею

void setup() {
  pinMode(FAN, OUTPUT);
  pinMode(L_DIR, OUTPUT); pinMode(L_PWM, OUTPUT);
  pinMode(R_DIR, OUTPUT); pinMode(R_PWM, OUTPUT);
  digitalWrite(FAN, LOW);
  irL = analogRead(AO_L);               // старт середніх — з поточних значень
  irR = analogRead(AO_R);
}

void loop() {
  readSensors();
  float sum  = irL + irR;               // загальна близькість вогню
  float diff = irL - irR;               // >0 → жар зліва, <0 → справа

  if (sum < SEE_FIRE) {
    // Вогню не видно — стій (або тут можна крутитися й шукати).
    digitalWrite(FAN, LOW);
    drive(0, 0);
  }
  else if (sum >= BURN_NEAR) {
    // Впритул до полумʼя — стоп і дми, доки жар не впаде.
    drive(0, 0);
    digitalWrite(FAN, HIGH);
  }
  else {
    // Бачимо вогонь — їдемо на нього, підрулюючи за різницею.
    digitalWrite(FAN, LOW);
    int turn  = (int)(TURN_GAIN * diff);        // кермо пропорційно різниці
    int left  = BASE_SPD - turn;                // сильніше зліва → пригальмуй лівий
    int right = BASE_SPD + turn;                // → робот доверне ліворуч, на жар
    drive(left, right);
  }
  delay(20);                            // ~50 разів на секунду — досить для керма
}
