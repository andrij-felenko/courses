// Еквівалент на C++: та сама комбінаторна крихкість умовних конструкцій
void process_telemetry() {
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
    } else if (!is_connected && is_measuring) {
        abort_measurement();
        is_measuring = false;
    }
}
