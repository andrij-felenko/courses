void process_telemetry(void) {
    uint32_t raw_adc_data[16];
    read_adc(raw_adc_data);
    // Масив raw_adc_data заповнює 64 байти стека значеннями 0x0FFF...
}

void transmit_packet(void) {
    uint32_t packet_flags; // Неініціалізована змінна
    // Вона лягає на те саме місце стека, де щойно лежав raw_adc_data[0]!
    // packet_flags автоматично стає рівним 0x00000FFF замість 0!
    if (packet_flags & 0x01) {
        send_error_beacon();
    }
}

void task_loop(void) {
    process_telemetry();
    transmit_packet();
}
