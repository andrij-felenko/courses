#define RING_SIZE 64                 // мусить бути степенем двійки
#define RING_MASK (RING_SIZE - 1)

static volatile uint32_t buf[RING_SIZE];   // дані: тут — мітки часу
static volatile uint16_t head = 0;         // куди пише ISR
static volatile uint16_t tail = 0;         // звідки читає main

// --- письменник: лише з ISR (єдиний хазяїн head) ---
static inline bool ring_push(uint32_t item) {
  uint16_t h = head;                 // head пише лише ISR — читаємо свій індекс
  uint16_t next = (h + 1) & RING_MASK;
  if (next == tail) return false;    // повно -> відкидаємо новий (політика на ваш вибір)
  buf[h] = item;                     // 1) спершу ДАНІ
  head = next;                       // 2) потім ОПУБЛІКУВАТИ індекс
  return true;
}

// --- читач: лише з main/loop (єдиний хазяїн tail) ---
static inline bool ring_pop(uint32_t *out) {
  uint16_t t = tail;                 // tail читає лише main — читаємо свій індекс
  if (t == head) return false;       // порожньо
  *out = buf[t];                     // 1) спершу забрати дані
  tail = (t + 1) & RING_MASK;        // 2) потім звільнити слот
  return true;
}
