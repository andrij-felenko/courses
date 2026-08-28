#include "esp_timer.h"
#include <stdbool.h>
// buzzer_init() / buzzer_tone() — ті самі, що у вкладці ESP-IDF вище

typedef struct { uint16_t freq; uint16_t ms; } note_t;  // 0 Гц = пауза

typedef struct {
  const note_t *song;        // масив нот поточної мелодії
  uint16_t      len, idx;    // скільки нот у ній і яку граємо просто зараз
  int64_t       ends_at_ms;  // мить, коли поточна нота скінчиться
  bool          active;
} player_t;

// millis() тут нема — годинник дає монотонний лічильник мікросекунд
static inline int64_t now_ms(void) { return esp_timer_get_time() / 1000; }

static void start_note(player_t *p) {
  const note_t *n = &p->song[p->idx];
  buzzer_tone(n->freq);                    // 0 Гц → duty = 0, тобто тиша
  p->ends_at_ms = now_ms() + n->ms;        // ось коли її знімати
}

// Запустити мелодію з початку (перериває попередню, якщо грала)
void player_play(player_t *p, const note_t *s, uint16_t n) {
  p->song = s; p->len = n; p->idx = 0; p->active = true;
  start_note(p);                           // одразу вмикаємо першу ноту
}

void player_stop(player_t *p) { buzzer_tone(0); p->active = false; }

// Викликати ЩОРАЗУ в циклі задачі. Нічого не блокує: лише дивиться на годинник.
void player_update(player_t *p) {
  if (!p->active) return;
  if (now_ms() < p->ends_at_ms) return;    // ще рано — виходимо миттєво
  if (++p->idx >= p->len) { player_stop(p); return; }   // мелодія скінчилась
  start_note(p);
}
