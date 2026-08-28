// --- KY-016: керування кольором, катод АБО анод ---
const uint8_t PIN_R = 9;      // усі три — PWM-піни (з «~» на Uno)
const uint8_t PIN_G = 10;
const uint8_t PIN_B = 11;

// true  — плата зі СПІЛЬНИМ АНОДОМ (колір вмикає низький рівень)
// false — плата зі СПІЛЬНИМ КАТОДОМ (колір вмикає високий рівень)
const bool COMMON_ANODE = false;

// один вихід каналу: тут і тільки тут живе інверсія для анода
static inline uint8_t level(uint8_t v) {
  return COMMON_ANODE ? (uint8_t)(255 - v) : v;
}

void setColor(uint8_t r, uint8_t g, uint8_t b) {
  analogWrite(PIN_R, level(r));   // r,g,b — «людська» яскравість: 255 = яскраво
  analogWrite(PIN_G, level(g));
  analogWrite(PIN_B, level(b));
}

void setup() {
  pinMode(PIN_R, OUTPUT);
  pinMode(PIN_G, OUTPUT);
  pinMode(PIN_B, OUTPUT);
  setColor(255, 90, 0);           // теплий помаранчевий — однаково на обох типах плат
}

void loop() {}
