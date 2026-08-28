#define DHT_PORT  GPIOA
#define DHT_PIN   GPIO_PIN_1

// Перемкнути ніжку у вихід (push-pull) або у вхід.
static void dht_output(void) {
    GPIO_InitTypeDef g = {0};
    g.Pin = DHT_PIN;  g.Mode = GPIO_MODE_OUTPUT_PP;
    g.Pull = GPIO_NOPULL;  g.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(DHT_PORT, &g);
}
static void dht_input(void) {
    GPIO_InitTypeDef g = {0};
    g.Pin = DHT_PIN;  g.Mode = GPIO_MODE_INPUT;
    g.Pull = GPIO_PULLUP;   // внутрішня підтяжка (зовнішній резистор усе одно бажаний)
    HAL_GPIO_Init(DHT_PORT, &g);
}

static inline int dht_get(void) {   // прочитати рівень лінії: 1 або 0
    return HAL_GPIO_ReadPin(DHT_PORT, DHT_PIN) == GPIO_PIN_SET;
}

// Чекати рівень level не довше timeout мкс; 1 — дочекалися, 0 — вийшов час.
static int wait_level(int level, uint32_t timeout) {
    uint32_t start = micros();
    while (dht_get() != level) {
        if ((uint32_t)(micros() - start) > timeout) return 0;
    }
    return 1;
}

// Читання. Повертає 1 при успіху; результат — у *temp, *hum.
int dht11_read(int *temp, int *hum) {
    uint8_t bytes[5] = {0, 0, 0, 0, 0};

    // ── Фаза 1: стартовий імпульс ──
    dht_output();
    HAL_GPIO_WritePin(DHT_PORT, DHT_PIN, GPIO_PIN_RESET); // притиснули низько
    HAL_Delay(20);                                        // ≥ 18 мс (мілісекунди!)
    HAL_GPIO_WritePin(DHT_PORT, DHT_PIN, GPIO_PIN_SET);   // відпустили
    delay_us(30);                                         // 20–40 мкс
    dht_input();                                          // віддали лінію давачу

    // ── Фаза 2: відповідь давача (80 мкс низько + 80 мкс високо) ──
    if (!wait_level(0, 100)) return 0;
    if (!wait_level(1, 100)) return 0;
    if (!wait_level(0, 100)) return 0;

    // ── Фаза 3: 40 бітів ──
    for (int i = 0; i < 40; i++) {
        if (!wait_level(1, 100)) return 0;   // пропустили 50 мкс низько
        uint32_t t0 = micros();
        if (!wait_level(0, 100)) return 0;   // дочекалися фронту вниз
        uint32_t width = micros() - t0;      // ширина високого імпульсу

        bytes[i / 8] <<= 1;
        if (width > 50) bytes[i / 8] |= 1;   // довгий → 1
    }

    // ── Фаза 4: контрольна сума ──
    if ((uint8_t)(bytes[0] + bytes[1] + bytes[2] + bytes[3]) != bytes[4])
        return 0;

    *hum  = bytes[0];
    *temp = bytes[2];
    return 1;
}
