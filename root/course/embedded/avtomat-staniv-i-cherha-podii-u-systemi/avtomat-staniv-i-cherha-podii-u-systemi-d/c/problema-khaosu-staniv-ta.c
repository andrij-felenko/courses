// Типовий приклад логіки на прапорцях: хаос умовних переходів
void process_telemetry(void) {
    if (is_connected && !is_low_power && !has_fault) {
        if (has_sensor_data) {
            send_packet();
            has_sensor_data = false;
        } else if (!is_measuring) {
            start_measurement();
            is_measuring = true;
        }
    } else if (has_fault && is_connected) {
        send_error_beacon();
        // Що робити, якщо під час відправки аварії зникне зв'язок?
    } else if (!is_connected && is_measuring) {
        // Небезпечний проміжний стан: зв'язок втрачено під час вимірювання
        abort_measurement();
        is_measuring = false;
    }
}
