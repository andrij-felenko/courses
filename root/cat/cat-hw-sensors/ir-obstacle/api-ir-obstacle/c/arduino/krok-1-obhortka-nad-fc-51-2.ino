IrObstacle front(2);        // OUT давача на D2, дебаунс 8 мс за замовчуванням

void setup() {
  Serial.begin(9600);
  front.begin();
}

void loop() {
  front.update();                     // опитати давач (неблокуюче)
  if (front.obstacle())
    Serial.println("ПЕРЕШКОДА");
  else
    Serial.println("вільно");
  // тут може бути будь-яка інша робота — update() не блокує
}
