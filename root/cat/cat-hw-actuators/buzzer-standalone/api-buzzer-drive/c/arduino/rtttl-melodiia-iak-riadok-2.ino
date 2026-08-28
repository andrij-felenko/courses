class RtttlPlayer {
  const char*   p;              // курсор у рядку RTTTL (PROGMEM)
  int           defDur = 4;     // d=
  int           defOct = 6;     // o=
  long          wholeMs = 0;    // тривалість цілої ноти в мс (з b=)
  bool          active = false;
  unsigned long noteEndsAt = 0;
  uint8_t       pin;

  char peek() { return pgm_read_byte(p); }         // глянути символ
  char take() { return pgm_read_byte(p++); }        // взяти й посунутись

  // Прочитати ціле число під курсором (0, якщо цифр нема)
  int number() {
    int n = 0;
    while (isdigit(peek())) n = n * 10 + (take() - '0');
    return n;
  }

public:
  explicit RtttlPlayer(uint8_t pin_) : pin(pin_) { pinMode(pin, OUTPUT); }

  // Розібрати заголовок і стати на перший символ нот
  void begin(const char* song) {
    p = song;
    while (peek() && take() != ':') { }             // пропустити назву до ':'
    // блок умовчань: пари ключ=значення через кому, до ':'
    while (peek() && peek() != ':') {
      char key = take();
      if (take() == '=') {
        int v = number();
        if      (key == 'd') defDur = v;
        else if (key == 'o') defOct = v;
        else if (key == 'b') wholeMs = 240000L / v; // ціла нота = 4 удари
      }
      if (peek() == ',') take();
    }
    if (peek() == ':') take();                        // з'їсти другу ':'
    active = true;
    nextNote();                                       // одразу першу
  }

  bool isPlaying() const { return active; }

  // Викликати в loop() — неблокувально, як у BuzzerPlayer
  void update() {
    if (!active) return;
    if (millis() < noteEndsAt) return;
    nextNote();
  }

private:
  void nextNote() {
    // пропустити коми/пробіли між нотами
    while (peek() == ',' || peek() == ' ') take();
    if (!peek()) { noTone(pin); active = false; return; }   // кінець рядка

    // 1) тривалість: число або умовчання
    int dur = number();
    if (dur == 0) dur = defDur;

    // 2) літера ноти (або 'p' — пауза)
    char letter = take();

    // 3) необов'язковий дієз
    bool sharp = false;
    if (peek() == '#') { sharp = true; take(); }

    // 4) необов'язкова октава
    int oct = defOct;
    if (isdigit(peek())) oct = number();

    // 5) необов'язкова крапка — подовжує на половину
    bool dotted = false;
    if (peek() == '.') { dotted = true; take(); }

    // тривалість у мс: ціла нота / дільник, з урахуванням крапки
    long ms = wholeMs / dur;
    if (dotted) ms += ms / 2;

    uint16_t f = noteToFreq(letter, sharp, oct);
    if (f == 0) noTone(pin);                // пауза або поза діапазоном
    else        tone(pin, f);
    noteEndsAt = millis() + ms;
  }
};
