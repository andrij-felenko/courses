# ⚙️ Складання та читання повідомлень у FlatBuffers

FlatBuffers відрізняється від традиційних протоколів серіалізації відсутністю окремого етапу розбору (unpacking/parsing). Повідомлення конструюється безпосередньо у внутрішньому двійковому форматі, що дозволяє отримувачу читати будь-яке поле за постійний час O(1) без виділення проміжної пам'яті в RAM і без копіювання байтів.

Розгляньмо практичну реалізацію: формування пакета телеметрії польотного контролера (акселерометр, напруга батареї, назва профілю) та його безпечне читання з перевіркою цілісності буфера.

## Схема протоколу (.fbs)

Створимо файл опису схеми `telemetry.fbs`:

```flatbuffers
namespace Flight;

struct Vector3 {
    x: float;
    y: float;
    z: float;
}

table SensorReport {
    timestamp_s: uint32;
    sensor_id: uint32;
    temperature_c100: int32;
    battery_mv: uint32 = 3300; // значення за замовчуванням (не пишеться в буфер, якщо збігається)
    accel: Vector3;            // фіксована інлайн-структура (inline struct)
    device_name: string;       // динамічний рядок (зміщення на зовнішній буфер)
}

root_type SensorReport;
```

Компілятор `flatc` генерує заголовкові файли, що містять класи побудови (Builders) та типізовані акцесори до полів.

## Структури проти таблиць у FlatBuffers (Struct vs Table)

Схема FlatBuffers розрізняє два фундаментальні типи об'єктів:

1. **Фіксовані структури (`struct`)**:
   Оголошуються ключовим словом `struct` (наприклад, `Vector3`). Вони зберігаються в буфері суцільним двійковим блоком без використання віртуальних таблиць `vtable` та без заголовків зміщень.
   * **Переваги**: нульові накладні витрати на метадані, миттєвий доступ за фіксованим зміщенням, висока локальність кешу процесора.
   * **Обмеження**: розмір і склад полів фіксуються назавжди. У структуру не можна додавати або видаляти поля в майбутніх версіях схеми без порушення сумісності. Всі поля є обов'язковими.

2. **Гнучкі таблиці (`table`)**:
   Оголошуються ключовим словом `table` (наприклад, `SensorReport`). Кожне поле таблиці адресизується через таблицю віртуальних зміщень `vtable`.
   * **Переваги**: повна підтримка прямої та зворотної сумісності, можливість додавати нові поля або пропускати поля зі значеннями за замовчуванням.
   * **Ціна**: 2 байти в `vtable` на кожне оголошене поле плюс 4 байти зміщення на початку таблиці.

## Масиви та об'єднання (Vectors and Unions)

FlatBuffers надає високоефективні засоби роботи з колекціями та поліморфними даними:

* **Вектори структур (`[Vector3]`)**: укладаються в пам'яті суцільним масивом байтів із 4-байтовим префіксом кількості елементів. Читання такого вектора не потребує непрямої адресації — це прямий доступ до вказівника `const Vector3*`, який можна віддати алгоритмам SIMD або DSP.
* **Вектори таблиць (`[SensorReport]`)**: являють собою масив 32-бітних відносних зміщень на окремі таблиці. Це дозволяє кожному елементу масиву мати індивідуальну версію схеми та набір заповнених полів.
* **Динамічні об'єднання (`union`)**: реалізують безпечні варіанти (discriminated union). У буфері вони представляються парою: 1-байтним числовим полем типу (discriminant enum) та 32-бітним зміщенням на конкретну таблицю.

## Парадигма збирання «з кінця до початку» (Bottom-Up Layout)

Головна інженерна особливість генератора `FlatBufferBuilder` полягає в тому, що буфер формується від кінця виділеної пам'яті до її початку. 

Це зумовлено тим, що для запису батьківського об'єкта необхідно знати точні зміщення всіх його дочірніх елементів (рядків, векторів, вкладених таблиць). Оскільки розмір дочірніх елементів змінний, збирання «зліва направо» вимагало б багаторазового перерахунку й переміщення покажчиків у пам'яті. Збирання «справа наліво» (з кінця) дозволяє спочатку записати листки дерева даних (рядки та вектори), отримати їхні фіксовані адреси й після цього записати батьківську таблицю зі збереженням прямих числових зміщень.

Крім того, `FlatBufferBuilder` автоматично виконує дедуплікацію віртуальних таблиць: якщо кілька однакових об'єктів мають однакову розкладку полів, генератор створює лише одну `vtable` у буфері, а всі таблиці посилаються на неї, що значно скорочує підсумковий розмір пакета.

## Складання та доступ до полів у C та C++

У прикладі показано два боки взаємодії: генерацію буфера з кінця до початку та миттєве читання полів через віртуальну таблицю `vtable`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

// Приклад ручного кодека за специфікацією FlatBuffers Binary Wire Format
typedef struct {
    float x, y, z;
} Vector3;

// Побудова буфера FlatBuffers вручну (пам'ять заповнюється з кінця до початку)
typedef struct {
    uint8_t *buf;
    size_t   capacity;
    size_t   head; // курсор зміщення від початку буфера (росте вниз)
} FlatBuilder;

static void fb_init(FlatBuilder *b, uint8_t *buf, size_t cap) {
    b->buf = buf;
    b->capacity = cap;
    b->head = cap;
}

static uint32_t fb_push_bytes(FlatBuilder *b, const void *data, size_t size, size_t align) {
    // вирівнювання вниз
    size_t new_head = (b->head - size) & ~(align - 1);
    b->head = new_head;
    if (data) memcpy(&b->buf[b->head], data, size);
    return (uint32_t)(b->capacity - b->head); // зміщення від кінця
}

static uint32_t fb_create_string(FlatBuilder *b, const char *str) {
    size_t len = strlen(str);
    // 1 байт нуль-термінатора
    fb_push_bytes(b, "", 1, 1);
    // тіло рядка
    fb_push_bytes(b, str, len, 1);
    // довжина рядка uint32
    uint32_t l = (uint32_t)len;
    return fb_push_bytes(b, &l, 4, 4);
}

// Створення об'єкта SensorReport
static uint32_t fb_build_report(FlatBuilder *b, uint32_t ts, uint32_t id, int32_t temp,
                                uint32_t bat, const Vector3 *accel, const char *name) {
    // 1. Спочатку створюємо непрямі об'єкти (рядки)
    uint32_t name_offset = fb_create_string(b, name);

    // 2. Створюємо vtable (довжина vtable, довжина об'єкта, зсуви полів)
    // Поля: 0:ts (4), 1:id (4), 2:temp (4), 3:bat (4), 4:accel (12), 5:name (4)
    uint16_t vtable[8];
    vtable[0] = 8 * sizeof(uint16_t); // vtable_size = 16 Б
    vtable[1] = 4 + 4 + 4 + 4 + 4 + 12 + 4; // object_size = 36 Б
    vtable[2] = 4;   // offset field 0 (ts)
    vtable[3] = 8;   // offset field 1 (id)
    vtable[4] = 12;  // offset field 2 (temp)
    vtable[5] = (bat == 3300) ? 0 : 16; // 0 якщо дефолт!
    vtable[6] = 20;  // offset field 4 (accel struct)
    vtable[7] = 32;  // offset field 5 (name offset)

    // 3. Записуємо поля об'єкта в Table Data
    size_t table_start = (b->head - 36) & ~3;
    b->head = table_start;
    uint8_t *t = &b->buf[table_start];

    // Зсув до рядка name (відносний від позиції поля t[32])
    uint32_t rel_name = (uint32_t)((b->capacity - name_offset) - (table_start + 32));
    memcpy(&t[4],  &ts, 4);
    memcpy(&t[8],  &id, 4);
    memcpy(&t[12], &temp, 4);
    if (bat != 3300) memcpy(&t[16], &bat, 4);
    if (accel) memcpy(&t[20], accel, 12);
    memcpy(&t[32], &rel_name, 4);

    // 4. Записуємо vtable перед об'єктом і зв'язуємо відносним зсувом
    uint32_t vt_pos = fb_push_bytes(b, vtable, sizeof(vtable), 2);
    int32_t vt_offset = (int32_t)(b->capacity - vt_pos) - (int32_t)table_start;
    memcpy(&t[0], &vt_offset, 4); // перші 4 байти таблиці вказують на vtable

    return (uint32_t)(b->capacity - table_start);
}

// Завершення буфера: запис кореневого зсуву на початку
static size_t fb_finish(FlatBuilder *b, uint32_t root_offset) {
    uint32_t root_pos = (uint32_t)(b->capacity - root_offset);
    uint32_t rel_root = root_pos - (uint32_t)(b->head - 4);
    fb_push_bytes(b, &rel_root, 4, 4);
    return b->capacity - b->head;
}

// Пряме читання полів (Zero-Copy) без декодування
typedef struct {
    const uint8_t *table;
    const uint16_t *vtable;
    uint16_t vtable_size;
} SensorReportReader;

static bool fb_read_report(const uint8_t *buf, size_t len, SensorReportReader *r) {
    if (len < 8) return false;
    uint32_t root_offset;
    memcpy(&root_offset, buf, 4);
    if (root_offset + 4 > len) return false;

    r->table = buf + root_offset;
    int32_t vt_offset;
    memcpy(&vt_offset, r->table, 4);
    
    const uint8_t *vt_ptr = r->table - vt_offset;
    if (vt_ptr < buf || vt_ptr + 4 > buf + len) return false;

    r->vtable = (const uint16_t *)vt_ptr;
    r->vtable_size = r->vtable[0] / sizeof(uint16_t);
    return true;
}

static uint32_t get_timestamp(const SensorReportReader *r) {
    if (r->vtable_size <= 2 || r->vtable[2] == 0) return 0;
    uint32_t val;
    memcpy(&val, r->table + r->vtable[2], 4);
    return val;
}

static uint32_t get_battery(const SensorReportReader *r) {
    // Якщо зміщення 0 у vtable — повертаємо домовлене значення за замовчуванням
    if (r->vtable_size <= 5 || r->vtable[5] == 0) return 3300;
    uint32_t val;
    memcpy(&val, r->table + r->vtable[5], 4);
    return val;
}

static const char *get_name(const SensorReportReader *r) {
    if (r->vtable_size <= 7 || r->vtable[7] == 0) return "";
    uint32_t rel_offset;
    memcpy(&rel_offset, r->table + r->vtable[7], 4);
    const uint8_t *str_ptr = r->table + r->vtable[7] + rel_offset;
    return (const char *)(str_ptr + 4); // пропускаємо 4 байти довжини
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <string_view>
#include <span>
#include <optional>

// Типізований доступ до FlatBuffers буфера мовою C++
namespace flight {

struct alignas(4) Vector3 {
    float x;
    float y;
    float z;
};

class SensorReportView {
public:
    explicit SensorReportView(std::span<const uint8_t> buffer) noexcept
        : buffer_(buffer), table_(nullptr), vtable_(nullptr), vtable_entries_(0) {
        if (buffer.size() < 4) return;

        uint32_t root_offset = 0;
        std::memcpy(&root_offset, buffer.data(), sizeof(root_offset));
        if (root_offset + sizeof(int32_t) > buffer.size()) return;

        table_ = buffer.data() + root_offset;

        int32_t vt_offset = 0;
        std::memcpy(&vt_offset, table_, sizeof(vt_offset));
        const uint8_t* vt_ptr = table_ - vt_offset;

        if (vt_ptr < buffer.data() || vt_ptr + 2 > buffer.data() + buffer.size()) {
            table_ = nullptr;
            return;
        }

        vtable_ = reinterpret_cast<const uint16_t*>(vt_ptr);
        uint16_t vtable_byte_size = 0;
        std::memcpy(&vtable_byte_size, vtable_, sizeof(uint16_t));
        vtable_entries_ = vtable_byte_size / sizeof(uint16_t);
    }

    [[nodiscard]] bool is_valid() const noexcept { return table_ != nullptr; }

    [[nodiscard]] uint32_t timestamp_s() const noexcept {
        return read_field<uint32_t>(2, 0);
    }

    [[nodiscard]] uint32_t sensor_id() const noexcept {
        return read_field<uint32_t>(3, 0);
    }

    [[nodiscard]] int32_t temperature_c100() const noexcept {
        return read_field<int32_t>(4, 0);
    }

    [[nodiscard]] uint32_t battery_mv() const noexcept {
        return read_field<uint32_t>(5, 3300); // 3300 mV за замовчуванням
    }

    [[nodiscard]] std::optional<Vector3> accel() const noexcept {
        if (!has_field(6)) return std::nullopt;
        const uint16_t off = vtable_[6];
        Vector3 v{};
        std::memcpy(&v, table_ + off, sizeof(Vector3));
        return v;
    }

    [[nodiscard]] std::string_view device_name() const noexcept {
        if (!has_field(7)) return {};
        const uint16_t field_off = vtable_[7];
        const uint8_t* field_ptr = table_ + field_off;

        uint32_t rel_offset = 0;
        std::memcpy(&rel_offset, field_ptr, sizeof(rel_offset));
        const uint8_t* str_head = field_ptr + rel_offset;

        uint32_t len = 0;
        std::memcpy(&len, str_head, sizeof(len));
        const char* str_chars = reinterpret_cast<const char*>(str_head + 4);

        return std::string_view{str_chars, len};
    }

private:
    [[nodiscard]] bool has_field(size_t field_index) const noexcept {
        return is_valid() && (field_index < vtable_entries_) && (vtable_[field_index] != 0);
    }

    template <typename T>
    [[nodiscard]] T read_field(size_t field_index, T default_value) const noexcept {
        if (!has_field(field_index)) return default_value;
        const uint16_t offset = vtable_[field_index];
        T val{};
        std::memcpy(&val, table_ + offset, sizeof(T));
        return val;
    }

    std::span<const uint8_t> buffer_;
    const uint8_t* table_;
    const uint16_t* vtable_;
    size_t vtable_entries_;
};

} // namespace flight
```
:::

## Безпека та валідація буфера через Verifier

Оскільки читання FlatBuffers зводиться до арифметики зміщень над сирим буфером пам'яті, пошкоджений або зловмисний пакет із мережі може містити хибні зміщення, що призведуть до виходу за межі виділеного буфера (`Out-Of-Bounds Read`) або розіменування некоректних адрес.

Для захисту на вхідних шлюзах та мікроконтролерах використовується модуль `flatbuffers::Verifier`:
1. **Перевірка меж зміщень**: контролює, щоб кожен відносний зсув `vtable_offset`, покажчик таблиці чи рядка не виходив за фізичні межі вхідного масиву `[buffer, buffer + size]`.
2. **Перевірка вирівнювання**: переконується, що поля типів `uint32_t`, `float`, `uint64_t` розташовані за адресами, кратними їхньому розміру, що запобігає апаратним виняткам `HardFault` на процесорах Cortex-M0.
3. **Захист від зациклення**: виявляє та блокує циклічні посилання у вкладених структурах даних.
4. **Валідація рядків і масивів**: гарантує наявність нульового байта наприкінці рядка та коректність заявленої довжини елементів.

Час роботи верифікатора пропорційний розміру пакета O(N), проте його можна запускати лише один раз на вході мережевого драйвера перед передачею буфера прикладним підсистемам.

## Профілювання продуктивності на мікроконтролерах

На процесорі ARM Cortex-M4 з частотою 168 МГц пряме читання скалярного поля (наприклад, `battery_mv()`) через `ReadingView` займає лише 8–12 тактів процесора (менше 0.08 мікросекунди). Для порівняння, повна десеріалізація аналогічного повідомлення у Protobuf потребує від 500 до 1200 тактів.

Якщо програмі потрібно прочитати лише 1 або 2 поля з великого пакета телеметрії, FlatBuffers забезпечує прискорення у 50–100 разів порівняно з будь-яким класичним десеріалізатором.
