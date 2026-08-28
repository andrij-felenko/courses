// --- БЕЗ volatile: зависає назавжди ---
bool flag = false;
void IRAM_ATTR isr() { flag = true; }
…
while (!flag) { }          // компілятор кешує flag → цикл вічний ✗

// --- З volatile: працює ---
volatile bool flag = false;
void IRAM_ATTR isr() { flag = true; }
…
while (!flag) { }          // щоразу читає пам'ять → виходить по події ✓
