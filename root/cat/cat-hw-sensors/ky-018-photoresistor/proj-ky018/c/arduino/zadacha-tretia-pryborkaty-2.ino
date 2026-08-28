const uint8_t PIN_LDR = A0;
const uint8_t N = 16;               // розмір вікна (степінь двійки — зручно для ділення)

int   buf[N];                       // кільцевий буфер відліків
uint8_t idx = 0;                    // куди писати наступний
long  sum = 0;                      // поточна сума вмісту буфера
bool  filled = false;               // чи буфер уже повний

void setup() {
  Serial.begin(9600);
  for (uint8_t i = 0; i < N; i++) buf[i] = 0;
}

int movingAverage(int raw) {
  sum -= buf[idx];                  // викинути найдавніший відлік із суми
  buf[idx] = raw;                   // покласти новий на його місце
  sum += raw;                       // додати новий у суму
  idx = (idx + 1) % N;              // зсунути вказівник по колу
  if (idx == 0) filled = true;
  uint8_t count = filled ? N : idx; // поки не заповнилось — ділимо на реальну кількість
  return count ? (int)(sum / count) : raw;
}

void loop() {
  int raw = analogRead(PIN_LDR);
  Serial.println(movingAverage(raw));
  delay(20);
}
