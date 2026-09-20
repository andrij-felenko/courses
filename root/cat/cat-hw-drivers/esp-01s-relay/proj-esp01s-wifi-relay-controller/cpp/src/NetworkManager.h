#ifndef NETWORK_MANAGER_H
#define NETWORK_MANAGER_H

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <PubSubClient.h>
#include "RelayController.h"

/**
 * @brief Клас для керування Wi-Fi підключенням, HTTP-вебсервером та MQTT-клієнтом.
 */
class NetworkManager {
public:
    /**
     * @brief Конструктор мережевого менеджера.
     * @param relay Посилання на контролер реле.
     * @param web_port Порт локального HTTP-сервера.
     */
    explicit NetworkManager(RelayController& relay, uint16_t web_port = 80)
        : relay_(relay),
          server_(web_port),
          wifi_client_(),
          mqtt_client_(wifi_client_),
          mqtt_port_(1883),
          last_mqtt_reconnect_attempt_(0) {}

    /**
     * @brief Запуск мережевих служб.
     * @param ssid Назва мережі Wi-Fi.
     * @param password Пароль Wi-Fi.
     * @param mqtt_server Адреса MQTT-брокера.
     * @param mqtt_port Порт MQTT.
     * @param mqtt_user Логін MQTT.
     * @param mqtt_pass Пароль MQTT.
     */
    void begin(const char* ssid, const char* password,
               const char* mqtt_server = "", uint16_t mqtt_port = 1883,
               const char* mqtt_user = "", const char* mqtt_pass = "") {
        ssid_ = ssid;
        password_ = password;
        mqtt_server_ = mqtt_server;
        mqtt_port_ = mqtt_port;
        mqtt_user_ = mqtt_user;
        mqtt_pass_ = mqtt_pass;

        setupWiFi();
        setupHttpServer();
        setupMqtt();
    }

    /**
     * @brief Неблокуюча обробка мережевих подій у головному циклі program loop().
     */
    void loop() {
        // Перевірка стану Wi-Fi підключення
        if (WiFi.status() != WL_CONNECTED) {
            reconnectWiFi();
        }

        // Обслуговування запитів HTTP вебсервера
        server_.handleClient();

        // Обслуговування MQTT з'єднання
        if (mqtt_server_.length() > 0) {
            if (!mqtt_client_.connected()) {
                unsigned long now = millis();
                if (now - last_mqtt_reconnect_attempt_ > 5000) {
                    last_mqtt_reconnect_attempt_ = now;
                    reconnectMqtt();
                }
            } else {
                mqtt_client_.loop();
            }
        }
    }

    /**
     * @brief Публікація стану реле у MQTT топік.
     */
    void publishRelayState() {
        if (!mqtt_client_.connected()) {
            return;
        }

        const char* payload = relay_.getState() ? "ON" : "OFF";
        mqtt_client_.publish(mqtt_state_topic_.c_str(), payload, true);
    }

private:
    RelayController& relay_;
    ESP8266WebServer server_;
    WiFiClient wifi_client_;
    PubSubClient mqtt_client_;

    String ssid_;
    String password_;
    String mqtt_server_;
    uint16_t mqtt_port_;
    String mqtt_user_;
    String mqtt_pass_;

    String mqtt_client_id_ = "ESP01S-Relay-" + String(ESP.getChipId(), HEX);
    String mqtt_command_topic_ = "esp01s/relay/cmd";
    String mqtt_state_topic_ = "esp01s/relay/state";

    unsigned long last_mqtt_reconnect_attempt_;

    /**
     * @brief Первинна ініціалізація Wi-Fi з'єднання.
     */
    void setupWiFi() {
        WiFi.mode(WIFI_STA);
        WiFi.begin(ssid_.c_str(), password_.c_str());

        Serial.print(F("Підключення до Wi-Fi мережі: "));
        Serial.println(ssid_);

        uint8_t attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 30) {
            delay(500);
            Serial.print(F("."));
            attempts++;
        }

        if (WiFi.status() == WL_CONNECTED) {
            Serial.println();
            Serial.print(F("Wi-Fi підключено! IP-адреса: "));
            Serial.println(WiFi.localIP());
        } else {
            Serial.println();
            Serial.println(F("Не вдалося підключитися до Wi-Fi. Спроби тривають у фоновому режимі."));
        }
    }

    /**
     * @brief Перепідключення Wi-Fi у разі втрати зв'язку.
     */
    void reconnectWiFi() {
        static unsigned long last_wifi_check = 0;
        unsigned long now = millis();
        if (now - last_wifi_check > 10000) {
            last_wifi_check = now;
            if (WiFi.status() != WL_CONNECTED) {
                Serial.println(F("Втрачено Wi-Fi з'єднання. Повторна спроба підключення..."));
                WiFi.reconnect();
            }
        }
    }

    /**
     * @brief Налаштування маршрутів локального HTTP-сервера.
     */
    void setupHttpServer() {
        // Головна веб-сторінка
        server_.on("/", HTTP_GET, [this]() {
            String html = F("<!DOCTYPE html><html><head><meta charset='utf-8'>"
                            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
                            "<title>ESP-01S Relay</title>"
                            "<style>body{font-family:Arial,sans-serif;text-align:center;margin-top:40px;}"
                            ".btn{display:inline-block;padding:12px 24px;font-size:16px;color:#fff;border:none;"
                            "border-radius:4px;cursor:pointer;text-decoration:none;margin:8px;}"
                            ".on{background-color:#4CAF50;}.off{background-color:#f44336;}"
                            ".toggle{background-color:#008CBA;}</style></head><body>"
                            "<h2>Модуль реле ESP-01S</h2>"
                            "<p>Поточний стан: <strong>");
            html += relay_.getState() ? F("УВІМКНЕНО") : F("ВИМКНЕНО");
            html += F("</strong></p><p>"
                      "<a href='/on' class='btn on'>Увімкнути</a>"
                      "<a href='/off' class='btn off'>Вимкнути</a>"
                      "<a href='/toggle' class='btn toggle'>Переключити</a>"
                      "</p></body></html>");
            server_.send(200, "text/html", html);
        });

        // Увімкнення реле через HTTP
        server_.on("/on", HTTP_GET, [this]() {
            relay_.setState(true);
            publishRelayState();
            server_.sendHeader("Location", "/");
            server_.send(303);
        });

        // Вимкнення реле через HTTP
        server_.on("/off", HTTP_GET, [this]() {
            relay_.setState(false);
            publishRelayState();
            server_.sendHeader("Location", "/");
            server_.send(303);
        });

        // Переключення стану через HTTP
        server_.on("/toggle", HTTP_GET, [this]() {
            relay_.toggle();
            publishRelayState();
            server_.sendHeader("Location", "/");
            server_.send(303);
        });

        // REST API endpoint для інтеграції
        server_.on("/api/status", HTTP_GET, [this]() {
            String json = "{\"relay\":" + String(relay_.getState() ? "true" : "false") +
                          ",\"uptime\":" + String(millis() / 1000) + "}";
            server_.send(200, "application/json", json);
        });

        // 404
        server_.onNotFound([this]() {
            server_.send(404, "text/plain", "404: Not Found");
        });

        server_.begin();
        Serial.println(F("HTTP-сервер успішно запущено на порту 80"));
    }

    /**
     * @brief Налаштування MQTT-клієнта.
     */
    void setupMqtt() {
        if (mqtt_server_.length() == 0) return;

        mqtt_client_.setServer(mqtt_server_.c_str(), mqtt_port_);
        mqtt_client_.setCallback([this](char* topic, uint8_t* payload, unsigned int length) {
            this->handleMqttMessage(topic, payload, length);
        });
    }

    /**
     * @brief Неблокуюча спроба підключення до MQTT-брокера.
     */
    void reconnectMqtt() {
        if (WiFi.status() != WL_CONNECTED) return;

        Serial.print(F("Спроба підключення до MQTT-брокера... "));

        bool connected = false;
        if (mqtt_user_.length() > 0) {
            connected = mqtt_client_.connect(mqtt_client_id_.c_str(), mqtt_user_.c_str(), mqtt_pass_.c_str());
        } else {
            connected = mqtt_client_.connect(mqtt_client_id_.c_str());
        }

        if (connected) {
            Serial.println(F("З'єднання з MQTT встановлено!"));
            mqtt_client_.subscribe(mqtt_command_topic_.c_str());
            publishRelayState();
        } else {
            Serial.print(F("Помилка підключення MQTT, код станом: "));
            Serial.println(mqtt_client_.state());
        }
    }

    /**
     * @brief Обробка вхідних команд з MQTT-топіка.
     */
    void handleMqttMessage(char* topic, uint8_t* payload, unsigned int length) {
        String message;
        for (unsigned int i = 0; i < length; i++) {
            message += (char)payload[i];
        }
        message.trim();
        message.toUpperCase();

        Serial.print(F("Отримано MQTT команду ["));
        Serial.print(topic);
        Serial.print(F("]: "));
        Serial.println(message);

        if (message == "ON" || message == "1" || message == "TRUE") {
            relay_.setState(true);
            publishRelayState();
        } else if (message == "OFF" || message == "0" || message == "FALSE") {
            relay_.setState(false);
            publishRelayState();
        } else if (message == "TOGGLE") {
            relay_.toggle();
            publishRelayState();
        }
    }
};

#endif // NETWORK_MANAGER_H
