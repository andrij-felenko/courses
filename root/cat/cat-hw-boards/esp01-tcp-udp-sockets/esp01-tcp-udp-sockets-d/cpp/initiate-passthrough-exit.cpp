enum EscapeState { IDLE, WAITING_PRE_GUARD, ESCAPE_SENT, WAITING_POST_GUARD };
EscapeState escape_state = IDLE;
uint32_t guard_timer = 0;

void initiate_passthrough_exit() {
    // Етап 1: Зупиняємо передачу даних та запускаємо таймер тиші на 1000 мс
    escape_state = WAITING_PRE_GUARD;
    guard_timer = millis();
}

void process_escape_sequence_fsm() {
    uint32_t now = millis();
    
    switch (escape_state) {
        case WAITING_PRE_GUARD:
            // Перевіряємо витримування 1000 мс повного мовчання лінії UART
            if (now - guard_timer >= 1000) {
                // Етап 2: Відправляємо рівно три символи плюса без символів переводу рядка
                Serial.print("+++");
                guard_timer = now;
                escape_state = WAITING_POST_GUARD;
            }
            break;
            
        case WAITING_POST_GUARD:
            // Витримуємо 1000 мс тиші після відправки перед викликом нових AT-команд
            if (now - guard_timer >= 1000) {
                escape_state = IDLE;
                // Модуль відновив командний інтерпретатор і готовий приймати AT+CIPCLOSE
            }
            break;

        case IDLE:
        default:
            break;
    }
}
