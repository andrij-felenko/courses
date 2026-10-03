// C++ (Arduino): Кінцевий автомат відновлення прозорого сеансу ESP-01
#include <Arduino.h>

enum GatewayState {
  STATE_INIT,
  STATE_SETUP_PASSTHROUGH,
  STATE_STREAMING,
  STATE_RECOVERY
};

GatewayState currentState = STATE_INIT;

bool sendATCommand(String cmd, String expected, unsigned long timeoutMs) {
  Serial1.println(cmd);
  unsigned long start = millis();
  String response = "";
  while (millis() - start < timeoutMs) {
    while (Serial1.available()) {
      char c = Serial1.read();
      response += c;
      if (response.indexOf(expected) != -1) return true;
    }
  }
  return false;
}

void exitPassthroughMode() {
  // Захисна пауза тиші 1050 мс перед ескейп-символами
  delay(1050);
  Serial1.print("+++");
  // Захисна пауза тиші 1050 мс після ескейп-символів
  delay(1050);
}

void processGatewayFSM() {
  switch (currentState) {
    case STATE_INIT:
      sendATCommand("AT", "OK", 1000);
      sendATCommand("AT+CIPMUX=0", "OK", 1000);
      sendATCommand("AT+CIPMODE=1", "OK", 1000);
      currentState = STATE_SETUP_PASSTHROUGH;
      break;

    case STATE_SETUP_PASSTHROUGH:
      if (sendATCommand("AT+CIPSTART=\"TCP\",\"192.168.1.100\",8080", "CONNECT", 5000)) {
        Serial1.println("AT+CIPSEND");
        delay(100);
        currentState = STATE_STREAMING;
      } else {
        currentState = STATE_RECOVERY;
      }
      break;

    case STATE_STREAMING:
      // В режимі стримінгу перевіряємо чи не надійшло сповіщення CLOSED
      if (Serial1.available()) {
        String rxData = Serial1.readString();
        if (rxData.indexOf("CLOSED") != -1 || rxData.indexOf("WIFI DISCONNECT") != -1) {
          currentState = STATE_RECOVERY;
        }
      }
      break;

    case STATE_RECOVERY:
      exitPassthroughMode();
      sendATCommand("AT+CIPCLOSE", "OK", 2000);
      delay(2000);
      currentState = STATE_INIT;
      break;
  }
}
