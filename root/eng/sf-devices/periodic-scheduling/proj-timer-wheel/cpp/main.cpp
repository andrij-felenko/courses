#define WHEEL_SIZE 256          // степінь двійки → mod = маска

typedef struct Timer {
  uint32_t rounds;              // скільки повних кіл ще чекати
  void (*cb)(void*);            // що зробити, коли настане час
  void *arg;
  struct Timer *next;           // наступний у тому ж слоті
} Timer;

static Timer *wheel[WHEEL_SIZE];
static uint32_t cursor;          // «стрілка» — поточний слот

// запланувати подію через delta тіків
void schedule(Timer *t, uint32_t delta) {
  uint32_t slot = (cursor + delta) & (WHEEL_SIZE - 1);
  t->rounds = delta / WHEEL_SIZE;     // повних обертів колеса
  t->next = wheel[slot];              // вставляємо в голову списку слота — O(1)
  wheel[slot] = t;
}

// викликати рівно раз на тік (з обробника системного тіку)
void tick(void) {
  cursor = (cursor + 1) & (WHEEL_SIZE - 1);
  Timer **pp = &wheel[cursor];        // ідемо лише по ОДНОМУ слоту
  while (*pp) {
    Timer *t = *pp;
    if (t->rounds == 0) {
      *pp = t->next;                   // знімаємо зі слота
      t->cb(t->arg);                   // час настав — запускаємо
    } else {
      t->rounds--;                     // ще одне коло перечекати
      pp = &t->next;
    }
  }
}
