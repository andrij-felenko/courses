#include "esp_partition.h"   // ESP-IDF: доступ до розділу за типом/іменем

// Розділ даних оголошено в таблиці розділів під цим іменем (див. partitions.csv).
#define PROV_PARTITION_LABEL  "prov"

// Кеш прочитаного запису + прапорець «валідний». Заповнюється раз, у prov_init().
static prov_record_t s_record;
static bool          s_valid = false;

// Прочитати розділ, провалідувати трьома перевірками. Викликати ОДИН раз на старті.
// Повертає true, якщо запис на місці, нашої версії й цілий (CRC збіглася).
bool prov_init(void) {
    s_valid = false;

    // 1. Знайти розділ даних у таблиці розділів за іменем.
    const esp_partition_t *part = esp_partition_find_first(
        ESP_PARTITION_TYPE_DATA, ESP_PARTITION_SUBTYPE_ANY, PROV_PARTITION_LABEL);
    if (part == NULL)
        return false;               // розділу нема в таблиці — нема чого читати

    // 2. Прочитати перші sizeof(запис) байтів розділу в структуру.
    if (esp_partition_read(part, 0, &s_record, sizeof(s_record)) != ESP_OK)
        return false;               // помилка читання Flash

    // 3. ВАРТОВИЙ ПЕРШИЙ — магічне число. Стерта (0xFFFFFFFF) чи чужа область впаде тут.
    if (s_record.magic != PROV_MAGIC)
        return false;

    // 4. Версія формату — читаємо лише те, що вміємо прочитати.
    if (s_record.version != PROV_VERSION)
        return false;               // майбутній/чужий формат — краще визнати недійсним

    // 5. ВАРТОВИЙ ДРУГИЙ — CRC. Рахуємо з усього тіла, КРІМ самого поля crc32.
    //    Тіло = вся структура без останніх 4 байтів (розмір поля crc32).
    size_t body_len = sizeof(prov_record_t) - sizeof(s_record.crc32);
    uint32_t want = crc32_iso((const uint8_t *)&s_record, body_len);
    if (want != s_record.crc32)
        return false;               // напівзаписаний або побитий запис — не збіглося

    s_valid = true;                 // усі три перевірки пройшли — запис справжній
    return true;
}

// Чесна відповідь для решти прошивки: чи можна довіряти своїй особистості.
bool is_provisioned(void) {
    return s_valid;
}
