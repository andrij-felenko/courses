void setup() {
    Serial.begin(9600);           // швидкість; така сама має стояти в моніторі
    Serial.println("Плата стартувала");
}

void loop() {
    int sensor = analogRead(A0);
    Serial.print("Сенсор: ");
    Serial.print(sensor);
    Serial.print(" (");
    Serial.print(sensor * 5.0 / 1023.0, 2);
    Serial.println(" В)");
    delay(500);
}
