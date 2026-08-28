#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_W    128
#define SCREEN_H     64
#define OLED_ADDR  0x3C     // те, що показав сканер; зрідка 0x3D
#define OLED_RESET   -1     // I2C-модуль 0.96" не має окремої ніжки RESET

// Буфер 128*64/8 = 1024 байти живе всередині цього об'єкта, у RAM МК.
Adafruit_SSD1306 display(SCREEN_W, SCREEN_H, &Wire, OLED_RESET);

void setup() {
  Serial.begin(115200);
  Wire.begin();

  // SWITCHCAPVCC — увімкнути внутрішній зарядний насос (та сама пара 0x8D,0x14).
  // begin() ще й ВИДІЛЯЄ 1024 байти під буфер і повертає false, якщо RAM не стало.
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("SSD1306: begin() не вдався — адреса або брак RAM");
    for (;;) { }            // далі йти немає сенсу
  }

  display.clearDisplay();   // очистити буфер (у RAM; на склі ще старе/сміття)
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2);
  display.setCursor(0, 20);
  display.println("Привіт!");
  display.display();        // ← ОЦЕ штовхає буфер на скло. Без нього — порожньо.
}

void loop() { }
