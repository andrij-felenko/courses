#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <ctype.h>
#include <stdbool.h>
// buzzer_init() / buzzer_tone() / note_to_freq() — з прикладів вище

// Рядок RTTTL — звичайний const char* у флеші, курсор іде по ньому як по RAM.
// Пристрій тут не завмирає з іншої причини, ніж в Arduino: мелодія живе у
// ВЛАСНІЙ задачі, а vTaskDelay віддає процесор іншим задачам, а не крутить його.
static void rtttl_task(void *arg) {
  const char *p = (const char *)arg;
  int def_dur = 4, def_oct = 6;
  long whole_ms = 0;

  while (*p && *p++ != ':') { }                    // пропустити назву до ':'
  while (*p && *p != ':') {                        // умовчання: ключ=значення
    char key = *p++;
    if (*p++ == '=') {
      int v = 0;
      while (isdigit((unsigned char)*p)) v = v * 10 + (*p++ - '0');
      if      (key == 'd') def_dur  = v;
      else if (key == 'o') def_oct  = v;
      else if (key == 'b') whole_ms = 240000L / v; // ціла нота = 4 удари
    }
    if (*p == ',') p++;
  }
  if (*p == ':') p++;                              // з'їсти другу ':'

  while (*p) {
    while (*p == ',' || *p == ' ') p++;            // коми/пробіли між нотами
    if (!*p) break;

    int dur = 0;                                   // 1) тривалість або умовчання
    while (isdigit((unsigned char)*p)) dur = dur * 10 + (*p++ - '0');
    if (!dur) dur = def_dur;

    char letter = *p++;                            // 2) літера ноти ('p' — пауза)
    bool sharp = (*p == '#');                      // 3) необов'язковий дієз
    if (sharp) p++;

    int oct = def_oct;                             // 4) необов'язкова октава
    if (isdigit((unsigned char)*p)) {
      oct = 0;
      while (isdigit((unsigned char)*p)) oct = oct * 10 + (*p++ - '0');
    }

    long ms = whole_ms / dur;                      // 5) крапка — плюс половина
    if (*p == '.') { ms += ms / 2; p++; }

    buzzer_tone(note_to_freq(letter, sharp, oct)); // 0 Гц → пауза
    vTaskDelay(pdMS_TO_TICKS(ms));
  }

  buzzer_tone(0);                                  // кінець рядка — тиша
  vTaskDelete(NULL);                               // задача знімає сама себе
}
