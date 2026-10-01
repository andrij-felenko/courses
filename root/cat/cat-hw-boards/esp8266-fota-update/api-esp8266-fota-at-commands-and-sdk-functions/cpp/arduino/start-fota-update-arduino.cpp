#include <ESP8266httpUpdate.h>

void start_fota_update_arduino(const char* url) {
    WiFiClient client;
    t_httpUpdate_return ret = ESPhttpUpdate.update(client, url);
    
    switch (ret) {
        case HTTP_UPDATE_FAILED:
            Serial.printf("FOTA Error (%d): %s\n", 
                          ESPhttpUpdate.getLastError(), 
                          ESPhttpUpdate.getLastErrorString().c_str());
            break;
        case HTTP_UPDATE_NO_UPDATES:
            Serial.println("No updates found.");
            break;
        case HTTP_UPDATE_OK:
            Serial.println("FOTA Success! Rebooting...");
            break;
    }
}
