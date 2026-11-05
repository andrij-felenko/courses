#include <Arduino.h>
#include <FS.h>
#include <SD.h>

struct TelemetryPacket {
    uint32_t timestamp_ms;
    float accel_x;
    float accel_y;
    float accel_z;
};

File logFile;

void setup() {
    Serial.begin(115200);
    if (!SD.begin()) {
        Serial.println("Помилка ініціалізації SD-карти!");
        return;
    }
    
    logFile = SD.open("/telemetry.bin", FILE_WRITE);
}

void loop() {
    if (!logFile) return;

    TelemetryPacket pkt;
    pkt.timestamp_ms = millis();
    pkt.accel_x = 1.0f;
    pkt.accel_y = 0.0f;
    pkt.accel_z = 9.81f;

    uint32_t t_start = micros();
    
    // Прямий запис у файл із динамічним виділенням кластерів
    logFile.write(reinterpret_cast<const uint8_t*>(&pkt), sizeof(pkt));
    
    uint32_t duration_us = micros() - t_start;

    if (duration_us > 50000) {
        Serial.print("Виявлено хвостову затримку: ");
        Serial.print(duration_us);
        Serial.println(" мкс");
    }

    delay(10);
}
