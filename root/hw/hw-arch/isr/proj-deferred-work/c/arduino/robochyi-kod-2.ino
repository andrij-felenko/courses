volatile uint8_t  buf[64];        // кільцевий буфер
volatile uint8_t  head = 0, tail = 0;   // індекси: пише обробник, читає loop

void IRAM_ATTR onByte() {         // верхня половина
  uint8_t next = (head + 1) % sizeof(buf);
  if (next != tail) {             // є місце?
    buf[head] = readByte();       // лише читання регістра + запис
    head = next;
  }                               // переповнення — мовчки відкидаємо
}

void loop() {                     // нижня половина
  while (tail != head) {          // поки є непрочитане
    uint8_t b = buf[tail];
    tail = (tail + 1) % sizeof(buf);
    parse(b);                     // розбір, друк, математика — без поспіху
  }
}
