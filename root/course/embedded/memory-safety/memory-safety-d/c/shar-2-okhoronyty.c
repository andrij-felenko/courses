// Канарка дна стека: відоме число, яке перевіряємо на цілість
#define CANARY 0xDEADBEEFu
extern uint32_t _stack_bottom;      // символ із лінкер-скрипта: дно стека

void canary_install(void) {
    _stack_bottom = CANARY;         // ставимо мітку один раз при старті
}

void canary_check(void) {           // кличемо періодично (напр., у idle-таску)
    if (_stack_bottom != CANARY) {  // мітку затерто — стек заліз сюди
        // стек переповнився: фіксуємо й перезапускаємось контрольовано
        log_fatal("stack overflow");
        esp_restart();
    }
}
