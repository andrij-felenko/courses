const uint8_t  PIN_POT = A0;
const uint8_t  WIN = 16;             // розмір вікна усереднення (степінь 2 — зручно)

int      buf[WIN];                   // кільцевий буфер останніх відліків
uint8_t  idx = 0;                    // куди писати наступний відлік
long     sum = 0;                    // поточна сума вмісту буфера (щоб не рахувати щоразу)

void potBegin() {
  int first = analogRead(PIN_POT);
  for (uint8_t i = 0; i < WIN; i++) { buf[i] = first; sum += first; }  // старт без «розгону»
}

int potReadAveraged() {
  sum -= buf[idx];                   // прибрати найстаріший відлік із суми
  int fresh = analogRead(PIN_POT);
  buf[idx] = fresh;                  // записати найновіший на його місце
  sum += fresh;                      // додати до суми
  idx = (idx + 1) % WIN;             // індекс по колу
  return (int)(sum / WIN);           // середнє = сума / кількість
}
