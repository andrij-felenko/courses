#include <SoftwareSerial.h>

// SoftwareSerial(rxPin, txPin): rxPin приймає ВІД модуля, txPin шле В модуль.
//   D10 ← TXD модуля (напряму, TXD віддає 3.3 В — Uno читає як 1)
//   D11 → RXD модуля (ТІЛЬКИ через дільник 1к/2к! 5 В прямо псує вхід)
SoftwareSerial btSerial(10, 11);   // (RX, TX) з боку Arduino

void setup() {
    Serial.begin(9600);      // апаратний порт → монітор по USB
    btSerial.begin(9600);    // програмний порт → модуль, РОБОЧА швидкість
    Serial.println("Готово. Байти між монітором і модулем ідуть наскрізь.");
}
