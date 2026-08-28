#define DHT_PIN 2                 // ніжка з лінією DATA

// Повертає true, якщо читання вдалося; кладе результат у temp/hum.
bool dht11_read(int *temp, int *hum) {
    uint8_t bytes[5] = {0, 0, 0, 0, 0};

    // ── Фаза 1: стартовий імпульс від хоста ──
    pinMode(DHT_PIN, OUTPUT);
    digitalWrite(DHT_PIN, LOW);   // притискаємо лінію до землі
    delay(20);                    // ≥ 18 мс — будимо давача (беремо 20 із запасом)
    digitalWrite(DHT_PIN, HIGH);  // коротко відпускаємо
    delayMicroseconds(30);        // 20–40 мкс, поки давач «прокидається»
    pinMode(DHT_PIN, INPUT_PULLUP); // віддаємо лінію: тепер говорить давач

    // ── Фаза 2: чекаємо відповідь давача (80 мкс низько + 80 мкс високо) ──
    if (!wait_level(LOW,  100)) return false;  // давач притиснув лінію
    if (!wait_level(HIGH, 100)) return false;  // давач відпустив (80 мкс низько)
    if (!wait_level(LOW,  100)) return false;  // кінець 80 мкс високо — старт даних

    // ── Фаза 3: 40 бітів, значення = ширина високого імпульсу ──
    for (int i = 0; i < 40; i++) {
        if (!wait_level(HIGH, 100)) return false;  // пропускаємо 50 мкс низько
        uint32_t t0 = micros();                    // фронт угору — засікли час
        if (!wait_level(LOW, 100)) return false;   // чекаємо фронт униз
        uint32_t width = micros() - t0;            // ширина високого імпульсу

        // ширина ~26 мкс → 0, ~70 мкс → 1; поріг посередині (~50 мкс)
        bytes[i / 8] <<= 1;                         // звільняємо місце під новий біт
        if (width > 50) bytes[i / 8] |= 1;          // довгий імпульс → одиниця
    }

    // ── Фаза 4: контрольна сума ──
    uint8_t sum = bytes[0] + bytes[1] + bytes[2] + bytes[3];
    if (sum != bytes[4]) return false;             // не збіглося — читання зіпсоване

    *hum  = bytes[0];   // ціла частина вологості (байт 2 у DHT11 завжди 0)
    *temp = bytes[2];   // ціла частина температури (байт 4 завжди 0)
    return true;
}
