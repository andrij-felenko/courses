// Упакована бінарна структура кадру (C99)
#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;       // 0xA5 — магічний байт початку кадру
    uint8_t  msg_type;    // 0x01 — тип повідомлення (телеметрія)
    uint16_t seq_num;     // Лічильник пакета для відстеження втрат
    uint32_t timestamp;   // Час вимірювання Unix time (4 байти)
    int16_t  temperature; // Температура, розрахована як T*100 (2 байти: від -327.68 до +327.67 °C)
    uint16_t humidity;    // Вологість, H*100 (2 байти: 0..100.00 %)
    uint16_t vbat_mv;     // Напруга батареї в мВ (2 байти: 0..65535 мВ)
    uint16_t crc16;       // Контрольна сума CRC-16-CCITT для перевірки цілісності
} sensor_packet_t;
#pragma pack(pop)
