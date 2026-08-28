Button btns[3] = { Button(2), Button(3), Button(4) };

void setup() {
  for (auto& b : btns) b.begin();   // кожна визначить свою полярність окремо
}

void loop() {
  for (auto& b : btns) b.update();  // кожній — свій update щопрохід
  if (btns[0].pressed()) { /* ... */ }
  if (btns[1].longPress()) { /* ... */ }
}
