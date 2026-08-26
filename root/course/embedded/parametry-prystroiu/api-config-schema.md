# 📋 Контракт та API конфігураційного сховища

Цей документ визначає формальний бінарний контракт, структуру дескрипторів, протокол валідації та інтерфейси функцій конфігураційного рушія для вбудованих систем реального часу. Контракт єдиним чином стандартизує збереження налаштувань в енергонезалежній Flash-пам'яті, гарантує захист від пошкодження даних при раптовому знеструмленні (Power-Cut Safety), унеможливлює введення деструктивних параметрів і регламентує роботу випробувального режиму (Trial Run) з детермінованою міграцією версій схеми.

---

### 1. Бінарна анатомія та специфікація сектора Flash

Для збереження параметрів конфігурації у зовнішній або внутрішній Flash-пам'яті мікроконтролера резервується виділена область, розбита щонайменше на два симетричні сектори однакового розміру (Slot A та Slot B). Кожен сектор починається з уніфікованого 24-байтового службового заголовка (`cfg_header_t`), вирівняного за 4-байтовою межею для запобігання апаратної помилки `UsageFault` (Unaligned Access) на процесорних ядрах ARM Cortex-M0/M0+.

Безпосередньо за заголовком розташовується суцільний блок корисного навантаження (Payload), що містить актуальні значення параметрів, упаковані згідно з поточною версією схеми.

```
  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                  Magic Bytes (0x43464731 "CFG1")              |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |         Schema Version        |          Header Flags         |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                        Sequence Number                        |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |         Payload Length        |           Reserved            |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                        Payload CRC-32                         |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                   Configuration Payload Data                  |
 |                              ...                              |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Детальний опис полів заголовка та їхнє функціональне призначення:

1. **`magic` (4 байти, зсув `0x00`)**: Магічна послідовність байтів `0x43464731` (ASCII-рядок `"CFG1"` у прямому порядку байтів Little-Endian). Дозволяє завантажувачу миттєво відрізнити стертий сектор (`0xFFFFFFFF`), занулену область (`0x00000000`) або чужі дані від валідного блоку налаштувань.
2. **`schema_version` (2 байти, зсув `0x04`)**: Монотонний числовий номер схеми даних, скомпільованої в поточній прошивці. Початкова ревізія має значення `1`. При кожній модифікації структури параметрів у вихідному коді значення інкрементується на одиницю.
3. **`header_flags` (2 байти, зсув `0x06`)**: Системні прапорці стану сектора. Прапорець `0x0001` (`FLAG_TRIAL_PENDING`) сигналізує, що сектор містить експериментальну конфігурацію, яка ще не пройшла мережеве підтвердження. Прапорець `0x0002` (`FLAG_FACTORY_LOCKED`) забороняє стирання сектора стандартними командами користувацького інтерфейсу.
4. **`sequence_number` (4 байти, зсув `0x08`)**: Лічильник поколінь оновлення. При кожному успішному перезаписі значення збільшується на одиницю (`seq_new = seq_old + 1`). Порівняння лічильників реалізується через знакову різницю `(int32_t)(seq_a - seq_b) > 0`, що гарантує коректний вибір новішого сектора навіть після переповнення 32-бітного беззнакового числа через 4.29 мільярда ітерацій.
5. **`payload_len` (2 байти, зсув `0x0C`)**: Точний розмір корисного навантаження у байтах без урахування заголовка. Запобігає читанню неініціалізованого залишку сектора Flash.
6. **`reserved` (2 байти, зсув `0x0E`)**: Резервні байти для збереження 4-байтового вирівнювання структури. За замовчуванням заповнюються нулями.
7. **`crc32` (4 байти, зсув `0x10`)**: Контрольна сума корисного навантаження, обчислена за стандартом IEEE 802.3 (поліном `0xEDB88320`, початкове значення `0xFFFFFFFF`, фінальна інверсія бітів). Заголовок вважається дійсним лише тоді, коли апаратний або програмний розрахунок контрольної суми над областю `Payload` довжиною `payload_len` байтів повністю збігається зі значенням цього поля.

Усі поля багатобайтових чисел (цілі та дійсні числа, магічні значення та контрольні суми) строго зберігаються у форматі Little-Endian, що відповідає нативній розкладці пам'яті більшості сучасних мікроконтролерних архітектур (ARM Cortex-M, RISC-V, Xtensa).

---

### 2. Типізація параметрів та метадані дескрипторів

Кожен окремий параметр конфігурації однозначно описується константним дескриптором `cfg_descriptor_t`. Масив таких дескрипторів розміщується у Flash-пам'яті програми (`.rodata`) і формує незмінний словник параметрів пристрою.

При проєктуванні дескрипторів дотримуються наступних архітектурних гарантій:
- **Нульове динамічне виділення пам'яті**: робота з параметрами не викликає `malloc()` або `free()`, унеможливлюючи фрагментацію купи;
- **Контроль вирівнювання (Alignment)**: кожне 32-бітне число розміщується за адресою, кратною 4 байтам, що забезпечує максимальну швидкодію шини пам'яті;
- **Ізоляція секретів (Zeroization)**: змінні з прапорцем `CFG_FLAG_CONFIDENTIAL` після використання або при скиданні очищуються захищеною функцією обнулення (наприклад, `explicit_bzero` або `volatile memset`), щоб виключити витік ключів шифрування через залишковий стан оперативної пам'яті.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CONFIG_MAGIC 0x43464731UL /* "CFG1" в ASCII */

typedef enum {
    CONFIG_TYPE_BOOL   = 0x01, /* 1 байт: 0 або 1 */
    CONFIG_TYPE_INT32  = 0x02, /* 4 байти: знакове ціле */
    CONFIG_TYPE_UINT32 = 0x03, /* 4 байти: беззнакове ціле */
    CONFIG_TYPE_FLOAT  = 0x04, /* 4 байти: число з рухомою комою IEEE 754 */
    CONFIG_TYPE_STRING = 0x05, /* Фіксований масив char із нуль-термінатором */
    CONFIG_TYPE_BLOB   = 0x06  /* Бінарний масив довільних байтів */
} cfg_type_t;

typedef enum {
    CFG_FLAG_NONE         = 0x0000,
    CFG_FLAG_READ_ONLY    = 0x0001, /* Заборона модифікації користувачем (заводські дані) */
    CFG_FLAG_REBOOT_REQ   = 0x0002, /* Зміна набуває чинності лише після повного рестарту */
    CFG_FLAG_CONFIDENTIAL = 0x0004, /* Чутливий ключ/пароль: маскувати під час виводу в лог */
    CFG_FLAG_VOLATILE     = 0x0008, /* Тимчасовий параметр: тримати в RAM, не писати у Flash */
    CFG_FLAG_TRIAL_CRIT   = 0x0010  /* Критичний мережевий параметр: вимагає Trial Run */
} cfg_param_flags_t;

typedef enum {
    CFG_OK                   =  0, /* Успішне виконання */
    CFG_ERR_INVALID_MAGIC    = -1, /* Помилка магічних байтів сектора */
    CFG_ERR_CRC_MISMATCH     = -2, /* Порушення контрольної суми даних */
    CFG_ERR_VERSION_GAP      = -3, /* Несумісна версія схеми без функції міграції */
    CFG_ERR_OUT_OF_RANGE     = -4, /* Значення параметра виходить за межі [min, max] */
    CFG_ERR_READ_ONLY        = -5, /* Спроба запису в параметр із прапорцем READ_ONLY */
    CFG_ERR_NOT_FOUND        = -6, /* Запитаний Key ID відсутній у словнику дескрипторів */
    CFG_ERR_BUFFER_TOO_SMALL = -7, /* Буфер приймача замалий для рядка чи блоба */
    CFG_ERR_FLASH_WRITE      = -8, /* Апаратна помилка шини SPI / контролера Flash */
    CFG_ERR_TRIAL_ACTIVE     = -9, /* Спроба запустити нове випробування під час активного Trial */
    CFG_ERR_DEPENDENCY       = -10 /* Порушення крос-параметричних правил узгодженості */
} cfg_status_t;

typedef struct {
    uint32_t magic;
    uint16_t schema_version;
    uint16_t flags;
    uint32_t sequence_number;
    uint16_t payload_len;
    uint16_t reserved;
    uint32_t crc32;
} __attribute__((packed)) cfg_header_t;

typedef struct {
    uint16_t key_id;                      /* Унікальний числовий ідентифікатор параметра */
    const char *key_name;                 /* Текстове ім'я для CLI та зовнішніх протоколів */
    cfg_type_t type;                      /* Фізичний тип даних */
    uint16_t offset_in_struct;            /* Зсув поля від початку структури корисного навантаження */
    uint16_t size_bytes;                  /* Розмір поля у байтах */
    uint16_t flags;                       /* Бітова маска прав доступу та поведінки */
    int64_t  min_int;                     /* Мінімальна допустима межа цілого числа */
    int64_t  max_int;                     /* Максимальна допустима межа цілого числа */
    float    min_float;                   /* Нижня межа для чисел із рухомою комою */
    float    max_float;                   /* Верхня межа для чисел із рухомою комою */
    const void *default_value_ptr;        /* Вказівник на типове заводське значення у ROM */
    cfg_status_t (*custom_validator)(const void *val_ptr); /* Додатковий функціональний валідатор */
} cfg_descriptor_t;
```
```cpp
#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <expected>
#include <optional>
#include <type_traits>

namespace embedded::config {

inline constexpr std::uint32_t ConfigMagic = 0x43464731U;

enum class Type : std::uint8_t {
    Bool   = 0x01,
    Int32  = 0x02,
    Uint32 = 0x03,
    Float  = 0x04,
    String = 0x05,
    Blob   = 0x06
};

enum class Flags : std::uint16_t {
    None         = 0x0000,
    ReadOnly     = 0x0001,
    RebootReq    = 0x0002,
    Confidential = 0x0004,
    Volatile     = 0x0008,
    TrialCrit    = 0x0010
};

constexpr Flags operator|(Flags a, Flags b) noexcept {
    return static_cast<Flags>(static_cast<std::uint16_t>(a) | static_cast<std::uint16_t>(b));
}

constexpr bool operator&(Flags a, Flags b) noexcept {
    return (static_cast<std::uint16_t>(a) & static_cast<std::uint16_t>(b)) != 0;
}

enum class Error : std::int8_t {
    InvalidMagic    = -1,
    CrcMismatch     = -2,
    VersionGap      = -3,
    OutOfRange      = -4,
    ReadOnly        = -5,
    NotFound        = -6,
    BufferTooSmall  = -7,
    FlashWriteFault = -8,
    TrialActive     = -9,
    DependencyFault = -10
};

struct [[gnu::packed]] Header {
    std::uint32_t magic;
    std::uint16_t schema_version;
    std::uint16_t flags;
    std::uint32_t sequence_number;
    std::uint16_t payload_len;
    std::uint16_t reserved;
    std::uint32_t crc32;
};

template <typename T>
struct ParameterDescriptor {
    std::uint16_t key_id;
    std::string_view key_name;
    Type type;
    std::size_t offset_in_struct;
    Flags flags;
    T min_value;
    T max_value;
    T default_value;
    bool (*custom_validator)(const T &val) noexcept = nullptr;
};

} // namespace embedded::config
```
:::

---

### 3. Специфікація функцій конфігураційного рушія

Керування життєвим циклом параметрів реалізується через набір процедур з детермінованим часом виконання та передбачуваним використанням пам'яті. Усі функції є реентерабельними щодо читання та потокобезпечними.

Звернення до функцій запису під час виконання обробників переривань (ISR context) суворо заборонено, оскільки операції стирання та програмування Flash-пам'яті блокують шину на час до кількох десятків мілісекунд. У середовищі FreeRTOS/Zephyr функції запису захищаються взаємним виключенням (Mutex) з пріоритетним успадкуванням.

:::tabs
```c
/**
 * @brief Повна ініціалізація конфігураційного сховища при старті ядра.
 * 
 * Послідовність дій:
 * 1. Читає службові заголовки Slot A та Slot B;
 * 2. Перевіряє магічні байти та цілісність контрольних сум CRC-32;
 * 3. Обирає сектор із найбільшим значенням sequence_number;
 * 4. Якщо версія схеми у Flash старіша за CURRENT_SCHEMA_VER, викликає ланцюжок міграторів;
 * 5. Якщо жоден сектор не є валідним — завантажує заводські дефолти у RAM та ініціалізує Flash;
 * 6. Копіює активний стан у захищену RAM-структуру g_active_config.
 * 
 * @return CFG_OK у разі успіху або відповідний код помилки CFG_ERR_*.
 */
cfg_status_t cfg_manager_init(void);

/**
 * @brief Читання значення цілочисельного параметра за числовим ключем.
 * 
 * @param key_id  Ідентифікатор параметра з таблиці дескрипторів.
 * @param out_val Вказівник на змінну для запису результату.
 * @return CFG_OK або CFG_ERR_NOT_FOUND, якщо ідентифікатор не зареєстрований.
 */
cfg_status_t cfg_get_uint32(uint16_t key_id, uint32_t *out_val);

/**
 * @brief Читання рядкового параметра у виділений користувацький буфер.
 * 
 * @param key_id  Ідентифікатор параметра.
 * @param out_buf Вказівник на цільовий масив символів.
 * @param buf_len Розмір буфера (зобов'язаний вміщувати рядок разом із нуль-термінатором).
 * @return CFG_OK або CFG_ERR_BUFFER_TOO_SMALL.
 */
cfg_status_t cfg_get_string(uint16_t key_id, char *out_buf, size_t buf_len);

/**
 * @brief Попередня валідація кандидата конфігурації без застосування.
 * 
 * Виконує повний прохід по словнику дескрипторів, перевіряє межі кожного поля,
 * контролює спроби перезапису Read-Only параметрів та виконує матрицю
 * крос-параметричних правил узгодженості.
 * 
 * @param candidate_payload Вказівник на буфер з новою структурою параметрів.
 * @param len               Розмір буфера у байтах.
 * @return CFG_OK або код виявленого порушення валідації.
 */
cfg_status_t cfg_validate_candidate(const void *candidate_payload, size_t len);

/**
 * @brief Активація випробувального режиму (Trial Run).
 * 
 * Зберігає кандидата у випробувальний буфер оперативної пам'яті, запускає
 * незалежний таймер випробувального терміну (тривалістю trial_timeout_s)
 * та перемикає робочі покажчики підсистем на нові параметри.
 * 
 * @param candidate_payload Буфер перевіреного кандидата.
 * @param len               Розмір буфера.
 * @param trial_timeout_s   Час очікування підтвердження зв'язку в секундах (зазвичай 60 с).
 * @return CFG_OK або CFG_ERR_TRIAL_ACTIVE, якщо попередній Trial ще не завершено.
 */
cfg_status_t cfg_apply_trial(const void *candidate_payload, size_t len, uint32_t trial_timeout_s);

/**
 * @brief Атомарна фіксація випробуваної конфігурації (Commit).
 * 
 * Викликається після успішного мережевого рукостискання (TLS/MQTT Handshake).
 * Атомарно записує кандидата у вільний сектор Flash Ping-Pong із новим номером
 * генерації sequence_number, скидає прапорець Trial та зупиняє захисний таймер.
 * 
 * @return CFG_OK або CFG_ERR_FLASH_WRITE.
 */
cfg_status_t cfg_confirm_commit(void);

/**
 * @brief Аварійний відкат до попередньої стабільної конфігурації (Rollback).
 * 
 * Миттєво відкидає кандидата з RAM, відновлює активний робочий профіль
 * із гарантовано цілісного слота Flash та ініціює перезапуск мережевого стека.
 * 
 * @return CFG_OK.
 */
cfg_status_t cfg_abort_rollback(void);

/**
 * @brief Тип покажчика на функцію покрокової міграції між версіями схеми.
 */
typedef cfg_status_t (*cfg_migrator_fn)(const void *old_payload, size_t old_len,
                                        void *new_payload, size_t new_len);

/**
 * @brief Реєстрація функції міграції між версіями from_ver та to_ver.
 */
cfg_status_t cfg_register_migrator(uint16_t from_ver, uint16_t to_ver, cfg_migrator_fn migrator);
```
```cpp
namespace embedded::config {

class IConfigurationManager {
public:
    virtual ~IConfigurationManager() = default;

    virtual std::expected<void, Error> initialize() noexcept = 0;

    virtual std::expected<std::uint32_t, Error> get_uint32(std::uint16_t key_id) const noexcept = 0;
    virtual std::expected<std::string_view, Error> get_string(std::uint16_t key_id, std::span<char> buf) const noexcept = 0;

    virtual std::expected<void, Error> validate_candidate(std::span<const std::uint8_t> payload) const noexcept = 0;

    virtual std::expected<void, Error> apply_trial(std::span<const std::uint8_t> candidate_payload,
                                                   std::uint32_t trial_timeout_s) noexcept = 0;

    virtual std::expected<void, Error> confirm_commit() noexcept = 0;
    virtual std::expected<void, Error> abort_rollback() noexcept = 0;

    using MigratorFunction = bool (*)(std::span<const std::uint8_t> old_data,
                                     std::span<std::uint8_t> new_data) noexcept;

    virtual std::expected<void, Error> register_migrator(std::uint16_t from_version,
                                                         std::uint16_t to_version,
                                                         MigratorFunction migrator) noexcept = 0;
};

} // namespace embedded::config
```
:::

---

### 4. Матриця крос-параметричної валідації

Поодинока перевірка кожного параметра на відповідність діапазону `[min, max]` є необхідною, але недостатньою умовою надійності. Вбудована система містить тісно пов'язані апаратні та протокольні підсистеми, де некоректна комбінація двох індивідуально допустимих чисел викликає апаратний клінч або циклічні перезавантаження модема.

Менеджер конфігурації виконує перевірку за системною матрицею предикатів другого рівня:

| Набір параметрів | Предикат валідності | Наслідок порушення правила |
| :--- | :--- | :--- |
| `telemetry_interval_s`, `conn_timeout_s` | `telemetry_interval_s <= (conn_timeout_s / 2)` | Якщо таймаут менший за подвійний період звітування, будь-яка затримка доставки кадру в стільниковій мережі викличе хибне спрацювання сторожового таймера та обрив активної TCP-сесії. |
| `wifi_mode`, `channel` | `(wifi_mode != STA_ONLY) \|\| (channel >= 1 && channel <= 13)` | Запит каналу 14 у європейському регіоні або некоректного діапазону в режимі клієнта викликає відмову радіотракту на етапі сканування ефіру. |
| `mqtt_tls_enable`, `mqtt_port` | `(!mqtt_tls_enable && mqtt_port == 1883) \|\| (mqtt_tls_enable && mqtt_port == 8883)` | Спроба ініціалізації TLS-рукостискання на відкритому стандартному порту 1883 зависає на етапі очікування сертифіката сервера до вичерпання системного таймауту. |
| `dhcp_enabled`, `static_ip`, `gateway_ip` | `dhcp_enabled \|\| (static_ip != 0 && gateway_ip != 0 && (static_ip & subnet) == (gateway_ip & subnet))` | Якщо статична IP-адреса вузла не належить підмережі шлюзу за замовчуванням, маршрутизатор відкидає пакети як немаршрутизовані, і пристрій втрачає вихід у зовнішню мережу. |
| `tx_power_dbm`, `battery_type` | `battery_type != CR2032 \|\| tx_power_dbm <= 4` | Встановлення максимальної потужності передавача +20 dBm при живленні від мініатюрного дискового елемента CR2032 викликає імпульсний струм споживання понад 120 мА, що миттєво просаджує внутрішній опір батарейки нижче напруги вимкнення BOR (Brownout Reset). |

---

### 5. Контракт апаратного рівня доступу до Flash (HAL Interface)

Для забезпечення портативності між різними мікроконтролерами (STM32, ESP32, nRF52, RP2040) менеджер конфігурації не містить прямих звернень до регістрів периферії. Уся взаємодія з пам'яттю реалізується через стандартизовану структуру низькорівневих драйверів Flash HAL.

:::tabs
```c
typedef struct {
    uint32_t slot_a_base_addr; /* Фізична адреса першого сектора у мапі пам'яті */
    uint32_t slot_b_base_addr; /* Фізична адреса другого сектора у мапі пам'яті */
    uint32_t sector_size;      /* Розмір сектора стирання (зазвичай 4096 байтів) */
    
    bool (*flash_erase_sector)(uint32_t sector_addr);
    bool (*flash_write_page)(uint32_t dest_addr, const uint8_t *src_buf, size_t len);
    bool (*flash_read_data)(uint32_t src_addr, uint8_t *dest_buf, size_t len);
} cfg_flash_hal_t;
```
```cpp
namespace embedded::config {

struct FlashHal {
    std::uint32_t slot_a_base_addr;
    std::uint32_t slot_b_base_addr;
    std::uint32_t sector_size;

    bool (*flash_erase_sector)(std::uint32_t sector_addr) noexcept = nullptr;
    bool (*flash_write_page)(std::uint32_t dest_addr, std::span<const std::uint8_t> src) noexcept = nullptr;
    bool (*flash_read_data)(std::uint32_t src_addr, std::span<std::uint8_t> dest) noexcept = nullptr;
};

} // namespace embedded::config
```
:::

Вимоги до реалізації драйвера Flash HAL:
1. Функція `flash_erase_sector` зобов'язана виконувати перевірку стану завершення операції (Busy bit у регістрі статусу SPI Flash) та блокувати виконання на час не більше 100 мс.
2. Функція `flash_write_page` повинна підтримувати посторінковий запис блоками по 256 байтів без виходу за межу поточної фізичної сторінки чіпа.
3. Перед записом драйвер зобов'язаний переконатися, що цільова область стерта (містить байти `0xFF`), щоб уникнути паразитного накладання нульових бітів.
