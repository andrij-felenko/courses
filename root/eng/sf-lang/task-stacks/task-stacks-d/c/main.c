// створюємо задачу з 4 КБ стека (на ESP32 — у БАЙТАХ):
xTaskCreate(taskWork, "work", 4096, NULL, 1, NULL);

// під навантаженням перевіряємо водяний знак (з самої задачі):
UBaseType_t leftFree = uxTaskGetStackHighWaterMark(NULL);
//  leftFree велике  → стека з запасом, можна зменшити
//  leftFree ~ 0     → на межі переповнення, ТЕРМІНОВО збільшити

// небезпечний буфер на стеку → виносимо:
void task(void*) { char buf[4096];        /* ... */ }   // ✗ рве 4-КБ стек
void task(void*) { static char buf[4096]; /* ... */ }   // ✓ не на стеку
