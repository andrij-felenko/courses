#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include "telemetry_packet.h"

// Параметри бездротової Wi-Fi мережі
const char* WIFI_SSID = "TelemetryNet";
const char* WIFI_PASS = "SecretPassword123";

// Мережеві налаштування UDP-маяка
const IPAddress BROADCAST_IP(192, 168, 1, 255);
const uint16_t BEACON_PORT = 8888;
const uint32_t BEACON_INTERVAL_MS = 2000;

// Клас для керування періодичним неблокуючим UDP-маяком
class UdpBeacon {
public:
    UdpBeacon(WiFiUDP& udp, IPAddress target_ip, uint16_t port, uint32_t interval_ms)
        : udp_(udp), target_ip_(target_ip), port_(port), interval_ms_(interval_ms),
          last_send_ms_(0), sequence_counter_(0) {}

    // Ініціалізація сокета та слухання портів
    bool begin() {
        return udp_.begin(port_) != 0;
    }

    // Періодичне оновлення стану маяка (неблокуючий виклик для loop)
    void update() {
        uint32_t now = millis();
        if (now - last_send_ms_ >= interval_ms_) {
            last_send_ms_ = now;
            sendTelemetryBeacon();
        }

        receiveIncomingData();
    }

private:
    // Формування та відправка бінарної датаграми телеметрії
    void sendTelemetryBeacon() {
        TelemetryPacket packet{};
        packet.sequence = ++sequence_counter_;
        packet.uptime_ms = millis();
        
        // Симуляція даних із датчиків (22.5°C та 55.0% вологості)
        packet.temperature = 2250;
        packet.humidity = 5500;
        
        packet.finalize();

        udp_.beginPacket(target_ip_, port_);
        udp_.write(reinterpret_cast<const uint8_t*>(&packet), sizeof(packet));
        if (udp_.endPacket()) {
            Serial.printf("[UDP] Відправлено пакет #%u (CRC: 0x%04X, Uptime: %u ms)\n",
                          packet.sequence, packet.crc16, packet.uptime_ms);
        } else {
            Serial.println("[UDP] Помилка відправки широкомовного пакета!");
        }
    }

    // Обробка вхідних пакетиків-відповідей без блокування циклу
    void receiveIncomingData() {
        int packet_size = udp_.parsePacket();
        if (packet_size <= 0) {
            return;
        }

        uint8_t buffer[64];
        int len = udp_.read(buffer, sizeof(buffer));
        if (len <= 0) {
            return;
        }

        Serial.printf("[UDP] Отримано %d байтів від %s:%d\n",
                      len, udp_.remoteIP().toString().c_str(), udp_.remotePort());

        if (static_cast<size_t>(len) == sizeof(TelemetryPacket)) {
            const auto* rx_packet = reinterpret_cast<const TelemetryPacket*>(buffer);
            if (rx_packet->isValid()) {
                Serial.printf("    -> Валідний кадр #%u | Темп: %.2f°C | Волог: %.2f%%\n",
                              rx_packet->sequence, rx_packet->temperature / 100.0f, rx_packet->humidity / 100.0f);
            } else {
                Serial.println("    -> Помилка: Невірний CRC16 кадру!");
            }
        }
    }

    WiFiUDP& udp_;
    IPAddress target_ip_;
    uint16_t port_;
    uint32_t interval_ms_;
    uint32_t last_send_ms_;
    uint32_t sequence_counter_;
};

// Глобальні екземпляри сокета та маяка
WiFiUDP udp_socket;
UdpBeacon beacon(udp_socket, BROADCAST_IP, BEACON_PORT, BEACON_INTERVAL_MS);

void setup() {
    Serial.begin(115200);
    delay(100);
    Serial.println("\n--- Запуск неблокуючого UDP-маяка на ESP-01 ---");

    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    Serial.print("Підключення до Wi-Fi ");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.printf("\nWi-Fi підключено! IP адреса: %s\n", WiFi.localIP().toString().c_str());

    if (beacon.begin()) {
        Serial.printf("UDP сокет успішно відкрито на порту %u\n", BEACON_PORT);
    } else {
        Serial.println("Помилка ініціалізації UDP сокета!");
    }
}

void loop() {
    // Неблокуюче обслуговування відправки та прийому датаграм
    beacon.update();
}
