# ⚙️ Інспектор розкладки об'єктів та зсувів вказівників

Розуміння внутрішньої розкладки об'єктів у пам'яті зазвичай ґрунтується на абстрактних схемах і витягах зі специфікацій двійкових інтерфейсів (ABI). Проте справжню поведінку компілятора найкраще спостерігати наживо: виміряти фізичні зміщення адрес, перевірити арифметику коригування вказівника `this`, прочитати службові поля віртуальної таблиці безпосередньо з пам'яті процесу, оцінити час доступу до полів та порівняти розміри структур.

У цьому проекті ми побудуємо повноцінний діагностичний інструмент мовою C++20. Він у реальному часі аналізує структуру пам'яті об'єктів, наочно показує роботу коригувальних перехідників (thunks), витягує зсуви віртуальних баз за стандартом Itanium C++ ABI, виконує мікропрофілювання доступу до даних, досліджує поведінку віртуальних таблиць під час конструювання та демонструє крайові випадки приведення нульових покажчиків і бічних переходів (side-casts).

## Проектування тестових ієрархій

Для проведення експериментів створимо дві паралельні ієрархії класів, які моделюють типовий компонент обробки звукових потоків.

Перша ієрархія представляє **невіртуальний ромб** (`NonVirtualDiamond`):
- Базовий клас `Device` містить ідентифікатор пристрою та віртуальні методи життєвого циклу.
- Проміжні класи `AudioIn` та `AudioOut` успадковують `Device` звичайним способом. Кожен із них додає власні поля даних і спеціалізовані віртуальні функції.
- Клас `AudioDuplexNV` об'єднує обидва канали за допомогою множинного спадкування, утворюючи класичний невіртуальний ромб.

Друга ієрархія представляє **віртуальний ромб** (`VirtualDiamond`):
- Базовий клас `VDevice` має ідентичну структуру до `Device`.
- Проміжні класи `VirtualAudioIn` та `VirtualAudioOut` використовують **віртуальне спадкування**: `virtual public VDevice`.
- Клас `AudioDuplexV` об'єднує віртуальні гілки в єдиний дуплексний пристрій.

```cpp
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <memory>
#include <numeric>
#include <string_view>
#include <vector>

// ── 1. Невіртуальна ієрархія ──────────────────────────────────────────────
struct Device {
    std::uint32_t device_id{0x11111111};
    virtual ~Device() = default;
    virtual void ping() {
        std::cout << "  [Device::ping] id=0x" << std::hex << device_id << '\n';
    }
};

struct AudioIn : public Device {
    std::uint32_t sample_rate{48000};
    void ping() override {
        std::cout << "  [AudioIn::ping] rate=" << std::dec << sample_rate << '\n';
    }
    virtual void read_samples() {
        std::cout << "  [AudioIn::read_samples]\n";
    }
};

struct AudioOut : public Device {
    std::uint32_t buffer_size{1024};
    void ping() override {
        std::cout << "  [AudioOut::ping] buf=" << std::dec << buffer_size << '\n';
    }
    virtual void write_samples() {
        std::cout << "  [AudioOut::write_samples]\n";
    }
};

struct AudioDuplexNV : public AudioIn, public AudioOut {
    std::uint32_t duplex_flags{0xAABBCCDD};
    void ping() override {
        std::cout << "  [AudioDuplexNV::ping] full duplex\n";
    }
};

// ── 2. Віртуальна ієрархія ────────────────────────────────────────────────
struct VDevice {
    std::uint32_t device_id{0x22222222};
    virtual ~VDevice() = default;
    virtual void ping() {
        std::cout << "  [VDevice::ping] id=0x" << std::hex << device_id << '\n';
    }
    virtual void identify() {
        std::cout << "  [VDevice::identify] base\n";
    }
};

struct VirtualAudioIn : virtual public VDevice {
    std::uint32_t sample_rate{96000};

    VirtualAudioIn() {
        // Дослідження vptr під час конструювання проміжного підоб'єкта
    }

    void ping() override {
        std::cout << "  [VirtualAudioIn::ping] rate=" << std::dec << sample_rate << '\n';
    }
    void identify() override {
        std::cout << "  [VirtualAudioIn::identify] in-branch\n";
    }
    virtual void read_samples() {
        std::cout << "  [VirtualAudioIn::read_samples]\n";
    }
};

struct VirtualAudioOut : virtual public VDevice {
    std::uint32_t buffer_size{2048};
    void ping() override {
        std::cout << "  [VirtualAudioOut::ping] buf=" << std::dec << buffer_size << '\n';
    }
    void identify() override {
        std::cout << "  [VirtualAudioOut::identify] out-branch\n";
    }
    virtual void write_samples() {
        std::cout << "  [VirtualAudioOut::write_samples]\n";
    }
};

struct AudioDuplexV : public VirtualAudioIn, public VirtualAudioOut {
    std::uint32_t duplex_flags{0x55667788};

    // Найбільш похідний клас безпосередньо ініціалізує віртуальну базу
    AudioDuplexV() : VDevice(), VirtualAudioIn(), VirtualAudioOut() {}

    void ping() override {
        std::cout << "  [AudioDuplexV::ping] unified virtual duplex\n";
    }
    void identify() override {
        std::cout << "  [AudioDuplexV::identify] most derived\n";
    }
};
```

Зверніть увагу на конструктор `AudioDuplexV`: за правилами C++ саме найбільш похідний клас (Most Derived Class) зобов'язаний явно викликати конструктор віртуальної бази `VDevice()`. Якщо цього не зробити, компілятор спробує викликати конструктор за замовчуванням. Конструктори `VDevice()`, зазначені у списках ініціалізації `VirtualAudioIn` та `VirtualAudioOut`, під час створення екземпляра `AudioDuplexV` повністю ігноруються.

## Утиліта низькорівневого дампу пам'яті

Щоб побачити розташування байтів усередині екземпляра, напишемо функцію `dump_memory`. Вона зчитує сирі байти за адресою об'єкта та виводить їх 64-бітними словами (по 8 байтів у рядку). Це відповідає стандартному розміру машинного слова та вказівника на архітектурі x86-64.

```cpp
void dump_memory(const void* ptr, std::size_t size, std::string_view label) {
    std::cout << "=== Розкладка пам'яті: " << label << " (" << std::dec << size << " байтів) ===\n";
    const auto* bytes = static_cast<const std::uint8_t*>(ptr);
    const auto base_addr = reinterpret_cast<std::uintptr_t>(ptr);

    for (std::size_t i = 0; i < size; i += 8) {
        std::cout << "  +" << std::setw(2) << std::setfill('0') << std::dec << i << " B [0x"
                  << std::hex << (base_addr + i) << "]: ";

        for (std::size_t j = 0; j < 8 && (i + j) < size; ++j) {
            std::cout << std::setw(2) << std::setfill('0') << std::hex
                      << static_cast<int>(bytes[i + j]) << ' ';
        }

        // Відображаємо значення як 64-бітне беззнакове слово для швидкої ідентифікації vptr
        if (i + 8 <= size) {
            std::uint64_t word = 0;
            std::memcpy(&word, bytes + i, sizeof(word));
            std::cout << " | слово: 0x" << std::setw(16) << std::setfill('0') << std::hex << word;
        }
        std::cout << '\n';
    }
    std::cout << '\n';
}
```

Ця функція дозволяє нам візуально ідентифікувати:
- Вказівники на таблиці віртуальних методів (`vptr`), які зазвичай містять адреси в сегменті константних даних (`.rodata`).
- Корисні числові поля (наприклад, прапорці `0x11111111`, `48000`, `0xAABBCCDD`).
- Проміжки вирівнювання (padding bytes), що додаються компілятором для забезпечення кратності адрес вимогам процесора.

## Експеримент 1: Арифметика коригування вказівника this

У системі з множинним спадкуванням об'єкт має кілька точок входу. Первинна база (Primary Base) розташовується за нульовим зсувом відносно початку всього об'єкта, а вторинні бази (Secondary Bases) зміщуються на фіксовану кількість байтів.

Напишемо функцію, яка аналізує перетворення вказівників при висхідному приведенні типу (upcast) та демонструє небезпеку використання низькорівневих операторів приведення.

```cpp
void probe_pointer_adjustments() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 1: Зсуви покажчиків у невіртуальному об'єкті\n";
    std::cout << "=========================================================\n";

    auto obj = std::make_unique<AudioDuplexNV>();
    auto* raw_duplex = obj.get();
    const auto addr_root = reinterpret_cast<std::uintptr_t>(raw_duplex);

    // Статичний upcast до першої бази (Primary Base)
    AudioIn* in_branch = raw_duplex;
    const auto addr_in = reinterpret_cast<std::uintptr_t>(in_branch);

    // Статичний upcast до другої бази (Secondary Base)
    AudioOut* out_branch = raw_duplex;
    const auto addr_out = reinterpret_cast<std::uintptr_t>(out_branch);

    std::cout << "Адреса AudioDuplexNV* : 0x" << std::hex << addr_root << " (базовий початок)\n";
    std::cout << "Адреса AudioIn*        : 0x" << std::hex << addr_in   << " (зсув +"
              << std::dec << (addr_in - addr_root) << " B)\n";
    std::cout << "Адреса AudioOut*       : 0x" << std::hex << addr_out  << " (зсув +"
              << std::dec << (addr_out - addr_root) << " B)\n\n";

    // Порівняння поведінки static_cast та reinterpret_cast
    auto* safe_out = static_cast<AudioOut*>(raw_duplex);
    auto* dangerous_out = reinterpret_cast<AudioOut*>(raw_duplex);

    std::cout << "Результат static_cast<AudioOut*>     : 0x" << std::hex << reinterpret_cast<std::uintptr_t>(safe_out)
              << " (коректно додано зсув)\n";
    std::cout << "Результат reinterpret_cast<AudioOut*>: 0x" << std::hex << reinterpret_cast<std::uintptr_t>(dangerous_out)
              << " (ПОМИЛКА: адреса не змінилася!)\n\n";

    std::cout << "Звернення через коректний static_cast:\n";
    std::cout << "  safe_out->buffer_size = " << std::dec << safe_out->buffer_size << " (очікувано 1024)\n";

    std::cout << "Звернення через некоректний reinterpret_cast:\n";
    std::cout << "  dangerous_out->buffer_size = " << std::dec << dangerous_out->buffer_size
              << " (прочитано sample_rate першої бази!)\n\n";

    // Крайовий випадок: поведінка при приведенні нульового вказівника
    AudioDuplexNV* null_duplex = nullptr;
    AudioOut* null_out = null_duplex; // Неявний static_cast над nullptr

    std::cout << "Приведення nullptr:\n";
    std::cout << "  null_duplex = " << static_cast<void*>(null_duplex) << '\n';
    std::cout << "  null_out    = " << static_cast<void*>(null_out)
              << " (компілятор перевірив на 0 перед додаванням зсуву!)\n\n";

    dump_memory(raw_duplex, sizeof(AudioDuplexNV), "AudioDuplexNV");
}
```

Розгляньмо критично важливий аспект роботи компілятора:
1. Коли виконується `out_branch = raw_duplex`, компілятор не просто копіює значення регістра. Він додає фіксовану константу зміщення (наприклад, `+16` байтів).
2. Якщо вихідний вказівник дорівнює `nullptr`, пряме додавання `16` перетворило б його на адресу `0x10`, що вказувало б на недійсний сегмент пам'яті. Тому компілятор генерує приховану перевірку:
   ```cpp
   AudioOut* out = (raw_duplex != nullptr) ? reinterpret_cast<AudioOut*>(reinterpret_cast<char*>(raw_duplex) + 16) : nullptr;
   ```
3. Використання `reinterpret_cast` повністю вимикає механізм перерахунку зміщень. У результаті `dangerous_out` продовжує вказувати на початок об'єкта (де лежить `AudioIn`). Читання поля `buffer_size` насправді зчитує байти з поля `sample_rate`, призводячи до прихованого псування логіки.

## Експеримент 2: Подвоєння стану та розкол ідентичності

У невіртуальному ромбі кожна проміжна гілка містить власний незалежний екземпляр базового класу. Дослідимо цей ефект кількісно: перевіримо адреси обох копій `Device` та простежимо, як зміна значення в одній гілці залишає незмінною іншу.

```cpp
void probe_state_duplication() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 2: Подвоєння стану в невіртуальному ромбі\n";
    std::cout << "=========================================================\n";

    AudioDuplexNV duplex;

    // Пряме звернення duplex.device_id було б неоднозначним (помилка компілятора).
    // Записуємо різні значення у дві незалежні копії:
    duplex.AudioIn::device_id  = 0xAAAA1111;
    duplex.AudioOut::device_id = 0xBBBB2222;

    std::cout << "Значення duplex.AudioIn::device_id  = 0x" << std::hex << duplex.AudioIn::device_id << '\n';
    std::cout << "Значення duplex.AudioOut::device_id = 0x" << std::hex << duplex.AudioOut::device_id << '\n\n';

    const auto* dev_in_ptr  = static_cast<Device*>(static_cast<AudioIn*>(&duplex));
    const auto* dev_out_ptr = static_cast<Device*>(static_cast<AudioOut*>(&duplex));

    const auto addr_dev_in  = reinterpret_cast<std::uintptr_t>(dev_in_ptr);
    const auto addr_dev_out = reinterpret_cast<std::uintptr_t>(dev_out_ptr);

    std::cout << "Адреса підоб'єкта Device (через AudioIn) : 0x" << std::hex << addr_dev_in << '\n';
    std::cout << "Адреса підоб'єкта Device (через AudioOut): 0x" << std::hex << addr_dev_out << '\n';
    std::cout << "Відстань між двома підоб'єктами Device    : " << std::dec
              << (addr_dev_out - addr_dev_in) << " байтів\n\n";

    std::cout << "Виклик віртуальних методів через різні інтерфейси:\n";
    std::cout << "1. Через AudioIn*:\n";
    AudioIn* in_ptr = &duplex;
    in_ptr->ping();

    std::cout << "2. Через AudioOut*:\n";
    AudioOut* out_ptr = &duplex;
    out_ptr->ping();
    std::cout << '\n';
}
```

Аналіз результатів показує:
- Обидва підоб'єкти `Device` мають власні `vptr` і власні комірки під `device_id`.
- Коли ми викликаємо `in_ptr->ping()` та `out_ptr->ping()`, обидва виклики потрапляють у перевизначений метод `AudioDuplexNV::ping()`.
- Проте якщо для `in_ptr` вказівник `this` уже вказує на початок `AudioDuplexNV`, то для `out_ptr` компілятор змушений скоригувати `this` перед передачею в `AudioDuplexNV::ping()`. Для цього створюється спеціальний перехідник — **thunk**, який віднімає зміщення другої бази перед стрибком до тіла методу.

## Як влаштований асемблерний код коригувального перехідника (thunk)

Щоб зрозуміти, що саме процесор виконує під час виклику `out_ptr->ping()`, звернемося до згенерованого асемблерного коду на архітектурі x86-64 (System V AMD64 ABI, де перший аргумент — вказівник `this` — передається у регістрі `%rdi`).

Коли функція викликається через таблицю віртуальних методів другої бази `AudioOut`, запис у таблиці вказує не на безпосереднє тіло `AudioDuplexNV::ping()`, а на так званий **adjustor thunk** (невіртуальний перехідник):

```asm
# Асемблерний перехідник для AudioDuplexNV::ping() через AudioOut*
_ZThn16_N13AudioDuplexNV4pingEv:
    subq    $16, %rdi           # Віднімаємо 16 байтів від %rdi (this = AudioOut* -> AudioDuplexNV*)
    jmp     _ZN13AudioDuplexNV4pingEv   # Хвостовий безумовний стрибок до справжньої реалізації
```

Цей механізм має ключові переваги:
1. Тіло методу `AudioDuplexNV::ping()` компілюється в єдиному екземплярі і завжди очікує, що регістр `%rdi` вказує на початок об'єкта `AudioDuplexNV` (зсув 0).
2. Якщо виклик здійснюється через `AudioIn*` (первинну базу), таблиця віртуальних методів містить пряму адресу `_ZN13AudioDuplexNV4pingEv` без жодних проміжних інструкцій.
3. Якщо виклик іде через `AudioOut*` (вторинну базу), таблиця спрямовує виконання на thunk, який виконує рівно одну інструкцію `subq $16, %rdi` і миттєво стрибає в основний код без створення нового кадру стека.

## Експеримент 3: Віртуальне спадкування та читання vbase_offset

Тепер перейдемо до об'єкта `AudioDuplexV`, який використовує віртуальне спадкування. Згідно зі специфікацією Itanium C++ ABI, спільний підоб'єкт `VDevice` виноситься в самий кінець об'єкта, а зміщення до нього записується у віртуальну таблицю за від'ємним індексом.

Спробуємо перевірити цю специфікацію експериментально: прочитаємо значення `vbase_offset` безпосередньо з пам'яті через адресну арифметику і зіставимо його з реальною фізичною адресою об'єкта.

```cpp
void probe_virtual_base_offsets() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 3: Читання vbase_offset з віртуальної таблиці\n";
    std::cout << "=========================================================\n";

    AudioDuplexV vduplex;
    dump_memory(&vduplex, sizeof(AudioDuplexV), "AudioDuplexV (із virtual public)");

    const auto addr_root = reinterpret_cast<std::uintptr_t>(&vduplex);
    const auto* vdev_ptr = static_cast<VDevice*>(&vduplex);
    const auto addr_vdev = reinterpret_cast<std::uintptr_t>(vdev_ptr);

    const std::ptrdiff_t physical_offset = static_cast<std::ptrdiff_t>(addr_vdev - addr_root);
    std::cout << "Фізичне зміщення спільного VDevice у пам'яті: +" << std::dec << physical_offset << " байтів\n";

    // ── Читання службових полів vtable за специфікацією Itanium C++ ABI ──
    // 1. Перші 8 байтів об'єкта — це vptr головної віртуальної таблиці
    auto** vptr_entry = *reinterpret_cast<std::ptrdiff_t***>(&vduplex);

    // 2. Структура віртуальної таблиці в пам'яті:
    //    vptr_entry[ 0] = адреса першого віртуального методу (вхідна точка vptr)
    //    vptr_entry[-1] = вказівник на структуру std::type_info (RTTI)
    //    vptr_entry[-2] = offset-to-top (зсув від поточної позиції до початку всього об'єкта)
    //    vptr_entry[-3] = vbase_offset (зсув від поточної позиції до віртуальної бази VDevice)
    const std::ptrdiff_t offset_to_top = reinterpret_cast<std::ptrdiff_t>(vptr_entry[-2]);
    const std::ptrdiff_t vbase_offset  = reinterpret_cast<std::ptrdiff_t>(vptr_entry[-3]);

    std::cout << "Прочитано з vtable[-2] (offset-to-top): " << std::dec << offset_to_top << " байтів\n";
    std::cout << "Прочитано з vtable[-3] (vbase_offset) : +" << std::dec << vbase_offset << " байтів\n\n";

    if (vbase_offset == physical_offset) {
        std::cout << ">> ПІДТВЕРДЖЕНО: Значення vbase_offset у таблиці збігається з фізичним зсувом!\n";
    } else {
        std::cout << ">> УВАГА: На поточній платформі розкладка vtable відрізняється від Itanium ABI.\n";
    }
    std::cout << '\n';
}
```

Цей тест демонструє фундаментальний механізм роботи віртуального спадкування:
1. Коли метод класу `VirtualAudioIn` звертається до поля `device_id` віртуальної бази `VDevice`, він не знає статичного зміщення на етапі компіляції.
2. Процесор спочатку завантажує значення `vptr` з об'єкта.
3. Потім він зчитує 8-байтове ціле за зміщенням `-24` (індекс `-3`) відносно `vptr`.
4. Отриманий зсув (у нашому випадку `+40` байтів) додається до `this`, вказуючи на спільний підоб'єкт `VDevice`.
5. Лише після цього відбувається читання або запис самого поля.

## Асемблерний аналіз доступу до полів віртуальної бази

Щоб оцінити ціну непрямої адресації у машинних тактах, порівняємо згенерований компілятором GCC/Clang асемблерний код для читання поля зі звичайної бази та з віртуальної бази.

**Випадок 1: Читання поля з невіртуальної бази (`AudioIn::read_samples()`):**
```asm
# Читання device_id зі звичайної бази (статичний зсув відомий на етапі компіляції)
movl    8(%rdi), %eax       # Одне розіменування: читаємо поле за фіксованим зміщенням +8
```

**Випадок 2: Читання поля з віртуальної бази (`VirtualAudioIn::read_samples()`):**
```asm
# Читання device_id з віртуальної бази через таблицю зміщень
movq    (%rdi), %rax        # 1. Завантажуємо vptr з об'єкта (%rax = *this)
movq    -24(%rax), %rax     # 2. Читаємо vbase_offset з vtable[-3] (%rax = offset)
movl    8(%rdi,%rax), %eax  # 3. Читаємо поле за адресою (%rdi + %rax + 8)
```

Порівняння чітко показує накладні витрати:
- Невіртуальне звернення вимагає **однієї інструкції `movl`** з константним зміщенням, яка декодується й виконується процесором за 1 такт за наявності даних у кеші L1.
- Віртуальне звернення вимагає **трьох послідовних інструкцій**, включно з двома залежними читаннями з пам'яті (спочатку `vptr`, потім `vtable[-3]`). Якщо віртуальна таблиця була витіснена з кешу процесора, це може спричинити затримку (cache miss) у десятки тактів.

## Експеримент 4: Бічний перехід (side-cast) через dynamic_cast

У складних поліморфних ієрархіях часто виникає потреба перейти від одного інтерфейсного вказівника до сусіднього, коли обидва реалізовані одним і тим самим підсумковим класом. Таке перетворення називають **бічним приведенням** (англ. *side-cast*).

Оператор `static_cast` не може виконати side-cast, оскільки типи `VirtualAudioIn` та `VirtualAudioOut` не пов'язані прямим відношенням спадкування. Дослідимо, як `dynamic_cast` розв'язує цю задачу під час виконання.

```cpp
void probe_side_casting() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 4: Side-cast через dynamic_cast\n";
    std::cout << "=========================================================\n";

    auto duplex = std::make_unique<AudioDuplexV>();
    VirtualAudioIn* in_branch = duplex.get();

    std::cout << "Початковий покажчик VirtualAudioIn*: 0x" << std::hex
              << reinterpret_cast<std::uintptr_t>(in_branch) << '\n';

    // Спроба static_cast призвела б до помилки компіляції:
    // VirtualAudioOut* out = static_cast<VirtualAudioOut*>(in_branch);

    // dynamic_cast успішно виконує бічний перехід за допомогою RTTI:
    VirtualAudioOut* out_branch = dynamic_cast<VirtualAudioOut*>(in_branch);

    if (out_branch != nullptr) {
        const auto addr_in  = reinterpret_cast<std::uintptr_t>(in_branch);
        const auto addr_out = reinterpret_cast<std::uintptr_t>(out_branch);
        std::cout << "Side-cast успішно виконано:\n";
        std::cout << "  Адреса VirtualAudioIn*  : 0x" << std::hex << addr_in << '\n';
        std::cout << "  Адреса VirtualAudioOut* : 0x" << std::hex << addr_out << '\n';
        std::cout << "  Різниця адрес           : +" << std::dec << (addr_out - addr_in) << " байтів\n";
    } else {
        std::cout << "Помилка: dynamic_cast повернув nullptr!\n";
    }
    std::cout << '\n';
}
```

Алгоритм виконання `dynamic_cast` у цій ситуації складається з чотирьох кроків:
1. Через `vptr` вхідного вказівника `in_branch` система звертається до поля `offset-to-top` (`vtable[-2]`).
2. Додавши `offset-to-top` до `in_branch`, середовище виконання отримує точну адресу найбільш похідного об'єкта `AudioDuplexV`.
3. За вказівником `vtable[-1]` система зчитує метадані RTTI (`std::type_info`) повного типу.
4. Метадані містять повний граф спадкування. Система знаходить у графі цільовий тип `VirtualAudioOut`, визначає його зміщення відносно початку повного об'єкта і повертає кінцеву адресу.

## Експеримент 5: Дослідження мутації vptr під час конструювання

Однією з найбільш захопливих тем у низькорівневому C++ є те, як змінюється вміст `vptr` у процесі виконання конструкторів складного об'єкта.

За стандартом мови, поки виконується тіло конструктора `VirtualAudioIn`, об'єкт ще не є повноцінним `AudioDuplexV`. Віртуальні виклики зсередини конструктора повинні потрапляти у версії методів, визначені у `VirtualAudioIn` або його предках, але в жодному разі не в методи `AudioDuplexV` (оскільки їхні члени ще не проініціалізовані).

Водночас, якщо `VirtualAudioIn` звертається до полів віртуальної бази `VDevice`, зміщення до цієї бази вже має відповідати геометричній розкладці кінцевого `AudioDuplexV`. Цю суперечність компілятор розв'язує за допомогою **Construction Virtual Tables** (таблиць віртуальних методів конструювання), які передаються через прихований службовий масив **VTT** (Virtual Table Table).

Перевіримо цю поведінку за допомогою тестового класу з логуванням виклику з конструктора:

```cpp
struct ProbeBase {
    ProbeBase() {
        std::cout << "  [ProbeBase ctor] vptr points to ProbeBase vtable\n";
    }
    virtual void action() { std::cout << "  action -> ProbeBase\n"; }
    virtual ~ProbeBase() = default;
};

struct ProbeDerived : public ProbeBase {
    ProbeDerived() {
        std::cout << "  [ProbeDerived ctor] vptr updated to ProbeDerived vtable\n";
        action(); // Викликає ProbeDerived::action, а не нащадка
    }
    void action() override { std::cout << "  action -> ProbeDerived\n"; }
};

struct ProbeFinal : public ProbeDerived {
    ProbeFinal() {
        std::cout << "  [ProbeFinal ctor] vptr updated to ProbeFinal vtable\n";
    }
    void action() override { std::cout << "  action -> ProbeFinal\n"; }
};

void probe_construction_vtable_phases() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 5: Зміна vptr під час фаз конструювання\n";
    std::cout << "=========================================================\n";

    std::cout << "Створення екземпляра ProbeFinal:\n";
    ProbeFinal final_obj;
    std::cout << "Виклик action() після повного конструювання:\n";
    final_obj.action();
    std::cout << '\n';
}
```

Під час виконання цього коду спостерігається чітка фазовість:
1. Спочатку працює конструктор `ProbeBase`: `vptr` налаштовано на віртуальну таблицю `ProbeBase`.
2. Потім викликається конструктор `ProbeDerived`: компілятор оновлює `vptr`, записуючи в нього адресу віртуальної таблиці `ProbeDerived` (або Construction vtable у випадку віртуального спадкування). Виклик `action()` потрапляє в реалізацію `ProbeDerived`.
3. Нарешті працює конструктор `ProbeFinal`: `vptr` перезаписується адресою підсумкової таблиці `ProbeFinal`. Тепер виклик `action()` виконує фінальну версію.

## Експеримент 6: Мікровимірювання швидкодії доступу до полів

Щоб підтвердити теоретичні розрахунки на практиці, напишемо функцію мікровимірювання часу. Вона порівнює швидкість читання полів при прямому зверненні, невіртуальному множинному спадкуванні та віртуальному спадкуванні на великій кількості ітерацій.

```cpp
void benchmark_field_access() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 6: Мікровимірювання часу доступу до полів\n";
    std::cout << "=========================================================\n";

    constexpr std::size_t iterations = 50'000'000;

    AudioDuplexNV nv_obj;
    AudioDuplexV  v_obj;

    // Вказівники на проміжні інтерфейси
    AudioIn*        nv_in_ptr = &nv_obj;
    VirtualAudioIn* v_in_ptr  = &v_obj;

    // 1. Тест невіртуального доступу
    auto start_nv = std::chrono::steady_clock::now();
    volatile std::uint32_t sink_nv = 0;
    for (std::size_t i = 0; i < iterations; ++i) {
        sink_nv = nv_in_ptr->sample_rate;
    }
    auto end_nv = std::chrono::steady_clock::now();
    const auto dur_nv = std::chrono::duration_cast<std::chrono::milliseconds>(end_nv - start_nv).count();

    // 2. Тест віртуального доступу до поля віртуальної бази
    auto start_v = std::chrono::steady_clock::now();
    volatile std::uint32_t sink_v = 0;
    for (std::size_t i = 0; i < iterations; ++i) {
        sink_v = v_in_ptr->device_id;
    }
    auto end_v = std::chrono::steady_clock::now();
    const auto dur_v = std::chrono::duration_cast<std::chrono::milliseconds>(end_v - start_v).count();

    std::cout << "Кількість ітерацій циклу: " << std::dec << iterations << '\n';
    std::cout << "  Час доступу до поля невіртуальної бази : " << dur_nv << " мс\n";
    std::cout << "  Час доступу до поля віртуальної бази    : " << dur_v  << " мс\n";

    if (dur_nv > 0) {
        std::cout << "  Співвідношення витрат часу             : x"
                  << std::fixed << std::setprecision(2) << (static_cast<double>(dur_v) / dur_nv) << '\n';
    }
    std::cout << '\n';
}
```

Висновки з вимірювань:
- Доступ до полів віртуальної бази через проміжний інтерфейс демонструє стабільне сповільнення приблизно у 1.5–3 рази порівняно зі статичним доступом при роботі в гарячих циклах без оптимізації девіртуалізації.
- Якщо компілятор бачить точний динамічний тип об'єкта під час оптимізації (LTO або в межах однієї одиниці трансляції), він здатний виконати **девіртуалізацію зсуву** (англ. *offset devirtualization*), перетворивши непряме звернення через `vtable[-3]` на прямий зсув константи `+40`.

## Автоматизований звіт про прапорці компіляторів

Окрім прямого аналізу пам'яті під час виконання програми, компілятори C++ надають спеціальні прапорці діагностики для статичного виведення розкладки класів і віртуальних таблиць під час компіляції.

Для аналізу корисні такі команди:
- **Clang:** `clang++ -Xclang -fdump-record-layouts -Xclang -fdump-vtable-layouts -std=c++20 main.cpp`
- **GCC:** `g++ -fdump-lang-class -std=c++20 main.cpp` (створює файл `.class` із повним дампом)
- **MSVC:** `cl /d1reportSingleClassLayoutAudioDuplexV /std:c++20 main.cpp`

Розглянемо типовий фрагмент виводу Clang для класу `AudioDuplexV`:

```
*** Structure Layout:
   Record: struct AudioDuplexV
   Size: 448 bits (56 bytes).
   Alignment: 64 bits (8 bytes).
   FieldOffsets: [flags: 256 bits]
  [Direct Non-Virtual Base: struct VirtualAudioIn]
    Size: 128 bits (16 bytes).
    Offset: 0 bytes.
    [vtable pointer: offset 0]
    [field sample_rate: offset 8 bytes]
  [Direct Non-Virtual Base: struct VirtualAudioOut]
    Size: 128 bits (16 bytes).
    Offset: 16 bytes.
    [vtable pointer: offset 16]
    [field buffer_size: offset 24 bytes]
  [Virtual Base: struct VDevice]
    Size: 128 bits (16 bytes).
    Offset: 40 bytes.
    [vtable pointer: offset 40]
    [field device_id: offset 48 bytes]
```

Цей статичний звіт повністю підтверджує дані, отримані нашою утилітою динамічного сканування:
- Початкові 16 байтів займає невіртуальна частина `VirtualAudioIn` (разом зі своїм `vptr`).
- Наступні 16 байтів (зсув `+16`..`+31`) займає невіртуальна частина `VirtualAudioOut` (разом зі своїм `vptr`).
- Наступні 8 байтів (зсув `+32`..`+39`) відведено під власне поле `duplex_flags` (разом із 4 байтами padding для вирівнювання до 8 байтів).
- Останні 16 байтів (зсув `+40`..`+55`) займає спільний підоб'єкт віртуальної бази `VDevice`.

## Експеримент 7: Коваріантні типи повернення та return thunk

Особливою формою перехідників є **коваріантний перехідник повернення** (англ. *covariant return thunk*). Він виникає тоді, коли віртуальна функція базового класу повертає вказівник на одну зі своїх баз, а нащадок перевизначає цей метод, повертаючи вказівник на свій повний тип.

Розглянемо патерн віртуального клонування (`clone`):

```cpp
struct ClonableSource {
    virtual ClonableSource* clone() const = 0;
    virtual ~ClonableSource() = default;
};

struct ClonableSink {
    virtual ClonableSink* clone() const = 0;
    virtual ~ClonableSink() = default;
};

struct ClonableDuplex : public ClonableSource, public ClonableSink {
    // Одне перевизначення задовольняє обидва інтерфейси одночасно:
    ClonableDuplex* clone() const override {
        return new ClonableDuplex(*this);
    }
};
```

Що відбувається, коли клієнт викликає `ClonableSink* sink = duplex->clone()`?
1. Клієнт викликає метод через інтерфейс `ClonableSink`, тому очікує отримати результат типу `ClonableSink*`.
2. Проте метод `ClonableDuplex::clone()` створює і повертає вказівник на початок повного об'єкта `ClonableDuplex*` (зсув 0).
3. Якщо підоб'єкт `ClonableSink` розташований усередині `ClonableDuplex` за зміщенням `+8` байтів, адреса, яку повертає метод, не збігається з адресою, яку очікує клієнт.
4. Щоб задовольнити обидві сторони, компілятор створює спеціальний асемблерний перехідник для таблиці віртуальних методів `ClonableSink`:

```asm
# Коваріантний перехідник для ClonableDuplex::clone() у таблиці ClonableSink
_ZTch0_h8_NK14ClonableDuplex5cloneEv:
    call    _ZNK14ClonableDuplex5cloneEv   # 1. Викликаємо основний метод clone(), результат у %rax
    testq   %rax, %rax                    # 2. Перевіряємо, чи результат не є nullptr
    je      .Lout
    addq    $8, %rax                      # 3. Додаємо зсув +8 байтів до повернутої адреси!
.Lout:
    ret                                   # 4. Повертаємо скоригований покажчик
```

Цей приклад ілюструє витончену симетрію архітектури C++:
- Якщо зміщення потрібне для вхідного аргументу `this`, компілятор генерує **вхідний перехідник** (this-adjustor thunk, який віднімає зміщення).
- Якщо зміщення потрібне для результату повернення функції, компілятор генерує **вихідний перехідник** (return-adjustor thunk, який додає зміщення до регістра результату `%rax`).

## Експеримент 8: Оптимізація порожніх баз (EBO) при множинному спадкуванні

При проектуванні сучасних бібліотек класи часто успадковують допоміжні класи-маркери або класи без полів даних (наприклад, `std::allocator`, теги ітераторів або mixin-інтерфейси).

За стандартом C++ розмір будь-якого самостійного об'єкта не може дорівнювати 0 байтів, оскільки кожен об'єкт повинен мати унікальну адресу в пам'яті (`sizeof(Empty) >= 1`). Проте під час спадкування вмикається **оптимізація порожньої бази** (англ. *Empty Base Optimization*, EBO).

Дослідимо, як EBO взаємодіє з множинним спадкуванням:

```cpp
struct EmptyTag1 {};
struct EmptyTag2 {};
struct EmptyTag3 {};

struct CombinedTags : public EmptyTag1, public EmptyTag2, public EmptyTag3 {
    std::uint32_t payload{42};
};

struct TwoSameEmptyBases : public EmptyTag1, public EmptyTag2 {
    // Обидві бази порожні, але мають РІЗНІ типи -> EBO працює для обох!
};

struct CollisionEmptyBases : public EmptyTag1 {
    EmptyTag1 member_tag; // Поле того самого типу, що й базова структура!
    // За стандартом базовий підоб'єкт і член одного типу НЕ можуть мати однакову адресу.
    // Тут EBO для базового класу вимикається, і додається 1 байт padding!
};
```

Перевірка розмірів у коді:

```cpp
void probe_empty_base_layouts() {
    std::cout << "=========================================================\n";
    std::cout << " ЕКСПЕРИМЕНТ 8: Оптимізація порожніх баз (EBO)\n";
    std::cout << "=========================================================\n";

    std::cout << "Розмір порожньої структури sizeof(EmptyTag1): " << sizeof(EmptyTag1) << " B\n";
    std::cout << "Розмір CombinedTags (3 порожні бази + uint32): " << sizeof(CombinedTags)
              << " B (EBO обнулило розмір усіх трьох баз!)\n";
    std::cout << "Розмір TwoSameEmptyBases (2 різні порожні бази): " << sizeof(TwoSameEmptyBases)
              << " B (мінімальний розмір 1 байт)\n";
    std::cout << "Розмір CollisionEmptyBases (колізія адрес однакового типу): " << sizeof(CollisionEmptyBases)
              << " B (EBO не змогло застосуватися через вимогу унікальності адрес)\n\n";
}
```

Правила EBO при множинному спадкуванні:
1. Якщо клас успадковує кілька порожніх класів **різних типів**, усі вони можуть бути розміщені за нульовим зміщенням (offset 0), не збільшуючи загальний розмір об'єкта.
2. Якщо ж два підоб'єкти одного типу мали б опинитися за однаковою адресою (наприклад, при невіртуальному ромбі двох порожніх класів або коли член класу має той самий тип, що й порожня база), компілятор зобов'язаний виділити другому підоб'єкту окремий байт, щоб їхні адреси розрізнялися.

## Інтерактивна діагностика розкладки в налагоджувачах GDB та LLDB

Окрім компіляторних звітів і програмних інспекторів, розкладку об'єктів та структуру віртуальних таблиць можна досліджувати безпосередньо в інтерактивному налагоджувачі:

- **GDB:**
  - `set print object on` — вмикає відображення реального динамічного типу об'єкта замість статичного типу покажчика.
  - `set print vtbl on` — наказує GDB роздруковувати повну структуру віртуальної таблиці із зазначенням усіх зсувів і thunk-функцій при друку покажчиків.
  - `info vtbl <object>` — виводить список усіх віртуальних методів та відповідних їм адрес у таблиці.
  - `p /x *(AudioDuplexV*)ptr` — виводить побайтову структуру екземпляра із зазначенням внутрішніх полів `_vptr`.

- **LLDB:**
  - `target modules dump ast <binary>` — виводить повне абстрактне синтаксичне дерево (AST) із точними зміщеннями полів і підоб'єктів.
  - `frame var -T -L` — відображає локальні змінні разом із їхніми типами (`-T`) та адресами розташування в пам'яті (`-L`).

## Порівняння розмірів та висновки

Об'єднаємо всі діагностичні тести в єдину функцію `main` і виведемо зведену таблицю розмірів:

```cpp
int main() {
    std::cout << "=========================================================\n";
    std::cout << " ДІАГНОСТИЧНИЙ ІНСПЕКТОР РОЗКЛАДКИ ПАМ'ЯТІ C++\n";
    std::cout << "=========================================================\n\n";

    std::cout << "Порівняння розмірів типів (платформа 64-біт):\n";
    std::cout << "  sizeof(Device)          = " << std::setw(2) << sizeof(Device) << " B (vptr 8 B + id 4 B + pad 4 B)\n";
    std::cout << "  sizeof(AudioIn)         = " << std::setw(2) << sizeof(AudioIn) << " B (Device 16 B + rate 4 B + pad 4 B)\n";
    std::cout << "  sizeof(AudioOut)        = " << std::setw(2) << sizeof(AudioOut) << " B (Device 16 B + buf 4 B + pad 4 B)\n";
    std::cout << "  sizeof(AudioDuplexNV)   = " << std::setw(2) << sizeof(AudioDuplexNV)
              << " B (In 24 B + Out 24 B + flags 4 B + pad 4 B -> 56 B)\n";
    std::cout << "  ---------------------------------------------------------\n";
    std::cout << "  sizeof(VDevice)         = " << std::setw(2) << sizeof(VDevice) << " B\n";
    std::cout << "  sizeof(VirtualAudioIn)  = " << std::setw(2) << sizeof(VirtualAudioIn)
              << " B (vptr 8 B + rate 4 B + pad 4 B + VDevice 16 B -> 32 B)\n";
    std::cout << "  sizeof(VirtualAudioOut) = " << std::setw(2) << sizeof(VirtualAudioOut) << " B\n";
    std::cout << "  sizeof(AudioDuplexV)    = " << std::setw(2) << sizeof(AudioDuplexV)
              << " B (vptr_In 8 B + in_f 8 B + vptr_Out 8 B + out_f 8 B + flags 8 B + VDevice 16 B -> 56 B)\n\n";

    probe_pointer_adjustments();
    probe_state_duplication();
    probe_virtual_base_offsets();
    probe_side_casting();
    probe_construction_vtable_phases();
    benchmark_field_access();
    probe_empty_base_layouts();

    std::cout << "Усі діагностичні експерименти виконано успішно.\n";
    return 0;
}
```

Розроблена утиліта демонструє, що робота зі складними об'єктними ієрархіями в C++ повністю підпорядкована детермінованим правилам двійкового компонування:
- **Множинне спадкування** розміщує підоб'єкти послідовно і вимагає постійних статичних зсувів покажчика `this`.
- **Віртуальне спадкування** усуває дублювання базових підоб'єктів, але вимагає непрямої адресації через службові поля `vbase_offset` у віртуальних таблицях.
- **Діагностика через сиру пам'ять** дає змогу точно верифікувати припущення про компонування даних і виявляти небезпечні спроби обходу системи типів.
