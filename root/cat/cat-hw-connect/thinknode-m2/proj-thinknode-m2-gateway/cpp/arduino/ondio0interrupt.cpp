#include <queue>

std::queue<String> packetQueue;
volatile bool packetReceived = false;

void IRAM_ATTR onDio0Interrupt() {
    packetReceived = true;
}

void loop() {
    // 1. Швидко забираємо дані з радіомодуля
    if (packetReceived) {
        packetReceived = false;
        String data = readLoRaBuffer();
        packetQueue.push(data);
    }

    // 2. Повільно відправляємо через Wi-Fi
    if (!packetQueue.empty() && WiFi.status() == WL_CONNECTED) {
        String dataToSend = packetQueue.front();
        sendToServer((uint8_t*)dataToSend.c_str(), dataToSend.length());
        packetQueue.pop(); 
    }
}
