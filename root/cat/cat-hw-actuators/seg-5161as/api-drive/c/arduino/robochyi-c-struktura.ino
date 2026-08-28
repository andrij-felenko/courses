#include <Arduino.h>

class Seg5161 {
public:
  // pins[8] у порядку a,b,c,d,e,f,g,DP.
  // commonAnode = false для 5161AS (спільний катод), true для 5161BS.
  Seg5161(const uint8_t (&pins)[8], bool commonAnode = false)
    : _anode(commonAnode) {
    for (uint8_t i = 0; i < 8; i++) _pin[i] = pins[i];
  }

  void begin() {
    for (uint8_t i = 0; i < 8; i++) {
      pinMode(_pin[i], OUTPUT);
      writeSeg(i, false);            // старт із погашеного
    }
  }

  // Показати вже готову маску (біт=сегмент, порядок a..g,DP)
  void showMask(uint8_t mask) {
    for (uint8_t i = 0; i < 8; i++)
      writeSeg(i, (mask >> i) & 1);
  }

  // Показати символ 0..15 (0-9,A,b,C,d,E,F), опційно з крапкою
  void showHex(uint8_t v, bool dot = false) {
    uint8_t m = FONT[v & 0x0F];
    if (dot) m |= SDP;
    showMask(m);
  }

  void clear() { showMask(0); }

private:
  uint8_t _pin[8];
  bool    _anode;

  // Один сегмент: on=true → світиться. Полярність вирішує рівень.
  void writeSeg(uint8_t i, bool on) {
    // Спільний катод: сегмент світиться від HIGH.
    // Спільний анод:  усе навпаки — світиться від LOW.
    bool level = _anode ? !on : on;
    digitalWrite(_pin[i], level);
  }
};

// --- використання ---
const uint8_t SEG_PINS[8] = { 2, 3, 4, 5, 6, 7, 8, 9 }; // a b c d e f g DP
Seg5161 disp(SEG_PINS, /*commonAnode=*/false);          // 5161AS

void setup() { disp.begin(); }

void loop() {
  for (uint8_t v = 0; v < 16; v++) {   // прокрутити 0..F
    disp.showHex(v, /*dot=*/(v == 10)); // крапку лише на «A» — для прикладу
    delay(500);
  }
}
