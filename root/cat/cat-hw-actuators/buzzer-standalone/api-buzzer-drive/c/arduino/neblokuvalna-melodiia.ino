struct Note { uint16_t freq; uint16_t ms; };   // частота (0 = пауза) і тривалість

class BuzzerPlayer {
  uint8_t        pin;
  const Note*    song = nullptr;   // масив нот поточної мелодії
  uint16_t       len  = 0;         // скільки нот у ній
  uint16_t       idx  = 0;         // яку ноту граємо просто зараз
  unsigned long  noteEndsAt = 0;   // мить (millis), коли поточна нота скінчиться
  bool           active = false;

public:
  explicit BuzzerPlayer(uint8_t p) : pin(p) { pinMode(pin, OUTPUT); }

  // Запустити мелодію з початку (перериває попередню, якщо грала)
  void play(const Note* s, uint16_t n) {
    song = s; len = n; idx = 0; active = true;
    startNote();                   // одразу вмикаємо першу ноту
  }

  void stop() { noTone(pin); active = false; }
  bool isPlaying() const { return active; }

  // Викликати ЩОРАЗУ в loop(). Нічого не блокує: лише дивиться на годинник.
  void update() {
    if (!active) return;
    if (millis() < noteEndsAt) return;         // ще рано — виходимо миттєво

    idx++;                                      // час ноти вийшов → наступна
    if (idx >= len) { stop(); return; }         // мелодія скінчилась
    startNote();
  }

private:
  void startNote() {
    const Note& n = song[idx];
    if (n.freq == 0) noTone(pin);               // 0 Гц → пауза (тиша)
    else             tone(pin, n.freq);
    noteEndsAt = millis() + n.ms;               // ось коли її знімати
  }
};
