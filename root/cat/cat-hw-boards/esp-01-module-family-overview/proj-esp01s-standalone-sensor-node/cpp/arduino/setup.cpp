#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11

const char* ssid = "WiFi_Network";
const char* password = "SecretPassword";
const char* serverUrl = "http://192.168.1.100/api/data";

DHT dht(DHTPIN, DHTTYPE);
WiFiClient client;

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void loop() {
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  if (!isnan(temp) && !isnan(humidity)) {
    HTTPClient http;
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    String jsonPayload = "{\"temperature\":" + String(temp, 1) + ",\"humidity\":" + String(humidity, 1) + "}";
    int httpResponseCode = http.POST(jsonPayload);
    http.end();
  }
  
  delay(10000);
}
