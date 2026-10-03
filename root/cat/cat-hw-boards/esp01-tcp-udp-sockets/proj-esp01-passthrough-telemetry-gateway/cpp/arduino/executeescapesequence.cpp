// C++ (Arduino): Кінцевий автомат відновлення прозорого шлюзу телеметрії
#include <Arduino.h>

enum FsmState {
  STATE_STREAMING,
  STATE_HANDLE_FAULT,
  STATE_RECONNECT
};

FsmState currentFsmState = STATE_STREAMING;
unsigned long lastHeartbeat = 0;
const unsigned long HEARTBEAT_TIMEOUT_MS = 5000;

void executeEscapeSequence() {
  // Витримуємо 1050 мс тиші перед передачею
  delay(1050);
  Serial1.print("+++");
  // Витримуємо 1050 мс тиші після передачі
  delay(1050);
}

bool sendCommandCheckOK(const String& cmd, unsigned long timeoutMs) {
  Serial1.println(cmd);
  unsigned long start = millis();
  String resp = "";
  while (millis() - start < timeoutMs) {
    while (Serial1.available()) {
      char c = Serial1.read();
      resp += c;
      if (resp.indexOf("OK") != -1) return true;
    }
  }
  return false;
}

void updateGatewayFSM() {
  switch (currentFsmState) {
    case STATE_STREAMING:
      if (Serial1.available()) {
        String data = Serial1.readString();
        if (data.indexOf("CLOSED") != -1 || data.indexOf("WIFI DISCONNECT") != -1) {
          currentFsmState = STATE_HANDLE_FAULT;
        }
      }
      if (millis() - lastHeartbeat > HEARTBEAT_TIMEOUT_MS) {
        // Таймаут відсутності відповіді від сервера
        currentFsmState = STATE_HANDLE_FAULT;
      }
      break;

    case STATE_HANDLE_FAULT:
      executeEscapeSequence();
      sendCommandCheckOK("AT+CIPCLOSE", 1000);
      currentFsmState = STATE_RECONNECT;
      break;

    case STATE_RECONNECT:
      sendCommandCheckOK("AT+CIPMUX=0", 1000);
      sendCommandCheckOK("AT+CIPMODE=1", 1000);
      if (sendCommandCheckOK("AT+CIPSTART=\"TCP\",\"192.168.1.100\",8080", 5000)) {
        Serial1.println("AT+CIPSEND");
        delay(100);
        lastHeartbeat = millis();
        currentFsmState = STATE_STREAMING;
      } else {
        // При невдачі перепідключення чекаємо перед наступною спробою
        delay(3000);
      }
      break;
  }
}
