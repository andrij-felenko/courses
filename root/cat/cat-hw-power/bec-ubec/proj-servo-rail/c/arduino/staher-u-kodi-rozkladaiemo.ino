// ── Неблокувальний стагер: рознести пуски серв у часі. Arduino ──
// Замість delay() ведемо розклад і в loop() дивимось на millis().
// Керування лишається живим — радіо й монітор працюють між пусками.
#include <Servo.h>

const uint8_t N = 4;
const uint8_t PIN[N] = {3, 5, 6, 9};
Servo servo[N];

const uint16_t STAGGER_MS = 90;      // крок між пусками серв, мс
uint8_t  target[N];                  // куди кожне серво має піти, градуси
uint32_t dueAt[N];                   // момент (millis), коли дозволено рушити
bool     pending[N];                 // чи чекає це серво своєї черги

uint16_t angleToUs(uint8_t deg) {
  if (deg > 180) deg = 180;
  return 1000 + (uint32_t)1000 * deg / 180;
}

// Задати нову «розкладку» цілей: серва рушать по черзі, а не разом.
void scheduleMove(const uint8_t deg[N]) {
  uint32_t now = millis();
  for (uint8_t i = 0; i < N; i++) {
    target[i]  = deg[i];
    dueAt[i]   = now + (uint32_t)i * STAGGER_MS;  // i-те чекає i кроків
    pending[i] = true;
  }
}

void setup() {
  for (uint8_t i = 0; i < N; i++) {
    servo[i].attach(PIN[i]);
    servo[i].writeMicroseconds(1500);
    pending[i] = false;
  }
}

// Викликати ЧАСТО (щооберту loop): видає команди, коли настав їхній час.
void serviceStagger() {
  uint32_t now = millis();
  for (uint8_t i = 0; i < N; i++) {
    if (pending[i] && (int32_t)(now - dueAt[i]) >= 0) {
      servo[i].writeMicroseconds(angleToUs(target[i]));  // рушаємо ОДНЕ
      pending[i] = false;
    }
  }
}

void loop() {
  // приклад: раз на 3 с розкидати серва по нових кутах — по черзі
  static uint32_t last = 0;
  if (millis() - last > 3000) {
    uint8_t goal[N] = {30, 60, 120, 150};
    scheduleMove(goal);
    last = millis();
  }
  serviceStagger();     // піки рознесені; тут-таки читаємо радіо, міряємо шину…
}
