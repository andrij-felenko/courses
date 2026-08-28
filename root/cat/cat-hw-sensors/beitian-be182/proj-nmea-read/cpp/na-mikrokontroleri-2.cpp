// Те саме, але через TinyGPS++: бібліотека сама робить усі п'ять ланок.
#include <TinyGPS++.h>

TinyGPSPlus gps;

void setup() {
    Serial.begin(115200);
    Serial1.begin(38400);      // BE-182 за замовчуванням — 38400
}

void loop() {
    while (Serial1.available())
        gps.encode(Serial1.read());          // згодувати кожен байт

    // isValid() — це і є перевірка «fix є, координатам можна вірити»
    if (gps.location.isUpdated() && gps.location.isValid()) {
        Serial.print("lat=");  Serial.print(gps.location.lat(), 6);   // десяткові!
        Serial.print(" lon="); Serial.print(gps.location.lng(), 6);
        Serial.print(" sats="); Serial.println(gps.satellites.value());
    }
}
