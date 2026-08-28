void handleCommand(const char* cmd) {
  int value;

  if      (strcmp(cmd, "LED ON")  == 0) digitalWrite(LED, HIGH);
  else if (strcmp(cmd, "LED OFF") == 0) digitalWrite(LED, LOW);
  else if (strcmp(cmd, "STOP")    == 0) setSpeed(0);
  else if (sscanf(cmd, "SPEED %d", &value) == 1) setSpeed(value);   // "SPEED 120" → value=120
  else    SerialBT.printf("? невідома команда: %s\n", cmd);          // відповідь у той самий потік

  SerialBT.println("OK");        // підтвердження — зворотний зв'язок користувачу
}
