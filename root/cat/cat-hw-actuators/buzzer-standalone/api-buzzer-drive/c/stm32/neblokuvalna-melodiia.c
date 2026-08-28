#include "main.h"
#include <stdbool.h>
// tone_hz() — та сама, що у вкладці STM32 вище (ARR задає частоту)

typedef struct { uint16_t freq; uint16_t ms; } Note;    // 0 Гц = пауза

typedef struct {
  const Note *song;          // масив нот поточної мелодії
  uint16_t    len, idx;      // скільки нот у ній і яку граємо просто зараз
  uint32_t    ends_at;       // мить (HAL_GetTick), коли нота скінчиться
  bool        active;
} Player;

static void start_note(Player *p) {
  const Note *n = &p->song[p->idx];
  tone_hz(n->freq);                        // 0 Гц → зупинити ШІМ, тобто пауза
  p->ends_at = HAL_GetTick() + n->ms;      // ось коли її знімати
}

// Запустити мелодію з початку (перериває попередню, якщо грала)
void player_play(Player *p, const Note *s, uint16_t n) {
  p->song = s; p->len = n; p->idx = 0; p->active = true;
  start_note(p);                           // одразу вмикаємо першу ноту
}

void player_stop(Player *p) { tone_hz(0); p->active = false; }

// Викликати ЩОРАЗУ в while(1). Нічого не блокує: лише дивиться на годинник.
void player_update(Player *p) {
  if (!p->active) return;
  // різниця, а не абсолют, — тому перехід лічильника через нуль не страшний
  if ((int32_t)(HAL_GetTick() - p->ends_at) < 0) return;
  if (++p->idx >= p->len) { player_stop(p); return; }   // мелодія скінчилась
  start_note(p);
}
