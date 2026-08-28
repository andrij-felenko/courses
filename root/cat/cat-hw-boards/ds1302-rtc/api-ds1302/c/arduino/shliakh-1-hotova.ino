#include <ThreeWire.h>          // низький рівень трипровідного обміну
#include <RtcDS1302.h>          // сам годинник поверх ThreeWire

// Порядок аргументів: IO(DAT), SCLK(CLK), CE(RST) — саме так, не як у підписах плати.
// Класична Arduino UNO/Nano:
ThreeWire myWire(4, 5, 2);      // DAT=D4, CLK=D5, RST=D2
// ESP32 (будь-які вільні GPIO): ThreeWire myWire(27, 14, 26);

RtcDS1302<ThreeWire> Rtc(myWire);

void printDateTime(const RtcDateTime& dt);   // оголошення, тіло — нижче

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 2000) { }     // дочекатись термінала, але не вічно

  Rtc.Begin();

  // Час компіляції як стартове значення: __DATE__ і __TIME__ підставляє компілятор.
  // Це момент, коли ви натиснули «Завантажити», з точністю до кількох секунд.
  RtcDateTime compiled = RtcDateTime(__DATE__, __TIME__);

  // 1) Зняти захист запису (WP). Без цього SetDateTime тихо нічого не зробить.
  if (Rtc.GetIsWriteProtected()) {
    Serial.println(F("RTC був захищений від запису — знімаю захист."));
    Rtc.SetIsWriteProtected(false);
  }

  // 2) Пустити годинник, якщо він стоїть (біт CH=1 на свіжій мікросхемі).
  if (!Rtc.GetIsRunning()) {
    Serial.println(F("RTC стояв — запускаю генератор."));
    Rtc.SetIsRunning(true);
  }

  // 3) Виставити час ЛИШЕ якщо збережений менший за час компіляції або недійсний.
  //    Інакше щоразу після перезапуску ви б затирали ЖИВИЙ час часом прошивки.
  RtcDateTime now = Rtc.GetDateTime();
  if (!Rtc.IsDateTimeValid() || now < compiled) {
    Serial.println(F("Час недійсний або застарілий — ставлю час компіляції."));
    Rtc.SetDateTime(compiled);
  }
}

void loop() {
  RtcDateTime now = Rtc.GetDateTime();        // одна структура — весь календар
  printDateTime(now);
  Serial.println();

  if (!now.IsValid()) {
    // Найчастіша причина — розряджена або відсутня батарейка (годинник «забув» час).
    Serial.println(F("!! Час недійсний — перевірте CR2032."));
  }

  delay(5000);                                 // читати раз на 5 с досить
}

void printDateTime(const RtcDateTime& dt) {
  char buf[24];
  snprintf(buf, sizeof(buf), "%04u-%02u-%02u %02u:%02u:%02u",
           dt.Year(), dt.Month(), dt.Day(),
           dt.Hour(), dt.Minute(), dt.Second());
  Serial.print(buf);
}
