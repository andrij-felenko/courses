void releaseCoils() {
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  digitalWrite(10, LOW);
  digitalWrite(11, LOW);
}

void loop() {
  motor.step(STEPS_PER_REV);
  releaseCoils();                // погасили обмотки — мотор охолов, струм не тече
  delay(2000);
}
