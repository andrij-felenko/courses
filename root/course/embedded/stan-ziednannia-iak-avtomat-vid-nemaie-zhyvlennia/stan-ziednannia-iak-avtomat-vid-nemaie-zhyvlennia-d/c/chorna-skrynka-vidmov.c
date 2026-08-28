typedef struct {
    uint32_t timestamp_ms;    // Системний час моменту переходу
    uint8_t  from_state;      // Початковий стан
    uint8_t  to_state;        // Новий стан
    uint8_t  event_id;        // Подія, що викликала перехід
    uint8_t  retry_count;     // Поточний лічильник спроб
    int8_t   rssi_dbm;        // Рівень сигналу в момент події (дБм)
    uint16_t cme_error_code;  // Останній числовий код CME/CMS ERROR
    uint16_t voltage_vbat_mv; // Напруга живлення (мілівольти)
    uint8_t  reserved[2];     // Вирівнювання структури до 16 байтів
} fsm_transition_log_t;
