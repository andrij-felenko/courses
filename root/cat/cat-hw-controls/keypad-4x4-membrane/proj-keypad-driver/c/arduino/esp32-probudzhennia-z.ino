#include <Keypad.h>
#include "esp_sleep.h"
#include "driver/rtc_io.h"
#include "driver/gpio.h"

const byte ROWS = 4, COLS = 4;
char keys[ROWS][COLS] = {
    {'1','2','3','A'},
    {'4','5','6','B'},
    {'7','8','9','C'},
    {'*','0','#','D'}
};
// рядки — на RTC-здатні ноги (лише такі вміє стежити ext1):
byte rowPins[ROWS] = {32, 33, 25, 26};
// стовпці — звичайні ведені ноги, свідомо БЕЗ стрепінгових (GPIO12 уникаємо → 4 замість неї):
byte colPins[COLS] = {27, 14, 4, 13};

Keypad kpd = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

RTC_DATA_ATTR uint32_t wakeCount = 0;   // переживає сон у RTC-пам'яті

// маска рядкових ніг для ext1 (біт номера GPIO):
const uint64_t ROW_MASK =
    (1ULL << 32) | (1ULL << 33) | (1ULL << 25) | (1ULL << 26);

void setup() {
    Serial.begin(115200);
    delay(150);
    wakeCount++;

    // Після глибокого сну стовпці лишаються ЗАФІКСОВАНІ (hold) з минулого разу —
    // спершу зняти фіксацію, інакше бібліотека не зможе гнати сітку для сканування:
    gpio_deep_sleep_hold_dis();
    for (byte c = 0; c < COLS; c++) gpio_hold_dis((gpio_num_t)colPins[c]);

    if (esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_EXT1) {
        Serial.printf("Прокинувся від натиску #%u\n", wakeCount);
        char k = NO_KEY;
        for (byte t = 0; t < 40 && k == NO_KEY; t++) { k = kpd.getKey(); delay(2); }
        if (k != NO_KEY) { Serial.print("клавіша: "); Serial.println(k); }
        // тут: обробити подію
    } else {
        Serial.println("Холодний старт.");
    }

    // --- Перевести сітку в ДЗЕРКАЛЬНИЙ арм-стан (під те, що вміє класичний ESP32) ---
    for (byte c = 0; c < COLS; c++) {
        pinMode(colPins[c], OUTPUT);
        digitalWrite(colPins[c], HIGH);               // усі стовпці у «1»
        gpio_hold_en((gpio_num_t)colPins[c]);         // ЗАФІКСУВАТИ «1»: цифровий драйвер у сні гасне
    }
    for (byte r = 0; r < ROWS; r++) {
        pinMode(rowPins[r], INPUT_PULLDOWN);              // рядки у спокої «0»
        rtc_gpio_pulldown_en((gpio_num_t)rowPins[r]);     // підтяжка ВНИЗ мусить жити й у сні
        rtc_gpio_pullup_dis((gpio_num_t)rowPins[r]);
    }
    gpio_deep_sleep_hold_en();                        // тримати фіксацію стовпців і в глибокому сні

    // будити, коли БУДЬ-ЯКА стежена нога стане ВИСОКОЮ (натиск підіймає рядок у «1»):
    esp_sleep_enable_ext1_wakeup(ROW_MASK, ESP_EXT1_WAKEUP_ANY_HIGH);

    Serial.println("Засинаю. Розбудить натиск.");
    Serial.flush();
    esp_deep_sleep_start();     // усе нижче не виконається — після сну setup() почнеться заново
}

void loop() { }                // при глибокому сні не потрібен: після сну виконується setup()
