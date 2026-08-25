# ⚙️ Розбір рекламних пакетів та налаштування GAP у коді

Безпечний розбір двійкових структур Advertising Data (AD Data) та формування запитів узгодження параметрів з'єднання на канальному рівні є критичною частиною будь-якого вбудованого BLE-застосунку. Некоректна робота з сирими байтовими буферами в радіоефірі призводить до виходу за межі виділеної пам'яті (Buffer Overflow), асинхронних збоїв шини через непарне вирівнювання покажчиків (*Unaligned Memory Access*) або зависання підсистеми радіозв'язку в мікроконтролері.

Низькорівневий стек радіомодуля повертає розробнику лише плаский масив байтів, отриманий безпосередньо з радіоефіру. Прошивка мікроконтролера повинна самостійно перевірити цілісність отриманого кадру, виділити корисні поля, відкинути сміття, санітизувати рядки, агрегувати асинхронні відповіді, діагностувати причини розривів та коректно налаштувати таймінги взаємодії.

Нижче наведено аналіз типових апаратних пасток, алгоритми безпечного потокового розбору структур TLV (*Type-Length-Value*), видобування специфічних даних виробника, генератор рекламних кадрів з автоматичним розділенням даних, механіку агрегації звітів сканування, вимоги операційних систем до таймінгів, простеження через події інтерфейсу HCI, коди завершення зв'язку та процедуру оновлення параметрів мовами C та C++.

---

### Апаратні пастки: вирівнювання пам'яті та безпека буферів

Перед написанням коду розбору необхідно враховувати специфіку архітектури мікроконтролерів (зокрема лінійок ARM Cortex-M та ESP32). Прийом рекламних пакетів пов'язаний з двома серйозними ризиками, які часто спричиняють випадкові збої пристроїв у польових умовах:

#### 1. Збій непарного вирівнювання покажчиків (Unaligned Access Fault)

У структурах TLV корисні багатобайтові дані (16-бітні та 32-бітні числа) можуть починатися з будь-якого байтового зсуву всередині буфера. Наприклад, якщо перший блок містить 1 байт прапорців (займає 3 байти: довжина, тип, значення), то наступний блок почнеться з індексу 3. Поле даних другого блоку потрапить на зсув 5 — тобто на непарну адресу в оперативній пам'яті.

Якщо розробник спробує зчитати 16-бітне число звичайним приведенням типів `*(uint16_t*)&buffer[5]`, поведінка залежатиме від ядра:
- На ядрах **ARM Cortex-M0 / Cortex-M0+** (використовуються в багатьох недорогих BLE-чипах) апаратний модуль зчитування взагалі не підтримує непарний доступ до пам'яті. Така інструкція негайно викликає апаратний виняток **HardFault**, що призводить до перезавантаження мікроконтролера.
- На ядрах **ARM Cortex-M3 / M4 / M33** та **Xtensa / RISC-V (ESP32)** непарний доступ може бути дозволений апаратно, проте він виконується за кілька додаткових тактів шини. Більше того, якщо в системному регістрі конфігурації увімкнено біт контролю вирівнювання (`SCB->CCR |= SCB_CCR_UNALIGN_TRP_Msk`), такий доступ також викличе аварійний збій.

Єдиним безпечним та переносним способом видобування 16-бітних і 32-бітних чисел з буфера TLV є явне побайтове збирання через бітові зсуви або копіювання за допомогою стандартної функції `memcpy`.

#### 2. Захист від зловмисного переповнення буфера (Truncation Attack)

Корисне навантаження рекламного кадру надходить із ненадійного джерела — радіоефіру. Зловмисник або радіомодуль із пошкодженою пам'яттю може сформувати пакет, у якому байт довжини `Length` вказує, наприклад, 30 байтів, тоді як у буфері фактично залишилося лише 5 байтів.

Якщо алгоритм сліпо додає поле довжини до поточного покажчика або передає цей розмір у функцію копіювання, мікроконтролер почне зчитувати чужу пам'ять поза межами буфера. Це призводить або до витоку конфіденційних даних (ключів шифрування), або до аварійного звернення за межі доступного адресного простору (Memory Access Violation).

---

### Безпечний потоковий парсер рекламних структур TLV

Алгоритм розбору повинен працювати як лінійний ітератор, що обчислює точний залишок неперевіреної пам'яті перед кожним кроком. Розбір організовується за схемою нульового копіювання (*Zero-Copy*), тобто парсер не виділяє динамічну пам'ять у купі (Heap), а повертає вказівники та діапазони (`std::span`), що посилаються безпосередньо на байти первинного буфера прийому.

Схема контролю лінійного залишку буфера:

```
Залишок буфера: [ Length ][ AD Type ][ ... Payload ... ]
                   ^          ^             ^
                   |          |             +-- Розмір (Length - 1)
                   |          +---------------- 1 байт
                   +--------------------------- 1 байт
Умова безпеки: Поточний_індекс + 1 + (Length - 1) <= Загальний_розмір_буфера
```

Якщо байт довжини дорівнює нулю (`0x00`), це свідчить про досягнення зони нульового заповнення (Zero Padding), і парсер штатно завершує роботу. Якщо ж поле довжини виходить за фактичні межі залишку буфера, пакет визнається структурно пошкодженим, і розбір переривається з фіксацією помилки.

Ось реалізація модульного парсера мовами C та C++:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Стандартні типи AD Data згідно з Bluetooth Assigned Numbers */
typedef enum {
    BLE_AD_TYPE_FLAGS                 = 0x01,
    BLE_AD_TYPE_UUID16_INCOMPLETE     = 0x02,
    BLE_AD_TYPE_UUID16_COMPLETE       = 0x03,
    BLE_AD_TYPE_UUID32_INCOMPLETE     = 0x04,
    BLE_AD_TYPE_UUID32_COMPLETE       = 0x05,
    BLE_AD_TYPE_UUID128_INCOMPLETE    = 0x06,
    BLE_AD_TYPE_UUID128_COMPLETE      = 0x07,
    BLE_AD_TYPE_SHORT_LOCAL_NAME      = 0x08,
    BLE_AD_TYPE_COMPLETE_LOCAL_NAME   = 0x09,
    BLE_AD_TYPE_TX_POWER_LEVEL        = 0x0A,
    BLE_AD_TYPE_SLAVE_CONN_INTERVAL   = 0x12,
    BLE_AD_TYPE_SERVICE_DATA_16       = 0x16,
    BLE_AD_TYPE_APPEARANCE            = 0x19,
    BLE_AD_TYPE_ADV_INTERVAL          = 0x1A,
    BLE_AD_TYPE_MANUFACTURER_SPECIFIC = 0xFF
} ble_ad_type_t;

/* Структура дескриптора знайденого блоку даних */
typedef struct {
    uint8_t        type;        /* Ідентифікатор AD Type */
    const uint8_t* data;        /* Вказівник на початок корисного навантаження блоку */
    uint8_t        data_len;    /* Довжина корисного навантаження (Length - 1) */
} ble_ad_element_t;

/* Сигнатура функції зворотного виклику. Повернення false зупиняє подальший обхід */
typedef bool (*ble_ad_iterator_cb)(const ble_ad_element_t* elem, void* user_ctx);

/**
 * @brief Безпечний потоковий розбір сирого масиву рекламних даних.
 * @param buffer Вказівник на сирий масив байтів AdvData або ScanRspData.
 * @param buffer_len Фактичний розмір буфера в байтах.
 * @param callback Функція обробки кожного знайденого елемента.
 * @param user_ctx Вказівник на довільний контекст користувача.
 * @return Кількість успішно розібраних блоків TLV.
 */
size_t ble_ad_parse(const uint8_t* buffer, size_t buffer_len, 
                    ble_ad_iterator_cb callback, void* user_ctx) 
{
    if (!buffer || buffer_len == 0 || !callback) {
        return 0;
    }

    size_t offset = 0;
    size_t elements_found = 0;

    while (offset < buffer_len) {
        uint8_t length = buffer[offset];

        /* Довжина 0 вказує на zero-padding або кінець корисного навантаження */
        if (length == 0) {
            break;
        }

        /* Перевірка на вихід за межі буфера: 1 байт поля Length + length байтів тіла */
        if (offset + 1 + length > buffer_len) {
            /* Пакет пошкоджений: заявлена довжина виходить за межі буфера */
            break;
        }

        /* Формуємо дескриптор знайденого елемента */
        ble_ad_element_t elem;
        elem.type     = buffer[offset + 1];
        elem.data     = &buffer[offset + 2];
        elem.data_len = (uint8_t)(length - 1);

        elements_found++;

        /* Викликаємо функцію обробки. Якщо вона повернула false — перериваємо пошук */
        if (!callback(&elem, user_ctx)) {
            break;
        }

        /* Зсуваємо вказівник на наступний блок */
        offset += (1 + length);
    }

    return elements_found;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <optional>
#include <functional>

enum class BleAdType : uint8_t {
    Flags                = 0x01,
    Uuid16Incomplete     = 0x02,
    Uuid16Complete       = 0x03,
    Uuid32Incomplete     = 0x04,
    Uuid32Complete       = 0x05,
    Uuid128Incomplete    = 0x06,
    Uuid128Complete      = 0x07,
    ShortLocalName       = 0x08,
    CompleteLocalName    = 0x09,
    TxPowerLevel         = 0x0A,
    SlaveConnInterval    = 0x12,
    ServiceData16        = 0x16,
    Appearance           = 0x19,
    AdvInterval          = 0x1A,
    ManufacturerSpecific = 0xFF
};

struct BleAdElement {
    BleAdType                   type;
    std::span<const uint8_t>    data;

    [[nodiscard]] std::string_view as_string_view() const noexcept {
        return {reinterpret_cast<const char*>(data.data()), data.size()};
    }
};

class BleAdParser {
public:
    using ElementVisitor = std::function<bool(const BleAdElement&)>;

    /**
     * @brief Безпечний розбір сирого масиву рекламних даних через std::span.
     * @param payload Діапазон байтів рекламного кадру.
     * @param visitor Функція-обробник. Повертає false для зупинки.
     * @return Кількість валідних елементів.
     */
    static size_t for_each(std::span<const uint8_t> payload, const ElementVisitor& visitor) {
        if (payload.empty()) {
            return 0;
        }

        size_t offset = 0;
        size_t parsed_count = 0;

        while (offset < payload.size()) {
            const uint8_t length = payload[offset];

            if (length == 0) {
                break; // Досягнуто нульового заповнювача
            }

            // Перевірка цілісності: чи вміщується задекларований блок у залишок пам'яті
            if (offset + 1 + length > payload.size()) {
                break; // Захист від зловмисних чи пошкоджених пакетів
            }

            BleAdElement element{
                .type = static_cast<BleAdType>(payload[offset + 1]),
                .data = payload.subspan(offset + 2, length - 1)
            };

            parsed_count++;

            if (!visitor(element)) {
                break;
            }

            offset += (1 + length);
        }

        return parsed_count;
    }
};
```
:::

---

### Практичний приклад: видобування імені пристрою та показників сенсора

Розглянемо типову прикладну задачу для центрального вузла (BLE Gateway): під час пасивного або активного сканування отримати повне ім'я вузла (`Complete Local Name`, тип `0x09`) та розшифрувати кастомні показники телеметрії з поля `Manufacturer Specific Data` (`0xFF`).

Важлива вимога стандарту Bluetooth: усі рядки в полях `Shortened Local Name` та `Complete Local Name` передаються **без завершального нульового байта** (`\0`). Якщо вбудована програма спробує виконати стандартні функції `printf("%s")`, `strlen` або `strcpy` безпосередньо над покажчиком `elem->data`, функція піде читати пам'ять далі до випадкового нуля в RAM. Тому парсер зобов'язаний явно обмежувати довжину копіювання розміром `elem->data_len` та самостійно записувати нуль-термінатор у вихідний буфер.

Крім того, корисне ім'я з радіоефіру може містити недруковані керуючі символи або шкідливі послідовності ANSI escape. Для захисту терміналів розробника та баз даних символи з кодами менше ніж `0x20` (пробіл) рекомендується замінювати на знак підкреслення або відкидати під час санітизації.

Нехай наш автономний давач клімату використовує офіційний Company ID компанії Espressif Systems (`0x02E5`, що в пам'яті записується як `0xE5 0x02` у форматі Little-Endian) і транслює 4 корисних байти телеметрії:
- 2 байти знакової температури у сотих частках градуса Цельсія (`int16_t`, little-endian);
- 1 байт відносної вологості повітря у відсотках (`uint8_t`, 0..100 %);
- 1 байт залишкового заряду батареї у відсотках (`uint8_t`, 0..100 %).

Структура поля даних `Manufacturer Specific Data` (сумарно 6 байтів payload):

```
+---------------+---------------+-------------------------------+---------------+---------------+
| Company ID(L) | Company ID(H) | Temp Low (1Б) | Temp High (1Б)| Вологість(1Б) | Батарея (1Б)  |
| 0xE5          | 0x02          | Знакова температура / 100     | 0..100 %      | 0..100 %      |
+---------------+---------------+-------------------------------+---------------+---------------+
```

Нижче наведено завершений модуль фільтрації та розбору даних:

:::tabs
```c
#include <stdio.h>

/* Структура розібраного звіту давача */
typedef struct {
    char    device_name[32];
    bool    has_name;
    int16_t temperature_centi_celsius;
    uint8_t humidity_pct;
    uint8_t battery_pct;
    bool    has_telemetry;
} sensor_report_t;

/* Callback обробника одного TLV блоку */
static bool sensor_ad_visitor(const ble_ad_element_t* elem, void* user_ctx) {
    sensor_report_t* report = (sensor_report_t*)user_ctx;

    if (elem->type == BLE_AD_TYPE_COMPLETE_LOCAL_NAME) {
        /* Копіюємо ім'я з гарантією завершального нуля та захистом від переповнення */
        size_t copy_len = (elem->data_len < sizeof(report->device_name) - 1) 
                          ? elem->data_len 
                          : sizeof(report->device_name) - 1;
        
        for (size_t i = 0; i < copy_len; ++i) {
            uint8_t ch = elem->data[i];
            /* Санітизація: замінюємо керуючі символи на пробіл */
            report->device_name[i] = (ch >= 0x20 && ch <= 0x7E) ? (char)ch : ' ';
        }
        report->device_name[copy_len] = '\0';
        report->has_name = true;
    }
    else if (elem->type == BLE_AD_TYPE_MANUFACTURER_SPECIFIC) {
        /* Перевіряємо мінімальну довжину: 2 байти Company ID + 4 байти сенсорів = 6 Б */
        if (elem->data_len >= 6) {
            /* Безпечне зчитування Company ID у форматі Little-Endian */
            uint16_t company_id = (uint16_t)elem->data[0] | ((uint16_t)elem->data[1] << 8);

            if (company_id == 0x02E5) { /* Espressif Systems */
                /* Зчитуємо температуру без виникнення Unaligned Access Fault */
                int16_t raw_temp = (int16_t)((uint16_t)elem->data[2] | ((uint16_t)elem->data[3] << 8));
                report->temperature_centi_celsius = raw_temp;
                report->humidity_pct = elem->data[4];
                report->battery_pct  = elem->data[5];
                report->has_telemetry = true;
            }
        }
    }

    return true; /* Продовжуємо обхід наступних блоків */
}

void process_adv_packet(const uint8_t* raw_adv_data, size_t raw_len) {
    sensor_report_t report;
    memset(&report, 0, sizeof(report));

    ble_ad_parse(raw_adv_data, raw_len, sensor_ad_visitor, &report);

    if (report.has_name) {
        printf("Знайдено пристрій: %s\n", report.device_name);
    }
    if (report.has_telemetry) {
        printf("Телеметрія: T = %.2f °C, Вологість = %u %%, Заряд = %u %%\n",
               report.temperature_centi_celsius / 100.0f,
               report.humidity_pct,
               report.battery_pct);
    }
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <string>

struct SensorData {
    std::string device_name;
    double      temperature_celsius{0.0};
    uint8_t     humidity_pct{0};
    uint8_t     battery_pct{0};
    bool        valid_telemetry{false};
};

class SensorAdDecoder {
public:
    static std::optional<SensorData> decode(std::span<const uint8_t> raw_payload) {
        SensorData result;

        BleAdParser::for_each(raw_payload, [&result](const BleAdElement& elem) {
            if (elem.type == BleAdType::CompleteLocalName) {
                std::string raw_name = std::string(elem.as_string_view());
                // Санітизація недрукованих символів
                for (char& c : raw_name) {
                    if (static_cast<unsigned char>(c) < 0x20) {
                        c = ' ';
                    }
                }
                result.device_name = std::move(raw_name);
            } 
            else if (elem.type == BleAdType::ManufacturerSpecific) {
                // Перевіряємо довжину: 2 байти Company ID + 4 байти корисних даних
                if (elem.data.size() >= 6) {
                    const uint16_t company_id = static_cast<uint16_t>(elem.data[0]) |
                                               (static_cast<uint16_t>(elem.data[1]) << 8);

                    if (company_id == 0x02E5) { // Espressif Systems
                        const int16_t raw_temp = static_cast<int16_t>(
                            static_cast<uint16_t>(elem.data[2]) |
                            (static_cast<uint16_t>(elem.data[3]) << 8)
                        );

                        result.temperature_celsius = raw_temp / 100.0;
                        result.humidity_pct        = elem.data[4];
                        result.battery_pct         = elem.data[5];
                        result.valid_telemetry     = true;
                    }
                }
            }
            return true; // Продовжуємо парсинг
        });

        if (result.device_name.empty() && !result.valid_telemetry) {
            return std::nullopt;
        }

        return result;
    }
};
```
:::

---

### Генератор рекламних пакетів з оптимізацією ліміту 31 байта

На боці периферійного пристрою розробник стикається зі зворотною проблемою: як упакувати прапорці виявлення, повне ім'я вузла, перелік сервісів і кастомну телеметрію в ліміт 31 байта. Якщо всі дані не вміщуються в один кадр, генератор повинен автоматично перенести другорядні структури (наприклад, довге ім'я пристрою) у буфер відповіді на сканування `Scan Response`.

Типовий розрахунок бюджету байтів для стандартного автономного вузла:
- Блок прапорців `Flags` (тип `0x01`): 1 байт довжини + 1 байт типу + 1 байт значення = **3 байти**.
- Повний перелік 16-бітних сервісів `Complete 16-bit UUIDs` (тип `0x03`, наприклад, сервіс батареї `0x180F` та сенсора `0x181A`): 1 + 1 + 4 = **6 байтів**.
- Повне ім'я вузла `Complete Local Name` (тип `0x09`, наприклад, "Meteo-Sensor-Node-1", 19 символів): 1 + 1 + 19 = **21 байт**.
- Телеметрія виробника `Manufacturer Specific Data` (тип `0xFF`, Company ID + 4 байти показників): 1 + 1 + 6 = **8 байтів**.

Сумарний розмір усіх бажаних структур становить `3 + 6 + 21 + 8 = 38 байтів`. Це на 7 байтів перевищує максимальний ліміт 31 байта для кадру `ADV_IND`.

Стратегія інженерного вирішення:
1. В основний рекламний пакет `ADV_IND` поміщаються критично важливі для виявлення та фільтрації структури: `Flags` (3 Б), `16-bit UUIDs` (6 Б) та `Manufacturer Data` (8 Б). Разом вони займають `3 + 6 + 8 = 17 байтів` із 31 доступного (залишок 14 байтів).
2. Повне ім'я пристрою `Complete Local Name` (21 Б) виноситься у вторинний буфер `Scan Response Data` (`SCAN_RSP`). Коли центральний пристрій здійснює активне сканування, він надсилає `SCAN_REQ` і отримує повну назву окремим кадром.

Ось модуль формування рекламного кадру з суворим контролем переповнення буфера:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BLE_LEGACY_ADV_MAX_PAYLOAD 31

typedef struct {
    uint8_t buffer[BLE_LEGACY_ADV_MAX_PAYLOAD];
    size_t  current_len;
} ble_adv_builder_t;

void ble_adv_builder_init(ble_adv_builder_t* builder) {
    if (builder) {
        memset(builder->buffer, 0, sizeof(builder->buffer));
        builder->current_len = 0;
    }
}

/**
 * @brief Додавання довільного TLV блоку до рекламного кадру.
 * @return true, якщо блок успішно вмістився в ліміт 31 байта.
 */
bool ble_adv_builder_add_field(ble_adv_builder_t* builder, uint8_t type, 
                              const uint8_t* data, uint8_t data_len) 
{
    if (!builder || (!data && data_len > 0)) {
        return false;
    }

    /* Розрахунок необхідного місця: 1 байт (Length) + 1 байт (Type) + data_len */
    size_t required_space = 2 + data_len;

    if (builder->current_len + required_space > BLE_LEGACY_ADV_MAX_PAYLOAD) {
        return false; /* Переповнення буфера */
    }

    /* Запис поля довжини (Type + data_len) */
    builder->buffer[builder->current_len] = (uint8_t)(1 + data_len);
    builder->buffer[builder->current_len + 1] = type;

    if (data_len > 0) {
        memcpy(&builder->buffer[builder->current_len + 2], data, data_len);
    }

    builder->current_len += required_space;
    return true;
}

bool ble_adv_builder_add_flags(ble_adv_builder_t* builder, uint8_t flags) {
    return ble_adv_builder_add_field(builder, BLE_AD_TYPE_FLAGS, &flags, 1);
}

bool ble_adv_builder_add_name(ble_adv_builder_t* builder, const char* name) {
    if (!name) return false;
    return ble_adv_builder_add_field(builder, BLE_AD_TYPE_COMPLETE_LOCAL_NAME, 
                                     (const uint8_t*)name, (uint8_t)strlen(name));
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <array>
#include <optional>
#include <cstring>

class BleAdvBuilder {
public:
    static constexpr size_t MaxPayloadSize = 31;

    BleAdvBuilder() = default;

    [[nodiscard]] bool add_field(BleAdType type, std::span<const uint8_t> data) noexcept {
        const size_t required_space = 2 + data.size();
        if (current_size_ + required_space > MaxPayloadSize) {
            return false; // Не вміщується в буфер
        }

        buffer_[current_size_]     = static_cast<uint8_t>(1 + data.size());
        buffer_[current_size_ + 1] = static_cast<uint8_t>(type);

        if (!data.empty()) {
            std::memcpy(&buffer_[current_size_ + 2], data.data(), data.size());
        }

        current_size_ += required_space;
        return true;
    }

    [[nodiscard]] bool add_flags(uint8_t flags) noexcept {
        const std::array<uint8_t, 1> f{flags};
        return add_field(BleAdType::Flags, f);
    }

    [[nodiscard]] bool add_complete_name(std::string_view name) noexcept {
        const auto span = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(name.data()), name.size()
        );
        return add_field(BleAdType::CompleteLocalName, span);
    }

    [[nodiscard]] std::span<const uint8_t> build() const noexcept {
        return {buffer_.data(), current_size_};
    }

private:
    std::array<uint8_t, MaxPayloadSize> buffer_{};
    size_t current_size_{0};
};
```
:::

---

### Агрегація звітів активного сканування у базі пристроїв

Коли активний сканер (Active Scanner) прослуховує ефір, він отримує інформацію про кожен навколишній пристрій у вигляді двох окремих асинхронних подій канального рівня:
1. Спочатку надходить подія прийому основного кадру `ADV_IND` (або `ADV_SCAN_IND`). Вона містить MAC-адресу мовника, тип адреси, рівень RSSI та масив `AdvData`.
2. Контролер сканера автоматично надсилає `SCAN_REQ` і через короткий проміжок часу отримує подію прийому `SCAN_RSP`, яка містить ту саму MAC-адресу, але інший масив корисних даних `ScanRspData`.

У реальному радіоефірі через інтерференцію пакет `SCAN_RSP` може бути втрачений, або периферійний пристрій може взагалі не підтримувати сканування (наприклад, надсилає `ADV_NONCONN_IND`). Тому програмний стек хоста повинен вести таблицю знайдених вузлів (*Device Database*), яка об'єднує дані обох звітів за унікальним ключем `(MAC-адреса, Address Type)`.

Ключові вимоги до реалізації таблиці пристроїв сканера:
- **Оновлення рівня сигналу RSSI:** сире значення RSSI зазнає швидких релеєвських завмирань через багатопроменеве поширення радіохвиль. Для фільтрації флуктуацій застосовують експоненційне згладжування (EMA, *Exponential Moving Average*):

```
RSSI_filtered = α · RSSI_new + (1 - α) · RSSI_previous
```

Де коефіцієнт згладжування `α` зазвичай обирають у діапазоні `0.1 ≤ α ≤ 0.3`.
- **Тайм-аут старіння записів (Entry TTL):** якщо від пристрою не надходило нових рекламних пакетів протягом заданого часу (наприклад, 10–30 секунд), запис у таблиці позначається як застарілий або видаляється з пам'яті для звільнення RAM мікроконтролера.
- **Скидання кешу при зміні прапорців:** якщо пристрій змінив стан прапорців `Flags` або перелік сервісів, кешовані поля попереднього `SCAN_RSP` інвалідуються, ініціюючи повторний активний запит.

---

### Простеження через інтерфейс HCI (HCI LE Advertising Report)

На стику між апаратним трансивером Bluetooth і процесором застосунку працює інтерфейс хост-контролера HCI (*Host Controller Interface*). Коли радіоконтролер успішно декодує рекламний пакет у радіоефірі, він формує спеціальний асинхронний кадр події `HCI_LE_Advertising_Report_Event` (код події `0x3E`, субкод `0x02`):

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Event (0x3E)  | Param Len (N) | Sub-Event(0x02)| Num Reports  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Event Type    | Address Type  |       Device Address (0..3)   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Device Address (4..5)         |  Data Length  | Payload ...   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| ... Payload continued ...     |   RSSI (1Б)   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Розшифровка полів кадру HCI:
- **`Event Type` (1 байт):** тип прийнятого рекламного кадру: `0x00` (`ADV_IND`), `0x01` (`ADV_DIRECT_IND`), `0x02` (`ADV_SCAN_IND`), `0x03` (`ADV_NONCONN_IND`), `0x04` (`SCAN_RSP`).
- **`Address Type` (1 байт):** тип MAC-адреси: `0x00` (Public Device Address), `0x01` (Random Device Address), `0x02` (Public Identity Address після резолвінгу RPA), `0x03` (Random Identity Address).
- **`Device Address` (6 байтів):** двійкова апаратна адреса передавача (little-endian).
- **`Data Length` (1 байт):** розмір масиву корисних даних `AdvData` або `ScanRspData` (0..31 байт).
- **`Payload` (`Data Length` байтів):** сирий масив байтів TLV, який безпосередньо передається у функцію `ble_ad_parse()`.
- **`RSSI` (1 байт):** виміряна потужність вхідного сигналу зі знаком (`int8_t` від -127 до +20 дБм).

Важливий аспект налаштування сканера через HCI-команду `HCI_LE_Set_Scan_Parameters`: параметр `Filter_Duplicates`. Якщо фільтрацію дублікатів увімкнено (`0x01`), радіоконтролер надсилає на процесор хоста лише перший отриманий пакет від кожного унікального пристрою за період сканування. Це кардинально знижує навантаження на шину UART/SPI та економить процесорний час. Проте, якщо ваш давач періодично оновлює покажчики температури безпосередньо всередині поля `Manufacturer Specific Data`, фільтрацію дублікатів необхідно обов'язково вимкнути (`0x00`), інакше хост ніколи не побачить оновлення даних без перепідключення.

---

### Діагностика розривів зв'язку (HCI Disconnection Reasons)

У процесі експлуатації з'єднань між периферією та центральним пристроєм радіозв'язок періодично розривається. Коли контролер фіксує завершення сесії, він генерує подію `HCI_Disconnection_Complete_Event` (код події `0x05`), яка містить 1 байт коду причини розриву (*Reason Code*).

Аналіз кодів завершення сесії дозволяє точно локалізувати джерело проблеми:

- `0x08` — `Connection Timeout`. Спрацював системний таймер нагляду Supervision Timeout. Контролер не зміг успішно прийняти жодного коректного пакета від партнера протягом встановленого інтервалу (наприклад, 4 секунд). Головні причини: фізичний вихід користувача із зони радіозв'язку, критичний рівень завад від одночасного трафіку Wi-Fi або раптове відключення живлення (наприклад, виймання батарейки з давача).
- `0x13` — `Remote User Terminated Connection`. Партнер штатно розірвав з'єднання з ініціативи вищого рівня застосунку (наприклад, користувач смартфона натиснув кнопку вимкнення в мобільному додатку або вимкнув системний перемикач Bluetooth).
- `0x16` — `Connection Terminated by Local Host`. Локальний мікроконтролер самостійно закрив з'єднання викликом відповідної функції стека (наприклад, після успішної передачі чергової порції телеметрії давач розриває зв'язок і переходить у режим глибокого енергозбереження).
- `0x3D` — `Connection Terminated due to MIC Failure`. Апаратний контролер виявив невідповідність коду автентичності повідомлення MIC (*Message Integrity Check*) під час розшифрування пакета канального рівня AES-CCM. Зазвичай свідчить про спробу підміни даних зловмисником або втрату синхронізації 39-бітного внутрішнього лічильника пакетів `PacketCounter`.
- `0x3E` — `Connection Failed to be Established`. Центральний пристрій надіслав команду `CONNECT_IND`, проте периферія не вийшла в радіоефір і не відповіла жодним пакетом у межах початкового вікна передачі `TransmitWindow`.

---

### Сумісність параметрів з'єднання з операційними системами (iOS / Android)

Коли периферія формує запит на оновлення параметрів зв'язку, вона повинна суворо дотримуватися вимог операційних систем, до яких підключається. Наприклад, компанія Apple у специфікації *Accessory Design Guidelines for Apple Devices* висуває жорсткі математичні обмеження для будь-якого BLE-аксесуара:

1. **Кратність інтервалу:** значення `Interval Min` та `Interval Max` повинні бути кратними 15 мс (тобто 15, 30, 45, 60, 75 мс тощо).
2. **Мінімальний розрив:** `Interval Max` має бути щонайменше на 15 мс більшим за `Interval Min` (або дорівнювати йому, якщо потрібен фіксований розклад).
3. **Обмеження максимального періоду зв'язку:** добуток інтервалу та латентності периферії не повинен перевищувати 2 секунди:

```
Interval_Max · (Slave_Latency + 1) ≤ 2.0 секунди
```

4. **Граничний тайм-аут нагляду:** `Supervision Timeout` має бути не більшим за 6.0 секунд і водночас повинен задовольняти базову нерівність надійності:

```
Supervision_Timeout > (1 + Slave_Latency) · Interval_Max · 2
```

Якщо запит `L2CAP_CONNECTION_PARAM_UPDATE_REQ` порушує хоча б одне з цих правил, стек iOS негайно повертає відповідь із кодом відхилення `0x0001` (*Connection Parameters Rejected*), залишаючи попередній енергозатратний інтервал.

---

### Формування запиту оновлення параметрів зв'язку (L2CAP Signaling)

У практичній розробці периферійних вузлів виникає фундаментальна невідповідність енергетичних профілів:
1. **Під час початкового підключення** центральний пристрій зазвичай встановлює агресивний інтервал зв'язку 15–30 мс, щоб за лічені частки секунди провести шифрування, обмін ключами та завантажити повну базу сервісів GATT.
2. **У стані спокою** автономному давачу непотрібно обмінюватися пакетами 50 разів на секунду. Тримання радіотракту в такому режимі розрядить дискову батарейку CR2032 за кілька тижнів замість запланованих двох років.

Периферія є підпорядкованим вузлом (Link Layer Slave) і не може примусово змінити системний таймер зв'язку. Проте стандарт GAP надає периферії право надіслати хосту запит на зміну параметрів через спеціальний сигнальний канал L2CAP (*Logical Link Control and Adaptation Protocol*, `CID = 0x0006`).

Сигнальний кадр `L2CAP_CONNECTION_PARAM_UPDATE_REQ` (код команди `0x12`) містить 4 ключових параметри:
- **`Interval Min` / `Interval Max`:** бажані нижня та верхня межі періоду подій зв'язку (у дискретах по 1.25 мс);
- **`Slave Latency`:** кількість подій з'єднання, які периферія планує пропускати у сплячому режимі за відсутності нових даних;
- **`Timeout Multiplier`:** максимальний часовий інтервал нагляду Supervision Timeout (у дискретах по 10 мс).

Двійкова структура кадру L2CAP:

```
+--------------------+--------------------+---------------------------------------+
| Довжина L2CAP (2Б) | Канал CID (2Б)     | Код команди (1Б, 0x12) | Ідентифікатор|
| 0x0008             | 0x0006 (Signaling) | L2CAP_CONN_PARAM_UPDATE_REQ   | (1Б, ID)     |
+--------------------+--------------------+---------------------------------------+
| Довжина даних (2Б) | Min Interval (2Б)  | Max Interval (2Б)                     |
| 0x0008             | (кратне 1.25 мс)   | (кратне 1.25 мс)                      |
+--------------------+--------------------+---------------------------------------+
| Slave Latency (2Б) | Supervision Timeout|                                       |
| (0..499 подій)     | (кратне 10 мс)     |                                       |
+--------------------+--------------------+---------------------------------------+
```

Правила складання бінарного пакета мовами C та C++:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>

#define L2CAP_CID_BLE_SIGNALING          0x0006
#define L2CAP_CMD_CONN_PARAM_UPDATE_REQ  0x12

typedef struct __attribute__((packed)) {
    /* Заголовок кадру адаптації L2CAP */
    uint16_t l2cap_length;      /* Довжина поля сигналізації = 12 байтів */
    uint16_t l2cap_cid;         /* 0x0006 (LE Signaling Channel) */
    
    /* Заголовок команди сигналізації */
    uint8_t  command_code;      /* 0x12 (Connection Parameter Update Request) */
    uint8_t  identifier;        /* Унікальний ID транзакції для зіставлення з відповіддю */
    uint16_t command_length;    /* Довжина корисного навантаження команди = 8 байтів */
    
    /* Параметри зв'язку (усі числові поля у форматі Little-Endian) */
    uint16_t interval_min;      /* Мінімальний інтервал (одиниці 1.25 мс) */
    uint16_t interval_max;      /* Максимальний інтервал (одиниці 1.25 мс) */
    uint16_t slave_latency;     /* Дозволений пропуск подій зв'язку периферією */
    uint16_t timeout_multiplier;/* Supervision Timeout (одиниці 10 мс) */
} l2cap_conn_param_update_req_t;

/**
 * @brief Побудова пакета запиту оновлення параметрів зв'язку L2CAP.
 * @param out_buf Буфер для запису сформованого кадру (мінімум 16 байтів).
 * @param max_buf_len Максимальний розмір буфера.
 * @param pkt_id Унікальний лічильник транзакції.
 * @param min_ms Мінімальний інтервал у мілісекундах (наприклад, 100.0 мс).
 * @param max_ms Максимальний інтервал у мілісекундах (наприклад, 200.0 мс).
 * @param latency Кількість подій для пропуску (наприклад, 4).
 * @param timeout_ms Тайм-аут нагляду в мілісекундах (наприклад, 4000 мс).
 * @return Фактичний розмір зібраного пакета в байтах.
 */
size_t build_l2cap_param_update_req(uint8_t* out_buf, size_t max_buf_len,
                                    uint8_t pkt_id,
                                    float min_ms, float max_ms,
                                    uint16_t latency, uint16_t timeout_ms)
{
    if (!out_buf || max_buf_len < sizeof(l2cap_conn_param_update_req_t)) {
        return 0;
    }

    l2cap_conn_param_update_req_t* req = (l2cap_conn_param_update_req_t*)out_buf;

    req->l2cap_length    = 12; // 4 байти заголовка команди + 8 байтів параметрів
    req->l2cap_cid       = L2CAP_CID_BLE_SIGNALING;
    req->command_code    = L2CAP_CMD_CONN_PARAM_UPDATE_REQ;
    req->identifier      = pkt_id;
    req->command_length  = 8;

    /* Переведення часових інтервалів у стандартні протокольні дискрети */
    req->interval_min       = (uint16_t)(min_ms / 1.25f);
    req->interval_max       = (uint16_t)(max_ms / 1.25f);
    req->slave_latency      = latency;
    req->timeout_multiplier = (uint16_t)(timeout_ms / 10);

    return sizeof(l2cap_conn_param_update_req_t);
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>

struct GapConnectionRequirements {
    float    min_interval_ms{100.0f};
    float    max_interval_ms{200.0f};
    uint16_t slave_latency{4};
    uint16_t supervision_timeout_ms{4000};
};

class L2CapSignalingBuilder {
public:
    static constexpr size_t PacketSize = 16;
    static constexpr uint16_t BleSignalingCid = 0x0006;
    static constexpr uint8_t ParamUpdateReqOpcode = 0x12;

    /**
     * @brief Генерація бінарного кадру L2CAP_CONNECTION_PARAM_UPDATE_REQ.
     * @param transaction_id Унікальний лічильник транзакції.
     * @param reqs Бажані межі параметрів зв'язку.
     * @return Сформований масив байтів фіксованого розміру.
     */
    [[nodiscard]] static std::optional<std::array<uint8_t, PacketSize>> build_update_request(
        uint8_t transaction_id, 
        const GapConnectionRequirements& reqs) noexcept 
    {
        std::array<uint8_t, PacketSize> buffer{};

        // L2CAP Header (4 байти)
        buffer[0] = 0x0C; // Довжина поля сигналізації = 12 байтів
        buffer[1] = 0x00;
        buffer[2] = static_cast<uint8_t>(BleSignalingCid & 0xFF);
        buffer[3] = static_cast<uint8_t>((BleSignalingCid >> 8) & 0xFF);

        // Command Header (4 байти)
        buffer[4] = ParamUpdateReqOpcode;
        buffer[5] = transaction_id;
        buffer[6] = 0x08; // Довжина корисного навантаження команди = 8 байтів
        buffer[7] = 0x00;

        // Розрахунок протокольних одиниць
        const uint16_t int_min = static_cast<uint16_t>(reqs.min_interval_ms / 1.25f);
        const uint16_t int_max = static_cast<uint16_t>(reqs.max_interval_ms / 1.25f);
        const uint16_t timeout = static_cast<uint16_t>(reqs.supervision_timeout_ms / 10);

        // Запис значень у форматі Little-Endian
        buffer[8]  = static_cast<uint8_t>(int_min & 0xFF);
        buffer[9]  = static_cast<uint8_t>((int_min >> 8) & 0xFF);
        buffer[10] = static_cast<uint8_t>(int_max & 0xFF);
        buffer[11] = static_cast<uint8_t>((int_max >> 8) & 0xFF);
        buffer[12] = static_cast<uint8_t>(reqs.slave_latency & 0xFF);
        buffer[13] = static_cast<uint8_t>((reqs.slave_latency >> 8) & 0xFF);
        buffer[14] = static_cast<uint8_t>(timeout & 0xFF);
        buffer[15] = static_cast<uint8_t>((timeout >> 8) & 0xFF);

        return buffer;
    }
};
```
:::

Ці процедури дозволяють безпечно інтегрувати низькорівневе керування рекламою та з'єднанням у будь-який вбудований стек на базі FreeRTOS, Zephyr або чистих bare-metal середовищ.
