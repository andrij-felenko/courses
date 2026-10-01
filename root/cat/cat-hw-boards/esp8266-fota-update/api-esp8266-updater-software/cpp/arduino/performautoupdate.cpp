#include <ESP8266WiFi.h>
#include <ESP8266httpUpdate.h>

void performAutoUpdate(const char* serverUrl, const char* currentVersion) {
  WiFiClient client;

  // Реєстрація колбеку індикації прогресу
  ESPhttpUpdate.onProgress([](int current, int total) {
    Serial.printf("Прогрес оновлення: %d%% (%d / %d байт)\n", (current * 100) / total, current, total);
  });

  // Запуск автоматичного перевірочного виклику FOTA
  t_httpUpdate_return ret = ESPhttpUpdate.update(client, serverUrl, currentVersion);

  switch (ret) {
    case HTTP_UPDATE_NO_UPDATES:
      Serial.println("ПЗ актуальне. Оновлення не потрібне.");
      break;
    case HTTP_UPDATE_OK:
      Serial.println("Оновлення прийнято. Перезавантаження пристрою...");
      break;
    case HTTP_UPDATE_FAILED:
      Serial.printf("Помилка HTTPUpdate (%d): %s\n", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
      break;
  }
}
