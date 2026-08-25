# 📋 Повідомлення та типи протоколу параметрів MAVLink

Протокол параметрів MAVLink (Parameter Microservice) є стандартизованим інтерфейсом передачі, опису та модифікації конфігураційних змінних між автопілотом безпілотного апарата і наземною станцією керування або бортовими супутніми комп'ютерами. Цей мікросервіс спирається на фіксований набір бінарних повідомлень та строго типізовані переліки. Без глибокого розуміння точного бінарного розташування полів у кадрі, порядку байтів, правил пакування типів у 32-бітний контейнер та обробки 16-символьних ідентифікаторів неможливо побудувати надійний сервіс конфігурації бортового комп'ютера чи наземної станції керування.

Ця довідка містить вичерпний опис бінарних структур стандартного протоколу (Standard Parameter Protocol) та протоколу розширених параметрів (Parameter Extended Protocol), системних числових кодів типів `MAV_PARAM_TYPE`, кодів підтвердження `PARAM_ACK`, детального аналізу зміщення полів у пам'яті, правил адресації компонентів, розрахунку контрольних сум CRC Extra, прапорців сумісності `MAV_PROTOCOL_CAPABILITY`, вирівнювання структур у пам'яті та правил побітового копіювання бітів при роботі з різними архітектурами мікроконтролерів.

---

### Системні типи параметрів: перелік MAV_PARAM_TYPE

Кожен параметр на борту автопілота має оголошений тип даних, що визначається переліком `MAV_PARAM_TYPE`. У стандартному протоколі цей тип передається в однобайтовому полі `param_type` (тип `uint8_t`), вказуючи наземній станції, як саме інтерпретувати 4 байти поля `param_value`.

Усі повідомлення MAVLink використовують прямий порядок байтів (little-endian), що відповідає більшості сучасних процесорних архітектур (ARM Cortex-M, x86-64, RISC-V). Це означає, що молодший байт багатобайтового числа передається першим у каналі зв'язку.

| Числовий код | Назва типу | Розмір (байти) | Опис, бінарний формат та діапазон значень |
| :--- | :--- | :--- | :--- |
| **1** | `MAV_PARAM_TYPE_UINT8` | 1 | 8-бітне беззнакове ціле (`0` .. `255`). У 32-бітному контейнері займає молодший байт, решта 3 байти заповнюються нулями. |
| **2** | `MAV_PARAM_TYPE_INT8` | 1 | 8-бітне знакове ціле в додатковому коді (`-128` .. `127`). Вимагає збереження знакового біта при розширенні. |
| **3** | `MAV_PARAM_TYPE_UINT16` | 2 | 16-бітне беззнакове ціле (`0` .. `65535`). Використовується для лічильників, портів, бітових прапорців. |
| **4** | `MAV_PARAM_TYPE_INT16` | 2 | 16-бітне знакове ціле (`-32768` .. `32767`). Застосовується для калібрувальних коефіцієнтів сенсорів. |
| **5** | `MAV_PARAM_TYPE_UINT32` | 4 | 32-бітне беззнакове ціле (`0` .. `4294967295`). Бітові маски сенсорів, конфігурації портів, IP-адреси. |
| **6** | `MAV_PARAM_TYPE_INT32` | 4 | 32-бітне знакове ціле (`-2147483648` .. `2147483647`). Цілочисельні мітки часу, зміщення координат. |
| **7** | `MAV_PARAM_TYPE_UINT64` | 8 | 64-бітне беззнакове ціле (`0` .. `18446744073709551615`). Лише в Extended Protocol (GUID, ключі шифрування). |
| **8** | `MAV_PARAM_TYPE_INT64` | 8 | 64-бітне знакове ціле. Лише в Extended Protocol (UNIX-мітки в мікросекундах). |
| **9** | `MAV_PARAM_TYPE_REAL32` | 4 | 32-бітне число з рухомою комою одинарної точності за стандартом IEEE 754-2008. Фізичні величини, коефіцієнти PID. |
| **10** | `MAV_PARAM_TYPE_REAL64` | 8 | 64-бітне число з рухомою комою подвійної точності IEEE 754. Лише в Extended Protocol (координати GPS високої точності). |

У стандартному протоколі параметрів типи 1..6 (від `uint8` до `int32`) пакуються в 4-байтове поле `param_value` через пряме копіювання пам'яті (bit-cast), де менші типи вирівнюються за молодшими байтами. Типи 7, 8 та 10 (`uint64`, `int64`, `real64`) фізично не вміщуються в 4 байти і потребують використання розширеного протоколу.

---

### Ідентифікатор параметра: правила обробки param_id[16]

Поле `param_id` у всіх повідомленнях MAVLink являє собою фіксований масив із 16 байтів ASCII-символів. Це поле має суворі семантичні правила, які є найчастішим джерелом помилок переповнення буфера в саморобних наземних станціях та парсерах:

1. **Довжина назви менше 16 символів:** рядок завершується нульовим символом `\0` (null-terminator). Усі наступні невикористані байти масиву повинні заповнюватися нулями для детермінованості підрахунку контрольних сум і хешів.
2. **Довжина назви рівно 16 символів:** рядок **не містить** кінцевого нуля `\0` у межах масиву! Усі 16 байтів зайняті друкованими символами ASCII.
3. **Правило приймача:** будь-який парсер MAVLink зобов'язаний виділяти для локального рядка буфер розміром щонайменше 17 байтів, копіювати туди до 16 байтів із повідомлення та явно встановлювати нульовий термінатор на 16-ту позицію (`buffer[16] = '\0'`). Виклик стандартних функцій `strlen()` або `printf("%s")` безпосередньо над сирим полем `msg.param_id` призводить до виходу за межі пам'яті (buffer over-read).

---

### Адресація компонентів та ізоляція простору параметрів

MAVLink підтримує наявність багатьох незалежних компонентів у межах однієї системи (одного літального апарата з адресою `target_system`). Кожен компонент має свій власний числовий ідентифікатор `target_component` та веде власний, повністю ізольований простір параметрів:

* `MAV_COMP_ID_AUTOPILOT1` (`1`): головний автопілот польотного контролера (керування двигунами, стабілізація, навігація, параметри PID, батарея).
* `MAV_COMP_ID_CAMERA` (`100`): бортовий контролер оптичної камери (експозиція, роздільна здатність, частота кадрів, режим зуму).
* `MAV_COMP_ID_GIMBAL` (`154`): стабілізований трьохосьовий підвіс камери (коефіцієнти PID підвісу, швидкість панорамування, ліміти кутів).
* `MAV_COMP_ID_OBSTACLE_AVOIDANCE` (`196`): бортовий лідар або стереокамера обходу перешкод (безпечна дистанція зупинки, пороги тривоги).

Коли наземна станція ініціює вичитування списку параметрів за допомогою повідомлення `PARAM_REQUEST_LIST`, вона повинна вказувати точну адресу компонента, параметри якого запитуються. Автопілот повертає параметри автопілота (`target_component = 1`), а підвіс або камера відповідають лише на запити зі своїм `target_component`. Об'єднання або перемішування індексів між різними компонентами категорично заборонено: кожен компонент веде власний лічильник `param_count` та власну нумерацію `param_index` від `0` до `count - 1`.

---

### Контрольні суми CRC Extra для повідомлень параметрів

MAVLink використовує механізм **CRC Extra** для забезпечення сумісності структури повідомлень між різними версіями програмного забезпечення. До стандартної 16-бітної контрольної суми кадру CRC-16-CCITT під час генерації коду додається один так званий «магічний байт», розрахований на основі назв полів, їхніх типів та порядку в XML-визначенні. Якщо визначення повідомлення на борті відрізняється від визначення на станції (наприклад, додано поле або змінено тип), розраховані значення CRC не зійдуться, і пакет буде відкинутий на рівні приймача.

Нижче наведено нормативні значення CRC Extra для всіх повідомлень протоколу параметрів:

| Назва повідомлення | Числовий MSG ID | Байт CRC Extra | Мінімальний розмір корисних даних |
| :--- | :--- | :--- | :--- |
| `PARAM_REQUEST_READ` | **20** | **214** | 20 байтів |
| `PARAM_REQUEST_LIST` | **21** | **159** | 2 байти |
| `PARAM_VALUE` | **22** | **220** | 25 байтів |
| `PARAM_SET` | **23** | **168** | 23 байти |
| `PARAM_EXT_REQUEST_READ` | **320** | **229** | 20 байтів |
| `PARAM_EXT_REQUEST_LIST` | **321** | **88** | 2 байти |
| `PARAM_EXT_VALUE` | **322** | **243** | 149 байтів |
| `PARAM_EXT_SET` | **323** | **78** | 147 байтів |
| `PARAM_EXT_ACK` | **324** | **132** | 148 байтів |

Якщо при розробці власного стека повідомлення ігноруються автопілотом, першим кроком діагностики є перевірка збігу байта CRC Extra: невідповідність цього байта призводить до тихого відкидання пакетів на боці приймача без генерації помилок.

---

### Прапорці сумісності та можливостей протоколу

У повідомленні `AUTOPILOT_VERSION` (#148) бортова система транслює 64-бітне бітове поле можливостей `capabilities` з переліку `MAV_PROTOCOL_CAPABILITY`. Для протоколу параметрів критичними є такі прапорці:

* `MAV_PROTOCOL_CAPABILITY_PARAM_FLOAT` (`bit 0`, маска `0x01`): автопілот підтримує стандартний протокол передачі параметрів через 32-бітний `float`.
* `MAV_PROTOCOL_CAPABILITY_PARAM_UNION` (`bit 8`, маска `0x100`): автопілот підтримує побітове копіювання цілих типів (bit-cast) у поле `param_value` без арифметичного округлення до `float`.
* `MAV_PROTOCOL_CAPABILITY_PARAM_EXT` (`bit 20`, маска `0x100000`): автопілот підтримує розширений протокол параметрів (`PARAM_EXT_*`) для 64-бітних типів та довільних бінарних структур.

Наземна станція перевіряє ці прапорці під час первинного рукостискання, щоб обрати оптимальний протокол синхронізації та коректний алгоритм інтерпретації значень.

---

### Вирівнювання пам'яті та директиви пакування структур

У вбудованих системах на базі мікроконтролерів ARM Cortex-M0/M3/M4 невірне вирівнювання багатобайтових чисел (unaligned memory access) може призводити до апаратного винятку `HardFault` або зниження продуктивності на 2–3 такти процесора на кожне читання. Генератор коду MAVLink вирішує цю проблему двома шляхами:

1. **Внутрішнє сортування полів:** у бінарному тілі повідомлення 4-байтові поля (`param_value`) завжди розміщуються за зсувом, кратним 4; 2-байтові поля (`param_count`, `param_index`) розміщуються за зсувом, кратним 2; масиви байтів (`param_id`) та 1-байтові поля (`param_type`) розташовуються наприкінці.
2. **Директиви пакування:** структури оголошуються з атрибутом `__attribute__((packed))` у GCC/Clang або обгортаються у директиви `#pragma pack(push, 1)` / `#pragma pack(pop)` у MSVC, що гарантує відсутність неявних проміжних байтів (padding bytes) між полями структури на будь-якому компіляторі.

Завдяки цьому бінарні структури повідомлень MAVLink можна безпосередньо відображати на буфер прийому послідовного порту через виклики `memcpy`, гарантуючи повну переносність між 8-бітними AVR, 32-бітними STM32/ESP32 та 64-бітними процесорами x86-64 / Apple Silicon.

---

### Структури повідомлень стандартного протоколу (Standard Parameter Protocol)

Стандартний протокол параметрів включає чотири основні повідомлення: одне для запиту списку, одне для читання окремого параметра, одне для запису та одне універсальне повідомлення значення/підтвердження.

#### 1. PARAM_REQUEST_LIST (ID #21)

Повідомлення ініціалізації вичитування всього дерева параметрів з борта. Надсилається наземною станцією для запиту повної конфігурації після встановлення зв'язку.

* **Тип взаємодії:** Point-to-Point запит (станція → автопілот).
* **Відповідь:** Послідовний потік повідомлень `PARAM_VALUE` (від індексу `0` до `param_count - 1`).
* **Розмір корисного навантаження:** 2 байти.

```
Структура корисного навантаження PARAM_REQUEST_LIST (2 байти):
  Зсув  Розмір  Тип      Назва поля        Призначення
  -----------------------------------------------------------------------------
  [0]   1 байт  uint8_t  target_system     Системний ID апарата-адресата (1..255)
  [1]   1 байт  uint8_t  target_component  Компонентний ID (1 = MAV_COMP_ID_AUTOPILOT1)
```

:::tabs
```c
/* Бінарна структура повідомлення PARAM_REQUEST_LIST */
typedef struct __mavlink_param_request_list_t {
    uint8_t target_system;     /* ID системи-адресата */
    uint8_t target_component;  /* ID компонента-адресата */
} mavlink_param_request_list_t;

/* Функція пакування повідомлення у буфер */
int pack_param_request_list(uint8_t sys_id, uint8_t comp_id,
                            uint8_t target_sys, uint8_t target_comp,
                            uint8_t *buffer) {
    mavlink_message_t msg;
    mavlink_param_request_list_t payload;
    payload.target_system = target_sys;
    payload.target_component = target_comp;
    mavlink_msg_param_request_list_encode(sys_id, comp_id, &msg, &payload);
    return mavlink_msg_to_send_buffer(buffer, &msg);
}
```
```cpp
#include <cstdint>
#include <span>
#include <array>

/* C++ обгортка над повідомленням PARAM_REQUEST_LIST з ідіоматичним інтерфейсом */
struct ParamRequestList {
    uint8_t target_system{1};
    uint8_t target_component{1};

    [[nodiscard]] size_t encode(uint8_t sys_id, uint8_t comp_id,
                                std::span<uint8_t> output_buffer) const {
        mavlink_message_t msg;
        mavlink_param_request_list_t payload{
            .target_system = target_system,
            .target_component = target_component
        };
        mavlink_msg_param_request_list_encode(sys_id, comp_id, &msg, &payload);
        uint16_t len = mavlink_msg_to_send_buffer(output_buffer.data(), &msg);
        return static_cast<size_t>(len);
    }
};
```
:::

#### 2. PARAM_VALUE (ID #22)

Головне повідомлення передачі параметра. Надсилається автопілотом у відповідь на `PARAM_REQUEST_LIST`, `PARAM_REQUEST_READ` або як підтвердження зміни після отримання `PARAM_SET`.

* **Тип взаємодії:** Потокова відповідь або броадкаст-підтвердження (автопілот → усі GCS).
* **Розмір корисного навантаження:** 25 байтів.

```
Структура корисного навантаження PARAM_VALUE (25 байтів):
  Зсув    Розмір   Тип        Назва поля    Призначення
  -----------------------------------------------------------------------------
  [0..3]  4 байти  float      param_value   Значення параметра (IEEE 754 або bit-cast)
  [4..5]  2 байти  uint16_t   param_count   Загальна кількість параметрів на борту
  [6..7]  2 байти  uint16_t   param_index   Індекс поточного параметра (0..count-1)
  [8..23] 16 байт  char[16]   param_id      16-байтний ідентифікатор ASCII
  [24]    1 байт   uint8_t    param_type    Тип даних з переліку MAV_PARAM_TYPE
```

Повідомлення виконує три фундаментальні ролі:
1. **Елемент потоку списку:** під час вичитування всіх параметрів надсилається з послідовними `param_index` від `0` до `param_count - 1`.
2. **Точкова відповідь на читання:** повертає запитаний за назвою чи індексом параметр.
3. **Квитування запису:** після обробки `PARAM_SET` автопілот розсилає `PARAM_VALUE` усім під'єднаним станціям. При цьому `param_index` містить реальний індекс зміненого параметра або `65535` (`UINT16_MAX`), якщо параметр не індексується динамічно.

:::tabs
```c
/* Бінарна структура повідомлення PARAM_VALUE */
typedef struct __mavlink_param_value_t {
    float    param_value;   /* 4 байти значення */
    uint16_t param_count;   /* загальна кількість параметрів */
    uint16_t param_index;   /* індекс поточного параметра */
    char     param_id[16];  /* 16-байтний ідентифікатор */
    uint8_t  param_type;    /* тип даних (MAV_PARAM_TYPE) */
} mavlink_param_value_t;

/* Безпечне копіювання ідентифікатора у нуль-термінований рядок */
void extract_safe_param_id(const char wire_id[16], char out_str[17]) {
    memcpy(out_str, wire_id, 16);
    out_str[16] = '\0';
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <string>
#include <array>
#include <cstring>
#include <bit>

/* C++ структура з безпечною обробкою рядків та типізованим значенням */
struct ParamValueMsg {
    float raw_value{0.0f};
    uint16_t count{0};
    uint16_t index{0};
    std::array<char, 16> id{};
    uint8_t type{0};

    [[nodiscard]] std::string_view name() const noexcept {
        size_t len = 0;
        while (len < id.size() && id[len] != '\0') {
            ++len;
        }
        return std::string_view(id.data(), len);
    }

    [[nodiscard]] int32_t as_int32() const noexcept {
        return std::bit_cast<int32_t>(raw_value);
    }

    [[nodiscard]] uint32_t as_uint32() const noexcept {
        return std::bit_cast<uint32_t>(raw_value);
    }

    [[nodiscard]] float as_float() const noexcept {
        return raw_value;
    }
};
```
:::

#### 3. PARAM_REQUEST_READ (ID #20)

Запит вичитування одного конкретного параметра. Дозволяє вичитувати значення або за числовим індексом (`param_index >= 0`), або за рядковою назвою (`param_index = -1` та заповнений `param_id`).

* **Тип взаємодії:** Point-to-Point запит (станція → автопілот).
* **Відповідь:** Одиничне повідомлення `PARAM_VALUE`.
* **Розмір корисного навантаження:** 20 байтів.

```
Структура корисного навантаження PARAM_REQUEST_READ (20 байтів):
  Зсув    Розмір   Тип        Назва поля        Призначення
  -----------------------------------------------------------------------------
  [0..1]  2 байти  int16_t    param_index       Індекс (>= 0) або -1 для пошуку за назвою
  [2]     1 байт   uint8_t    target_system     ID системи-адресата
  [3]     1 байт   uint8_t    target_component  ID компонента-адресата
  [4..19] 16 байт  char[16]   param_id          Назва параметра (якщо index == -1)
```

Семантика поля `param_index` та обробка крайових випадків:
* Якщо `param_index >= 0`: пошук виконується за індексом у внутрішній таблиці автопілота. Це швидка операція з часовою складністю `O(1)`. Вміст поля `param_id` ігнорується. Якщо передано індекс, що перевищує або дорівнює `param_count`, автопілот ігнорує запит або надсилає повідомлення `STATUSTEXT` з попередженням про помилковий індекс.
* Якщо `param_index == -1`: автопілот виконує пошук за рядком `param_id`. Це операція з часовою складністю `O(N)`, яка вимагає побайтового порівняння рядків з усіма параметрами в пам'яті. Якщо параметр з такою назвою не знайдено, автопілот не генерує відповіді `PARAM_VALUE`, а наземна станція фіксує таймаут операції читання.

:::tabs
```c
/* Бінарна структура повідомлення PARAM_REQUEST_READ */
typedef struct __mavlink_param_request_read_t {
    int16_t param_index;      /* індекс або -1 */
    uint8_t target_system;    /* ID системи */
    uint8_t target_component; /* ID компонента */
    char    param_id[16];     /* назва */
} mavlink_param_request_read_t;

/* Складання запиту за індексом */
void make_read_by_index_request(mavlink_param_request_read_t *req,
                                uint8_t target_sys, uint8_t target_comp,
                                int16_t index) {
    req->target_system = target_sys;
    req->target_component = target_comp;
    req->param_index = index;
    memset(req->param_id, 0, 16);
}

/* Складання запиту за назвою */
void make_read_by_name_request(mavlink_param_request_read_t *req,
                               uint8_t target_sys, uint8_t target_comp,
                               const char *name) {
    req->target_system = target_sys;
    req->target_component = target_comp;
    req->param_index = -1;
    strncpy(req->param_id, name, 16);
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <array>
#include <algorithm>

struct ParamRequestRead {
    int16_t index{-1};
    uint8_t target_system{1};
    uint8_t target_component{1};
    std::array<char, 16> id{};

    static ParamRequestRead by_index(uint8_t sys, uint8_t comp, int16_t idx) noexcept {
        ParamRequestRead req;
        req.target_system = sys;
        req.target_component = comp;
        req.index = idx;
        req.id.fill('\0');
        return req;
    }

    static ParamRequestRead by_name(uint8_t sys, uint8_t comp, std::string_view name) noexcept {
        ParamRequestRead req;
        req.target_system = sys;
        req.target_component = comp;
        req.index = -1;
        req.id.fill('\0');
        size_t to_copy = std::min(name.size(), req.id.size());
        std::copy_n(name.data(), to_copy, req.id.data());
        return req;
    }
};
```
:::

#### 4. PARAM_SET (ID #23)

Запит модифікації значення параметра. Надсилається наземною станцією для зміни конкретного налаштування на борту.

* **Тип взаємодії:** Адресний запит на зміну (станція → автопілот).
* **Відповідь:** Броадкаст-повідомлення `PARAM_VALUE` з фактично встановленим значенням.
* **Розмір корисного навантаження:** 23 байти.

```
Структура корисного навантаження PARAM_SET (23 байти):
  Зсув    Розмір   Тип        Назва поля        Призначення
  -----------------------------------------------------------------------------
  [0..3]  4 байти  float      param_value       Нове значення (IEEE 754 або bit-cast)
  [4]     1 байт   uint8_t    target_system     ID цільової системи
  [5]     1 байт   uint8_t    target_component  ID цільового компонента
  [6..21] 16 байт  char[16]   param_id          Назва параметра для запису
  [22]    1 байт   uint8_t    param_type        Тип значення з переліку MAV_PARAM_TYPE
```

Особливості обробки `PARAM_SET`:
1. Автопілот зобов'язаний перевірити назву параметра, права доступу та допустимий діапазон значень (min/max).
2. Якщо значення виходить за межі допустимого діапазону, автопілот обмежує його (clamp) до найближчої границі або ігнорує, але в будь-якому випадку **відповідає повідомленням `PARAM_VALUE`**, що містить фактичне поточне значення. Завдяки цьому станція завжди бачить реальний стан параметра після спроби запису.
3. Запис у постійну Flash-пам'ять або EEPROM/FRAM зазвичай виконується синхронно або ставиться в чергу фонового запису.

:::tabs
```c
/* Бінарна структура повідомлення PARAM_SET */
typedef struct __mavlink_param_set_t {
    float   param_value;      /* нове значення */
    uint8_t target_system;    /* ID цільової системи */
    uint8_t target_component; /* ID цільового компонента */
    char    param_id[16];     /* назва параметра */
    uint8_t param_type;       /* тип значення */
} mavlink_param_set_t;

/* Пакування цілого значення uint32 у float поле PARAM_SET */
void set_param_uint32(mavlink_param_set_t *set_msg,
                      uint8_t target_sys, uint8_t target_comp,
                      const char *name, uint32_t val) {
    set_msg->target_system = target_sys;
    set_msg->target_component = target_comp;
    strncpy(set_msg->param_id, name, 16);
    set_msg->param_type = MAV_PARAM_TYPE_UINT32;
    memcpy(&set_msg->param_value, &val, sizeof(float));
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <array>
#include <algorithm>
#include <bit>

struct ParamSetMsg {
    float raw_value{0.0f};
    uint8_t target_system{1};
    uint8_t target_component{1};
    std::array<char, 16> id{};
    uint8_t type{0};

    static ParamSetMsg make_float(uint8_t sys, uint8_t comp,
                                  std::string_view name, float val) noexcept {
        ParamSetMsg msg;
        msg.target_system = sys;
        msg.target_component = comp;
        msg.type = 9; /* MAV_PARAM_TYPE_REAL32 */
        msg.raw_value = val;
        msg.id.fill('\0');
        std::copy_n(name.data(), std::min(name.size(), msg.id.size()), msg.id.data());
        return msg;
    }

    static ParamSetMsg make_uint32(uint8_t sys, uint8_t comp,
                                   std::string_view name, uint32_t val) noexcept {
        ParamSetMsg msg;
        msg.target_system = sys;
        msg.target_component = comp;
        msg.type = 5; /* MAV_PARAM_TYPE_UINT32 */
        msg.raw_value = std::bit_cast<float>(val);
        msg.id.fill('\0');
        std::copy_n(name.data(), std::min(name.size(), msg.id.size()), msg.id.data());
        return msg;
    }
};
```
:::

---

### Структури повідомлень розширеного протоколу (Parameter Extended Protocol)

Розширений протокол параметрів створений для усунення фундаментальних обмежень стандартного протоколу: відсутності підтримки 64-бітних типів, неможливості передачі довільних бінарних структур або рядкових значень конфігурації та відсутності явного статусу квитування операцій.

У розширеному протоколі замість 4-байтового `float` використовується універсальний 128-байтний сирий буфер `param_value[128]`.

#### 1. Коди результату підтвердження: перелік PARAM_ACK

Розширений протокол використовує явні коди квитування операцій у повідомленні `PARAM_EXT_ACK`:

| Код | Символьна назва | Опис результату |
| :--- | :--- | :--- |
| **0** | `PARAM_ACK_ACCEPTED` | Параметр успішно перевірено, збережено в оперативну пам'ять та зафіксовано в енергонезалежному сховищі. |
| **1** | `PARAM_ACK_VALUE_UNSUPPORTED` | Запропоноване значення виходить за межі допустимого діапазону або неприпустиме для даної конфігурації системи. |
| **2** | `PARAM_ACK_FAILED` | Критична помилка запису: збій Flash-пам'яті, спроба запису параметра «тільки для читання» або блокування системи у польоті. |
| **3** | `PARAM_ACK_IN_PROGRESS` | Операція триває у фоні (наприклад, виконується калібрування сенсорів або тривале стирання сектору EEPROM). |

#### 2. PARAM_EXT_REQUEST_LIST (ID #321)

Повідомлення запиту повного списку розширених параметрів.

```
Структура PARAM_EXT_REQUEST_LIST (2 байти):
  Зсув  Розмір  Тип      Назва поля        Призначення
  -----------------------------------------------------------------------------
  [0]   1 байт  uint8_t  target_system     ID системи-адресата
  [1]   1 байт  uint8_t  target_component  ID компонента-адресата
```

#### 3. PARAM_EXT_VALUE (ID #322)

Повідомлення передачі значення розширеного параметра. Загальний розмір корисного навантаження — 149 байтів.

```
Структура PARAM_EXT_VALUE (149 байтів):
  Зсув      Розмір     Тип        Назва поля    Призначення
  -----------------------------------------------------------------------------
  [0..1]    2 байти    uint16_t   param_count   Загальна кількість параметрів
  [2..3]    2 байти    uint16_t   param_index   Індекс поточного параметра (0..count-1)
  [4..19]   16 байтів  char[16]   param_id      16-байтна назва ASCII
  [20..147] 128 байтів char[128]  param_value   Буфер сирих бінарних даних
  [148]     1 байт     uint8_t    param_type    Тип даних з переліку MAV_PARAM_TYPE
```

:::tabs
```c
/* Бінарна структура повідомлення PARAM_EXT_VALUE */
typedef struct __mavlink_param_ext_value_t {
    uint16_t param_count;     /* загальна кількість */
    uint16_t param_index;     /* числовий індекс */
    char     param_id[16];    /* 16-байтна назва */
    char     param_value[128];/* 128-байтний буфер даних */
    uint8_t  param_type;      /* MAV_PARAM_TYPE */
} mavlink_param_ext_value_t;

/* Вичитування 64-бітного беззнакового цілого з розширеного буфера */
uint64_t get_ext_param_uint64(const mavlink_param_ext_value_t *msg) {
    uint64_t val = 0;
    memcpy(&val, msg->param_value, sizeof(uint64_t));
    return val;
}

/* Вичитування 64-бітного float подвійної точності */
double get_ext_param_real64(const mavlink_param_ext_value_t *msg) {
    double val = 0.0;
    memcpy(&val, msg->param_value, sizeof(double));
    return val;
}
```
```cpp
#include <cstdint>
#include <array>
#include <cstring>
#include <span>
#include <string_view>

struct ParamExtValueMsg {
    uint16_t count{0};
    uint16_t index{0};
    std::array<char, 16> id{};
    std::array<uint8_t, 128> raw_data{};
    uint8_t type{0};

    [[nodiscard]] uint64_t as_uint64() const noexcept {
        uint64_t val = 0;
        std::memcpy(&val, raw_data.data(), sizeof(uint64_t));
        return val;
    }

    [[nodiscard]] int64_t as_int64() const noexcept {
        int64_t val = 0;
        std::memcpy(&val, raw_data.data(), sizeof(int64_t));
        return val;
    }

    [[nodiscard]] double as_double() const noexcept {
        double val = 0.0;
        std::memcpy(&val, raw_data.data(), sizeof(double));
        return val;
    }

    [[nodiscard]] std::span<const uint8_t> as_custom_blob() const noexcept {
        return std::span<const uint8_t>(raw_data.data(), raw_data.size());
    }
};
```
:::

#### 4. PARAM_EXT_REQUEST_READ (ID #320)

Запит на читання одного розширеного параметра за числовим номером або назвою.

```
Структура PARAM_EXT_REQUEST_READ (20 байтів):
  Зсув    Розмір   Тип        Назва поля        Призначення
  -----------------------------------------------------------------------------
  [0..1]  2 байти  int16_t    param_index       Індекс (>= 0) або -1 для пошуку за назвою
  [2]     1 байт   uint8_t    target_system     ID системи-адресата
  [3]     1 байт   uint8_t    target_component  ID компонента-адресата
  [4..19] 16 байт  char[16]   param_id          Назва параметра
```

#### 5. PARAM_EXT_SET (ID #323)

Запит на зміну розширеного параметра. Загальний розмір — 147 байтів.

```
Структура PARAM_EXT_SET (147 байтів):
  Зсув      Розмір     Тип        Назва поля        Призначення
  -----------------------------------------------------------------------------
  [0]       1 байт     uint8_t    target_system     ID цільової системи
  [1]       1 байт     uint8_t    target_component  ID цільового компонента
  [2..17]   16 байтів  char[16]   param_id          Назва параметра
  [18..145] 128 байтів char[128]  param_value       Буфер нового значення
  [146]     1 байт     uint8_t    param_type        Тип параметра з MAV_PARAM_TYPE
```

#### 6. PARAM_EXT_ACK (ID #324)

Повідомлення явного квитування операції модифікації або перевірки параметра в розширеному протоколі.

```
Структура PARAM_EXT_ACK (148 байтів):
  Зсув      Розмір     Тип        Назва поля    Призначення
  -----------------------------------------------------------------------------
  [0..15]   16 байтів  char[16]   param_id      Назва підтверджуваного параметра
  [16..143] 128 байтів char[128]  param_value   Фактичне значення на борту після операції
  [144]     1 байт     uint8_t    param_type    Тип параметра з MAV_PARAM_TYPE
  [145]     1 байт     uint8_t    param_result  Результат виконання з переліку PARAM_ACK
```

:::tabs
```c
/* Бінарна структура повідомлення PARAM_EXT_ACK */
typedef struct __mavlink_param_ext_ack_t {
    char    param_id[16];     /* назва параметра */
    char    param_value[128]; /* підтверджене значення */
    uint8_t param_type;       /* MAV_PARAM_TYPE */
    uint8_t param_result;     /* результат операції (PARAM_ACK) */
} mavlink_param_ext_ack_t;

/* Перевірка успішності запису розширеного параметра */
bool is_ext_param_write_successful(const mavlink_param_ext_ack_t *ack) {
    return (ack->param_result == 0); /* 0 == PARAM_ACK_ACCEPTED */
}
```
```cpp
#include <cstdint>
#include <array>
#include <string_view>

enum class ParamAckResult : uint8_t {
    Accepted = 0,
    ValueUnsupported = 1,
    Failed = 2,
    InProgress = 3
};

struct ParamExtAckMsg {
    std::array<char, 16> id{};
    std::array<uint8_t, 128> value{};
    uint8_t type{0};
    ParamAckResult result{ParamAckResult::Failed};

    [[nodiscard]] bool is_accepted() const noexcept {
        return result == ParamAckResult::Accepted;
    }
};
```
:::

---

### Детальний аналіз побітового копіювання (Bit-casting) та перетворення типів

При роботі зі стандартним протоколом параметрів MAVLink виникає фундаментальна невідповідність між архітектурою повідомлення та типами даних: на рівні схеми повідомлення XML поле `param_value` задекларовано як `float` (32-бітне число з рухомою комою IEEE 754), однак логічно в ньому можуть передаватися цілі числа `uint8_t`, `int8_t`, `uint16_t`, `int16_t`, `uint32_t` або `int32_t`.

Згідно зі стандартом IEEE 754, формат одинарної точності `float` складається з трьох компонентів:
* 1 знаковий біт (`s`);
* 8 бітів експоненти (`e`) зі зміщенням 127;
* 23 біти мантиси (`m`) з неявним провідним бітом 1.

Це забезпечує рівно 24 біти двійкової точності (що відповідає приблизно 7.22 десятковим знакам). Якщо спробувати перетворити велике 32-бітне ціле число (наприклад, бітову маску сенсорів `0x80000001` або ціле значення `16777217`) за допомогою стандартного арифметичного приведення `(float)integer_value`, молодші розряди числа будуть округлені, а самі байти повністю зміняться відповідно до структури експоненти.

```
Початкове ціле число (uint32_t):
  Значення: 16777217  (0x01000001)
  Біти:     00000001 00000000 00000000 00000001

Результат числового приведення (float)16777217:
  Значення: 16777216.0 (0x4B800000)
  Біти:     01001011 10000000 00000000 00000000
  → Молодший біт безповоротно втрачено через брак розрядності мантиси!

Результат прямого побітового копіювання (memcpy / bit-cast):
  Біти:     00000001 00000000 00000000 00000001
  Як float: 2.3509887e-38 (не має математичного сенсу, але зберігає всі 32 біти)
```

Щоб зберегти цілісність даних, протокол MAVLink вимагає **побітового копіювання** (transposition / bit-cast): 4 байти цілого числа записуються в пам'ять поля `float` без будь-якої арифметичної зміни бітів.

:::tabs
```c
#include <stdint.h>
#include <string.h>

/* Безпечне пакування uint32 у float контейнер */
float pack_uint32_to_mavlink_float(uint32_t val) {
    float f;
    memcpy(&f, &val, sizeof(float));
    return f;
}

/* Безпечне розпакування float контейнера у uint32 */
uint32_t unpack_mavlink_float_to_uint32(float f) {
    uint32_t val;
    memcpy(&val, &f, sizeof(uint32_t));
    return val;
}

/* Безпечне розпакування float контейнера у int32 */
int32_t unpack_mavlink_float_to_int32(float f) {
    int32_t val;
    memcpy(&val, &f, sizeof(int32_t));
    return val;
}
```
```cpp
#include <cstdint>
#include <bit>
#include <concepts>

/* Сучасна ідіоматична C++20 реалізація через std::bit_cast (constexpr та zero-cost) */

template <std::integral T>
[[nodiscard]] constexpr float pack_integral_to_mavlink_float(T val) noexcept {
    static_assert(sizeof(T) <= sizeof(float), "Тип перевищує 32 біти контейнера");
    if constexpr (sizeof(T) == sizeof(float)) {
        return std::bit_cast<float>(val);
    } else {
        /* Для типів < 4 байтів вирівнюємо в uint32_t перед копіюванням */
        uint32_t wider = static_cast<uint32_t>(val);
        return std::bit_cast<float>(wider);
    }
}

template <std::integral T>
[[nodiscard]] constexpr T unpack_mavlink_float_to_integral(float f) noexcept {
    static_assert(sizeof(T) <= sizeof(float), "Тип перевищує 32 біти контейнера");
    if constexpr (sizeof(T) == sizeof(float)) {
        return std::bit_cast<T>(f);
    } else {
        uint32_t wider = std::bit_cast<uint32_t>(f);
        return static_cast<T>(wider);
    }
}
```
:::

---

### Порівняльний аналіз пропускної здатності та накладних витрат

При виборі між стандартним та розширеним протоколами параметрів інженер повинен враховувати суттєву різницю в розмірах кадрів та навантаженні на радіоканал.

| Характеристика протоколу | Standard Parameter Protocol | Parameter Extended Protocol |
| :--- | :--- | :--- |
| **Розмір корисного навантаження (Value)** | 25 байтів | 149 байтів |
| **Повний розмір кадру MAVLink v2** | 37 байтів (25 payload + 12 header/CRC) | 161 байт (149 payload + 12 header/CRC) |
| **Обсяг передачі 1500 параметрів** | 55.5 кілобайтів (≈ 444 кбіт) | 241.5 кілобайтів (≈ 1.93 Мбіт) |
| **Час завантаження при 57.6 кбіт/с** | ≈ 12–15 секунд | ≈ 50–60 секунд |
| **Підтримка типів > 32 біт** | Відсутня (вимагає дроблення або зрізання) | Повна (64-бітні цілі, double, бінарні структури) |
| **Квитування запису** | Неявне (броадкаст `PARAM_VALUE`) | Явне (`PARAM_EXT_ACK` з кодом результату) |

Через значно більший розмір кадру розширений протокол рідко використовується для повної початкової синхронізації всього дерева на вузькосмугових радіолініях. Замість цього в сучасних прошивках (PX4, ArduPilot) стандартний протокол застосовується як основний механізм передачі компактних числових налаштувань, а розширений протокол вмикається точково для специфічних вузлів (камери, підвіси, криптографічні модулі) або високошвидкісних ліній зв'язку Ethernet / USB.
