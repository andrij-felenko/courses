struct Reading {
    float    celsius;
    uint16_t raw;
    uint32_t timestamp;
    uint8_t  sensorId;
    uint8_t  crc;
    int8_t   rssi;       // сила сигналу, якщо давач бездротовий
    // …структура росте, її чіпають з десятка причин
};

// Зчеплення за зліпком: бере всю структуру, використовує ДВА поля
float applyCalibration(const Reading& r, const CalTable& tbl) {
    float offset = tbl.lookup(r.sensorId);   // потрібне поле 1
    return r.celsius + offset;               // потрібне поле 2
    // решта Reading тут не використана — але функція від неї залежить
}
