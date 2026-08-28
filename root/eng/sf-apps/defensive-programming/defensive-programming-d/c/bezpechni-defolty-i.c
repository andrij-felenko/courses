// поганий «дефолт»: лишаємо як є → невизначений бік відмови
relay_state_t state;            // сміття у стеку
if (read_config(&state) == ESP_OK) { /* ... */ }
apply(state);                   // застосували сміття

// безпечний дефолт: спершу обережне значення, тоді спроба уточнити
relay_state_t state = RELAY_OPEN;   // знеструмлено — безпечний бік
if (read_config(&state) != ESP_OK)
    ESP_LOGW(TAG, "config read failed; staying fail-safe");
apply(state);                       // навіть при збої — у безпеці
