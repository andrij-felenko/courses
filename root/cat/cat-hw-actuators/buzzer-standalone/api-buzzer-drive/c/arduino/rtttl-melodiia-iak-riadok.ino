#include <Arduino.h>

// Частоти нот c..b для октав 4..7. Індекс: (октава-4)*12 + півтон_від_C.
// Півтони в межах октави: c c# d d# e f f# g g# a a# b  (0..11)
static const uint16_t NOTE_FREQ[] PROGMEM = {
  // октава 4
  262,277,294,311,330,349,370,392,415,440,466,494,
  // октава 5
  523,554,587,622,659,698,740,784,831,880,932,988,
  // октава 6
 1047,1109,1175,1245,1319,1397,1480,1568,1661,1760,1865,1976,
  // октава 7
 2093,2217,2349,2489,2637,2794,2960,3136,3322,3520,3729,3951,
};

// Півтон-зсув літери від C у межах октави (a..g). -1 = нема такої.
static int8_t noteOffset(char c) {
  switch (c) {
    case 'c': return 0;  case 'd': return 2;  case 'e': return 4;
    case 'f': return 5;  case 'g': return 7;  case 'a': return 9;
    case 'b': return 11; default:  return -1;         // 'p' або сміття
  }
}

// Обчислити частоту ноти (0 = пауза/поза діапазоном)
static uint16_t noteToFreq(char letter, bool sharp, int octave) {
  int off = noteOffset(letter);
  if (off < 0) return 0;                     // пауза
  if (sharp)  off += 1;                       // дієз — на півтона вище
  int idx = (octave - 4) * 12 + off;
  if (idx < 0 || idx >= (int)(sizeof(NOTE_FREQ)/sizeof(NOTE_FREQ[0])))
    return 0;                                 // поза таблицею
  return pgm_read_word(&NOTE_FREQ[idx]);
}
