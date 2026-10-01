#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

constexpr uint8_t SCREEN_WIDTH = 128;
constexpr uint8_t SCREEN_HEIGHT = 64;
constexpr int8_t OLED_RESET_PIN = -1;
constexpr uint8_t OLED_I2C_ADDRESS = 0x3C;

// Клас формування тестової графіки для перевірки суміщення з вирізом у корпусі
class DisplayPattern {
public:
    explicit DisplayPattern(Adafruit_SSD1306& display)
        : display_(display), width_(display.width()), height_(display.height()) {}

    // Малювання прямокутної рамки по крайніх пікселях матриці 128x64
    void drawOuterBorder() {
        display_.drawRect(0, 0, width_, height_, SSD1306_WHITE);
    }

    // Малювання центрального перехрестя для контролю симетрії вирізу
    void drawCenterCrosshair() {
        const int16_t centerX = width_ / 2;
        const int16_t centerY = height_ / 2;
        const int16_t crossSize = 8;

        display_.drawFastHLine(centerX - crossSize, centerY, crossSize * 2 + 1, SSD1306_WHITE);
        display_.drawFastVLine(centerX, centerY - crossSize, crossSize * 2 + 1, SSD1306_WHITE);
    }

    // Малювання кутових маркерів для оцінки кутових зазорів
    void drawCornerMarkers() {
        const int16_t markerLen = 5;

        // Верхній лівий кут
        display_.drawFastHLine(0, 0, markerLen, SSD1306_WHITE);
        display_.drawFastVLine(0, 0, markerLen, SSD1306_WHITE);

        // Верхній правий кут
        display_.drawFastHLine(width_ - markerLen, 0, markerLen, SSD1306_WHITE);
        display_.drawFastVLine(width_ - 1, 0, markerLen, SSD1306_WHITE);

        // Нижній лівий кут
        display_.drawFastHLine(0, height_ - 1, markerLen, SSD1306_WHITE);
        display_.drawFastVLine(0, height_ - markerLen, markerLen, SSD1306_WHITE);

        // Нижній правий кут
        display_.drawFastHLine(width_ - markerLen, height_ - 1, markerLen, SSD1306_WHITE);
        display_.drawFastVLine(width_ - 1, height_ - markerLen, markerLen, SSD1306_WHITE);
    }

    // Очищення буфера та відмальовка повного тестового шаблону
    void renderFullPattern() {
        display_.clearDisplay();
        drawOuterBorder();
        drawCenterCrosshair();
        drawCornerMarkers();
        display_.display();
    }

private:
    Adafruit_SSD1306& display_;
    int16_t width_;
    int16_t height_;
};

static Adafruit_SSD1306 oledDisplay(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET_PIN);
static DisplayPattern patternRenderer(oledDisplay);

void setup() {
    Serial.begin(115200);

    // Ініціалізація I2C шини та драйвера OLED-дисплея
    if (!oledDisplay.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDRESS)) {
        Serial.println(F("Помилка ініціалізації OLED-дисплея!"));
        for (;;) {
            delay(1000);
        }
    }

    // Вивід прямокутного контуру та реперів для контролю обробки надфілями
    patternRenderer.renderFullPattern();
    Serial.println(F("Тестову рамку успішно виведено на дисплей."));
}

void loop() {
    // Загальмовуємо цикл: тестовий шаблон постійно утримується на екрані
    delay(500);
}
