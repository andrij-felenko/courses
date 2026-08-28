#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_W 128
#define SCREEN_H  64
Adafruit_SSD1306 display(SCREEN_W, SCREEN_H, &Wire, -1);

enum HudState { ST_IDLE, ST_MEASURE, ST_ALARM, ST_CONFIG };

// Людські назви станів для верхнього рядка.
const char* stateName(HudState s) {
  switch (s) {
    case ST_IDLE:    return "IDLE";
    case ST_MEASURE: return "MEASURE";
    case ST_ALARM:   return "ALARM";
    case ST_CONFIG:  return "CONFIG";
  }
  return "?";
}

const char* MENU[] = { "Run", "Zero", "Rng", "Set" };   // підписи КОРОТКІ навмисне — щоб рядок уклався в 128 px (розрахунок нижче)
const int   MENU_N = 4;

// Намалювати ВЕСЬ кадр за поточним станом. Викликається щоразу, коли щось змінилось.
void drawHud(HudState st, int32_t centi, int cursor) {
  display.clearDisplay();                 // чистимо буфер, малюємо кадр з нуля

  // — Зона 1: рядок стану вгорі, у рамці-плашці ————————————————
  display.drawRect(0, 0, SCREEN_W, 14, SSD1306_WHITE);
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(4, 3);
  display.print("St: ");
  display.print(stateName(st));

  // — Зона 2: велике число посередині, ціле «з комою вручну» ————————
  int32_t whole = centi / 100;            // ціла частина
  int32_t frac  = centi % 100;            // дві цифри після коми
  if (frac < 0) frac = -frac;             // модуль, щоб «-1.05» не став «-1.-5»
  char big[16];
  snprintf(big, sizeof(big), "%ld.%02ld", (long)whole, (long)frac);
  display.setTextSize(3);                 // розмір 3 ≈ 18x24 пікселі на символ
  display.setCursor(6, 20);
  display.print(big);
  display.setTextSize(1);                 // одиниці — дрібним, у куточку
  display.setCursor(104, 30);
  display.print("C");

  // — Зона 3: рядок меню внизу, курсор «>» перед активним пунктом ——————
  // Пікселний бюджет вирішує все: на кожен пункт іде (курсор + літери + проміжок) × 6 px.
  // {Run,Zero,Rng,Set} = (5+6+5+5)·6 = 126 px — влазить у 128 з малим запасом;
  // з довгими «Start»,«Range» останній пункт зрізало б за правим краєм екрана.
  display.drawFastHLine(0, 50, SCREEN_W, SSD1306_WHITE);  // відділити меню лінією
  int x = 2;
  for (int i = 0; i < MENU_N; i++) {
    display.setCursor(x, 54);
    display.print(i == cursor ? ">" : " ");   // курсор перед активним пунктом
    display.print(MENU[i]);
    x += (strlen(MENU[i]) + 2) * 6;           // курсор + підпис + проміжок, по 6 px на символ
  }

  display.display();                      // ← штовхаємо весь кадр на скло
}

void setup() {
  Wire.begin();
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { for (;;) {} }
}

void loop() {
  // Демонстрація: ганяємо стани й число, курсор повзе по меню.
  static int32_t t = 2500;                // 25.00 °C у сотих
  static int cursor = 0;
  static HudState st = ST_MEASURE;

  t += 7;                                 // «давач» поволі росте
  if (t > 8000) { st = ST_ALARM; }        // перейшли в тривогу за межею
  else          { st = ST_MEASURE; }

  drawHud(st, t, cursor);                 // перемалювали кадр
  cursor = (cursor + 1) % MENU_N;         // курсор на наступний пункт
  delay(400);
}
