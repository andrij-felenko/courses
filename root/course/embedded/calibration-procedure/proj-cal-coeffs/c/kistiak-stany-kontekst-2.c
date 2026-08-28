// ── Сирий канал давача (один відлік 24-біт коду) ──
extern int32_t  sensor_read_raw(void);

// ── Команди оператора (фронт — true рівно один раз на натискання) ──
extern bool  op_pressed_capture(void);   // «зняти цю опору»
extern bool  op_pressed_abort(void);     // «скасувати калібрування»

// ── Зворотний зв'язок операторові (дисплей/світлодіоди) ──
extern void  ui_prompt(const char *msg); // показати, що робити зараз
extern void  ui_progress(uint32_t done, uint32_t total); // хід усереднення

extern uint32_t now_ms(void);            // монотонний лічильник часу

// ── Енергонезалежне сховище (реалізація — поверх NVS/EEPROM/FRAM) ──
//    Повертають true при успіху. Деталі — у розділі про атомарний запис.
extern bool  cal_store_write(const cal_t *c);  // записати коефіцієнти атомарно
extern bool  cal_store_read(cal_t *out);       // підняти; false якщо нема/побито
