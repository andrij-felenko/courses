// Небезпечно при агресивному inlining:
void process_step_a(void) {
    uint8_t temp_buf[256];
    // Обробка...
}

void process_step_b(void) {
    uint8_t temp_buf[256];
    // Обробка...
}

void vTaskWorker(void *pvParameters) {
    while (1) {
        // У Debug: стек потрібен лише на 256 байтів (почергово)
        // У Release (-O3): компілятор вбудовує обидві функції, і кадр вимагає >512 байтів!
        process_step_a();
        process_step_b();
    }
}
