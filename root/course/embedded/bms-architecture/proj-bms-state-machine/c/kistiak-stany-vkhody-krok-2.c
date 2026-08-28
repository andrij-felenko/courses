// ── Виконавчі органи (кожна функція клацає одним контактором) ──
extern void contactor_neg(bool on);     // «мінусовий»
extern void contactor_pre(bool on);     // передзарядний (з резистором)
extern bool contactor_pre_is_on(void);  // чи передзарядний зараз замкнений
extern void contactor_main(bool on);    // головний «плюсовий»

// ── Виміри (повертають вольти; реалізація — АЦП за ізоляцією) ──
extern float read_u_pack(void);         // напруга пакета (бік батареї)
extern float read_u_load(void);         // напруга на навантаженні (бік ємності)

// ── Сигнали захисту (true = «небезпека, рубай») ──
extern bool  cell_protect_alarm(void);  // 1-ша лінія: монітор + МК
extern bool  secondary_alarm(void);     // 2-га лінія: незалежний вузол

// ── Допоміжні контакти (true = контактор НАСПРАВДІ замкнений) ──
extern bool  aux_main_closed(void);     // дзеркало реального стану головного

extern uint32_t now_ms(void);           // монотонний лічильник часу
extern void  set_fault_pin(bool on);    // апаратний вихід «BMS у відмові»

// ── Незалежна від живлення пам'ять: слід останньої відмови ──
extern fault_code_t nvm_read_last_fault(void);   // що було при минулому збої
extern void  nvm_clear_last_fault(void);         // стерти слід при скиданні
