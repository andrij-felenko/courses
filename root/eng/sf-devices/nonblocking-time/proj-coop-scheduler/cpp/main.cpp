// задачі-функції визначені деінде у скетчі
void blink();
void readSensor();
void sendData();
void updateScreen();

typedef void (*TaskFn)();          // покажчик на функцію задачі

struct Task {
  TaskFn        run;               // що виконати
  unsigned long period;            // період, мс
  unsigned long last;              // мітка останнього запуску
};

Task tasks[] = {
  { blink,        500,   0 },
  { readSensor,   1000,  0 },
  { sendData,     10000, 0 },
  { updateScreen, 100,   0 },
};
const size_t TASK_COUNT = sizeof(tasks) / sizeof(tasks[0]);

void loop() {
  unsigned long now = millis();
  for (size_t i = 0; i < TASK_COUNT; i++) {
    if (now - tasks[i].last >= tasks[i].period) {
      tasks[i].run();                     // задача виконується до кінця
      tasks[i].last += tasks[i].period;   // рівна сітка, а не = now
    }
  }
}
