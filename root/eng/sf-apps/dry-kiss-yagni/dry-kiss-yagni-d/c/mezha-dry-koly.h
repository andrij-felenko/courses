// Крок 1: чесне DRY. Два формати кадру мали спільний конверт — винесли.
void send_frame(const uint8_t *payload, size_t len);

// Крок 2: третій формат майже такий самий, але з CRC. Додаємо прапорець.
void send_frame(const uint8_t *payload, size_t len, bool with_crc);

// Крок 3: четвертий — ще й зі стисненням. Ще прапорець.
void send_frame(const uint8_t *payload, size_t len, bool with_crc, bool compress);

// Крок 4: п'ятий формат вимагає порядку байтів навпаки...
void send_frame(const uint8_t *payload, size_t len,
                bool with_crc, bool compress, bool big_endian);
// Тіло — вкладені if на кожну комбінацію. Ніхто вже не знає, які комбінації валідні.
