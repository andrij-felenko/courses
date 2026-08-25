# ⚙️ Практика: Архітектура систем кастомізації та диспетчеризації

У промислових розподілених системах (мережеві протоколи, збереження стану ігрових світів, брокери фінансових повідомлень та високочастотний трейдинг) серіалізація даних у бінарні формати є однією з найчастіших операцій. Універсальний рушій серіалізації повинен гарантувати максимальну швидкість виконання, нульові накладні витрати пам'яті (zero-cost abstractions) та надійну точку розширення, що дозволяє користувачам додавати підтримку нових типів без модифікації бібліотечних файлів.

Нижче наведено покроковий розбір побудови бінарного серіалізатора, аналіз прихованих дефектів при використанні повної спеціалізації функцій та детальну реалізацію трьох надійних інженерних моделей диспетчеризації.

---

## 1. Постановка завдання: бінарний серіалізатор BinaryWriter

Серіалізатор повинен надавати єдиний публічний інтерфейс запису `serialize(buffer, value)` і автоматично обирати найефективнішу стратегію обробки для чотирьох принципово різних категорій типів даних:

1. **Скалярні тривіальні типи** (`int32_t`, `double`, `uint64_t`, переліки `enum class`) — пряме побайтове копіювання у буфер пам'яті. Якщо цільова архітектура відрізняється порядком байтів від мережевого стандарту (наприклад, Little-Endian на x86 проти Big-Endian у мережі), серіалізатор повинен прозоро виконувати реверс байтів.
2. **Сирі вказівники та буфери пам'яті** (`T*`, `const char*`) — збереження маркерів наявності даних (`has_value`), довжини послідовності та послідовний запис сирих елементів із захистом від розіменування нульового вказівника `nullptr`.
3. **Стандартні динамічні контейнери** (`std::vector<T>`, `std::string`, `std::pair<U, V>`) — рекурсивна серіалізація кількості елементів з подальшим викликом серіалізатора для кожного внутрішнього елемента.
4. **Користувацькі складні бізнес-структури** (`SensorFrame`, `TradeOrder`) — кастомізація користувачем безпосередньо у прикладному коді без необхідності вносити зміни у заголовочні файли самого серіалізатора.

Для збереження згенерованих байтів визначимо клас динамічного бінарного буфера:

```cpp
#include <vector>
#include <cstdint>
#include <cstring>
#include <string>
#include <iostream>
#include <type_traits>
#include <concepts>
#include <span>
#include <bit>

class BinaryBuffer {
public:
    void write_raw(const void* data, std::size_t size) {
        const auto* bytes = static_cast<const uint8_t*>(data);
        storage_.insert(storage_.end(), bytes, bytes + size);
    }

    [[nodiscard]] const std::vector<uint8_t>& data() const noexcept {
        return storage_;
    }

    [[nodiscard]] std::size_t size() const noexcept {
        return storage_.size();
    }

    void clear() noexcept {
        storage_.clear();
    }

private:
    std::vector<uint8_t> storage_;
};
```

---

## 2. Фатальний підхід: спеціалізація шаблону функції

У старих підручниках або наївних реалізаціях часто радять створити первинний шаблон функції `serialize` і дозволити користувачам писати повні спеціалізації `template<> void serialize(...)` під кожен новий тип.

Розглянемо вихідний заголовочний файл бібліотеки:

```cpp
namespace broken_design {

// 1. Первинний шаблон серіалізатора для загальних типів
template<typename T>
void serialize(BinaryBuffer& buf, const T& value) {
    // За замовчуванням копіюємо як плоскі сирі байти
    buf.write_raw(&value, sizeof(T));
}

// 2. Спеціалізація для рядків std::string
template<>
inline void serialize<std::string>(BinaryBuffer& buf, const std::string& str) {
    uint32_t len = static_cast<uint32_t>(str.size());
    buf.write_raw(&len, sizeof(len));
    buf.write_raw(str.data(), len);
}

// 3. Спеціалізація для вказівників const char*
template<>
inline void serialize<const char*>(BinaryBuffer& buf, const char* const& str) {
    uint32_t len = static_cast<uint32_t>(std::strlen(str));
    buf.write_raw(&len, sizeof(len));
    buf.write_raw(str, len);
}

} // namespace broken_design
```

### Механізм виникнення прихованого дефекту

Цей код успішно збирається і працює рівно доти, доки бібліотека розвивається ізольовано. Проте через кілька місяців інший інженер команди додає утиліту для роботи з вказівниками, щоб підтримати опціональні значення:

```cpp
namespace broken_design {

// Додано нове перевантаження первинного шаблону для довільних вказівників T*
template<typename T>
void serialize(BinaryBuffer& buf, T* ptr) {
    uint8_t has_value = (ptr != nullptr) ? 1 : 0;
    buf.write_raw(&has_value, sizeof(has_value));
    if (ptr != nullptr) {
        serialize(buf, *ptr); // Рекурсивний виклик для розіменованого об'єкта
    }
}

} // namespace broken_design
```

Спробуємо виконати серіалізацію звичайного рядка мови C:

```cpp
void execute_serialization_test() {
    BinaryBuffer buf;
    const char* message = "SECURITY_TOKEN_PAYLOAD";

    // Виклик функції серіалізації
    broken_design::serialize(buf, message);
}
```

Розберемо покроково, як компілятор транслює цей рядок коду згідно зі стандартом ISO C++:

1. **Формування набору кандидатів перевантаження (Overload Candidate Set)**. У набір потрапляють виключно первинні шаблони. Повні спеціалізації `template<>` на цьому етапі **не розглядаються**:
   - Кандидат А: `serialize(BinaryBuffer&, const T&)` з параметром `T = const char*`.
   - Кандидат Б: `serialize(BinaryBuffer&, T*)` з параметром `T = const char`.
2. **Алгоритм часткового впорядкування (Partial Ordering)**. Компілятор порівнює Кандидата А та Кандидата Б. Шаблон `T*` приймає виключно вказівники, тоді як шаблон `const T&` може прийняти будь-який тип. Оскільки множина типів-вказівників є строгою підмножиною всіх типів C++, Кандидат Б є **більш спеціалізованим**. Кандидат Б перемагає у фазі Overload Resolution.
3. **Пошук спеціалізацій обраного переможця**. Компілятор перевіряє, чи має Кандидат Б повну спеціалізацію для типу `T = const char`. Такої спеціалізації немає!
4. **Ігнорування спеціалізації користувача**. Спеціалізація `serialize<const char*>`, написана раніше, була створена для Кандидата А. Оскільки Кандидат А програв перевантаження, всі його спеціалізації викидаються з процесу компіляції.
5. **Генерація неправильного коду**. Компілятор інстанціює тіло Кандидата Б: він записує байт прапорця `has_value = 1`, після чого викликає `serialize(buf, *ptr)` для типу `char`.
6. **Результат у пам'яті**. Замість усього рядка `"SECURITY_TOKEN_PAYLOAD"` довжиною 22 байти у буфер записується лише 1 байт прапорця і перший символ `'S'`.

Програма скомпілювалася без жодного попередження (zero warnings), але дані були незворотно пошкоджені. Це класичний приклад правила Саттера: спеціалізації функцій не беруть участі у перевантаженні.

---

## 3. Патерн 1: Делегування у допоміжну структуру (Traits Helper)

Щоб назавжди захистити кодову базу від таких помилок, застосовують патерн **делегування у статичні методи структури-трейта** (англ. *Helper Struct Delegation*).

Оскільки структури підтримують часткову спеціалізацію і не мають фази перевантаження функцій, вибір коду для структури відбувається за однозначними правилами зіставлення типів шаблонів.

```cpp
namespace trait_design {

// 1. Первинний шаблон структури серіалізатора
template<typename T, typename Enable = void>
struct SerializerTraits {
    static void write(BinaryBuffer& buf, const T& value) {
        static_assert(std::is_trivially_copyable_v<T>,
                      "Тип повинен бути trivially copyable або мати спеціалізацію SerializerTraits");
        
        // Для скалярних типів враховуємо порядок байтів
        if constexpr (std::is_integral_v<T> && sizeof(T) > 1) {
            // Перетворення до стандарту Big-Endian (мережевий порядок)
            T be_val = value;
            if constexpr (std::endian::native == std::endian::little) {
                be_val = std::byteswap(value);
            }
            buf.write_raw(&be_val, sizeof(T));
        } else {
            buf.write_raw(&value, sizeof(T));
        }
    }
};

// 2. Часткова спеціалізація для всіх вказівників T*
template<typename T>
struct SerializerTraits<T*> {
    static void write(BinaryBuffer& buf, const T* ptr) {
        uint8_t has_value = (ptr != nullptr) ? 1 : 0;
        buf.write_raw(&has_value, sizeof(has_value));
        if (ptr != nullptr) {
            SerializerTraits<T>::write(buf, *ptr);
        }
    }
};

// 3. Спеціалізація для рядків C-стилю const char*
template<>
struct SerializerTraits<const char*> {
    static void write(BinaryBuffer& buf, const char* str) {
        if (str == nullptr) {
            uint32_t zero_len = 0;
            buf.write_raw(&zero_len, sizeof(zero_len));
            return;
        }
        uint32_t len = static_cast<uint32_t>(std::strlen(str));
        buf.write_raw(&len, sizeof(len));
        buf.write_raw(str, len);
    }
};

// 4. Часткова спеціалізація для динамічних векторів std::vector<T>
template<typename T>
struct SerializerTraits<std::vector<T>> {
    static void write(BinaryBuffer& buf, const std::vector<T>& vec) {
        uint32_t count = static_cast<uint32_t>(vec.size());
        buf.write_raw(&count, sizeof(count));
        for (const auto& item : vec) {
            SerializerTraits<T>::write(buf, item);
        }
    }
};

// 5. Часткова спеціалізація для пар std::pair<T1, T2>
template<typename T1, typename T2>
struct SerializerTraits<std::pair<T1, T2>> {
    static void write(BinaryBuffer& buf, const std::pair<T1, T2>& pair) {
        SerializerTraits<T1>::write(buf, pair.first);
        SerializerTraits<T2>::write(buf, pair.second);
    }
};

// 6. Повна спеціалізація для рядків std::string
template<>
struct SerializerTraits<std::string> {
    static void write(BinaryBuffer& buf, const std::string& str) {
        uint32_t len = static_cast<uint32_t>(str.size());
        buf.write_raw(&len, sizeof(len));
        buf.write_raw(str.data(), len);
    }
};

// 7. ЄДИНА ПУБЛІЧНА ФУНКЦІЯ API (Ніколи не перевантажується і не спеціалізується!)
template<typename T>
void serialize(BinaryBuffer& buf, const T& value) {
    SerializerTraits<std::remove_cvref_t<T>>::write(buf, value);
}

} // namespace trait_design
```

### Як користувач додає власні бізнес-структури

Користувач бібліотеки більше не ризикує зіпсувати перевантаження функцій. Щоб навчити серіалізатор працювати з власною структурою `SensorFrame`, достатньо додати спеціалізацію структури `SerializerTraits`:

```cpp
struct SensorFrame {
    uint64_t timestamp_ns;
    uint32_t device_id;
    std::vector<float> readings;
};

// Спеціалізація структури у просторі імен бібліотеки
template<>
struct trait_design::SerializerTraits<SensorFrame> {
    static void write(BinaryBuffer& buf, const SensorFrame& frame) {
        SerializerTraits<uint64_t>::write(buf, frame.timestamp_ns);
        SerializerTraits<uint32_t>::write(buf, frame.device_id);
        SerializerTraits<std::vector<float>>::write(buf, frame.readings);
    }
};
```

Тепер виклик `trait_design::serialize(buf, my_sensor_frame)` коректно обробить усі поля, збереже вектори та впорядкує байти з гарантією стабільності.

---

## 4. Патерн 2: Диспетчеризація за тегами (Tag Dispatching)

Часто алгоритм серіалізації масивів даних вимагає оптимізації за властивостями типів: якщо елементи масиву є тривіально копійованими (`std::is_trivially_copyable_v<T>`), весь масив можна записати за один системний виклик `memcpy` на швидкості оперативної пам'яті (десятки гігабайтів за секунду). Якщо ж тип складний (наприклад, масив `std::string`), потрібно виконувати поелементний обхід.

Механізм **Tag Dispatching** переносить вибір алгоритму на перевантаження спеціальних порожніх структур-тегів:

```cpp
namespace tag_dispatch_design {

// Оголошення типів-тегів
struct ContiguousMemoryTag {};
struct ElementWiseMemoryTag {};

// Метафункція для вибору тегу під час компіляції
template<typename T>
struct MemoryLayoutCategory {
    using type = std::conditional_t<
        std::is_trivially_copyable_v<T> && (std::endian::native == std::endian::big || sizeof(T) == 1),
        ContiguousMemoryTag,
        ElementWiseMemoryTag
    >;
};

template<typename T>
using MemoryLayoutCategory_t = typename MemoryLayoutCategory<T>::type;

// Внутрішня гілка 1: швидке суцільне копіювання пам'яті
template<typename T>
void write_buffer_impl(BinaryBuffer& buf, const T* data, std::size_t count, ContiguousMemoryTag) {
    buf.write_raw(data, count * sizeof(T));
}

// Внутрішня гілка 2: поелементна серіалізація для складних типів
template<typename T>
void write_buffer_impl(BinaryBuffer& buf, const T* data, std::size_t count, ElementWiseMemoryTag) {
    for (std::size_t i = 0; i < count; ++i) {
        trait_design::serialize(buf, data[i]);
    }
}

// Публічна функція серіалізації масиву
template<typename T>
void serialize_contiguous_span(BinaryBuffer& buf, std::span<const T> elements) {
    uint32_t count = static_cast<uint32_t>(elements.size());
    buf.write_raw(&count, sizeof(count));
    
    // Компілятор обирає потрібне перевантаження за типом третього аргументу-тегу
    write_buffer_impl(buf, elements.data(), elements.size(), MemoryLayoutCategory_t<T>{});
}

} // namespace tag_dispatch_design
```

---

## 5. Патерн 3: Сучасна кастомізація у C++20 (Concepts + if constexpr)

У стандарті C++20 з'явилася можливість будувати всю систему кастомізації без спеціалізацій допоміжних структур і без фіктивних тегів за допомогою **Концептів** та виразів `if constexpr`.

```cpp
namespace modern_cpp20 {

// Концепт 1: Типи, які надають власний метод збереження serialize_to
template<typename T>
concept CustomSerializable = requires(const T& obj, BinaryBuffer& buf) {
    obj.serialize_to(buf);
};

// Концепт 2: Стандартні ітеровані контейнери
template<typename T>
concept SerializableContainer = requires(const T& container) {
    { container.begin() } -> std::input_or_output_iterator;
    { container.end() } -> std::input_or_output_iterator;
    { container.size() } -> std::convertible_to<std::size_t>;
} && !std::same_as<std::remove_cvref_t<T>, std::string>;

// Уніфікована функція серіалізації нового покоління
template<typename T>
void serialize(BinaryBuffer& buf, const T& value) {
    using PureType = std::remove_cvref_t<T>;

    if constexpr (CustomSerializable<PureType>) {
        // Пріоритет 1: Власний метод класу
        value.serialize_to(buf);
    } 
    else if constexpr (std::same_as<PureType, std::string>) {
        // Пріоритет 2: Рядки std::string
        uint32_t len = static_cast<uint32_t>(value.size());
        buf.write_raw(&len, sizeof(len));
        buf.write_raw(value.data(), len);
    } 
    else if constexpr (std::same_as<PureType, const char*> || std::same_as<PureType, char*>) {
        // Пріоритет 3: Рядки C-стилю
        if (value == nullptr) {
            uint32_t zero = 0;
            buf.write_raw(&zero, sizeof(zero));
        } else {
            uint32_t len = static_cast<uint32_t>(std::strlen(value));
            buf.write_raw(&len, sizeof(len));
            buf.write_raw(value, len);
        }
    } 
    else if constexpr (SerializableContainer<PureType>) {
        // Пріоритет 4: Контейнери (вектори, списки, множини)
        uint32_t count = static_cast<uint32_t>(value.size());
        buf.write_raw(&count, sizeof(count));
        for (const auto& item : value) {
            serialize(buf, item); // Рекурсивне збереження
        }
    } 
    else if constexpr (std::is_pointer_v<PureType>) {
        // Пріоритет 5: Довільні вказівники
        uint8_t has_val = (value != nullptr) ? 1 : 0;
        buf.write_raw(&has_val, sizeof(has_val));
        if (value != nullptr) {
            serialize(buf, *value);
        }
    } 
    else if constexpr (std::is_trivially_copyable_v<PureType>) {
        // Пріоритет 6: Скаляри та плоскі структури
        if constexpr (std::is_integral_v<PureType> && sizeof(PureType) > 1) {
            PureType be_val = value;
            if constexpr (std::endian::native == std::endian::little) {
                be_val = std::byteswap(value);
            }
            buf.write_raw(&be_val, sizeof(PureType));
        } else {
            buf.write_raw(&value, sizeof(PureType));
        }
    } 
    else {
        // Якщо жодна гілка не підійшла — зупиняємо збірку з детальним повідомленням
        static_assert(!sizeof(T), "Помилка компіляції: тип не підтримує бінарну серіалізацію!");
    }
}

} // namespace modern_cpp20
```

### Підключення бізнес-класів у моделі C++20

Тепер розробнику прикладного рівня взагалі не потрібно знати про існування спеціалізацій чи маніпулювати просторами імен бібліотеки. Достатньо реалізувати метод `serialize_to`:

```cpp
struct TradeOrder {
    uint64_t order_id;
    double price;
    uint32_t volume;
    std::string client_id;

    void serialize_to(BinaryBuffer& buf) const {
        modern_cpp20::serialize(buf, order_id);
        modern_cpp20::serialize(buf, price);
        modern_cpp20::serialize(buf, volume);
        modern_cpp20::serialize(buf, client_id);
    }
};
```

Компілятор бачить, що клас `TradeOrder` відповідає концепту `CustomSerializable`, і активує першу гілку `if constexpr` без виклику проміжних структур.

---

## 6. Зворотний процес: десеріалізація та відновлення даних

Для завершення картини реалізуємо дзеркальний механізм читання бінарних даних `BinaryReader`:

```cpp
class BinaryReader {
public:
    explicit BinaryReader(std::span<const uint8_t> data) 
        : buffer_(data), offset_(0) {}

    template<typename T>
    void read_raw(T& destination) {
        if (offset_ + sizeof(T) > buffer_.size()) {
            throw std::runtime_error("Недостатньо байтів у буфері для читання скаляра");
        }
        std::memcpy(&destination, buffer_.data() + offset_, sizeof(T));
        offset_ += sizeof(T);
    }

    void read_bytes(void* dest, std::size_t size) {
        if (offset_ + size > buffer_.size()) {
            throw std::runtime_error("Недостатньо байтів у буфері для читання масиву");
        }
        std::memcpy(dest, buffer_.data() + offset_, size);
        offset_ += size;
    }

    [[nodiscard]] bool empty() const noexcept {
        return offset_ >= buffer_.size();
    }

private:
    std::span<const uint8_t> buffer_;
    std::size_t offset_;
};

// Десеріалізація для моделі C++20
template<typename T>
T deserialize(BinaryReader& reader) {
    using PureType = std::remove_cvref_t<T>;

    if constexpr (std::same_as<PureType, std::string>) {
        uint32_t len = 0;
        reader.read_raw(len);
        std::string str(len, '\0');
        reader.read_bytes(str.data(), len);
        return str;
    } 
    else if constexpr (std::is_integral_v<PureType>) {
        PureType val{};
        reader.read_raw(val);
        if constexpr (sizeof(PureType) > 1 && std::endian::native == std::endian::little) {
            val = std::byteswap(val);
        }
        return val;
    } 
    else if constexpr (std::is_trivially_copyable_v<PureType>) {
        PureType val{};
        reader.read_raw(val);
        return val;
    } 
    else {
        static_assert(!sizeof(T), "Десеріалізація для цього типу не реалізована");
    }
}
```

---

## 7. Порівняльний аналіз архітектурних рішень

| Критерій оцінки | Повна спец. функцій | Traits Helper Structs | Tag Dispatching | C++20 Concepts + if constexpr |
| :--- | :--- | :--- | :--- | :--- |
| **Стійкість до перевантажень** | Крихка (ламається при появі нових перевантажень) | Абсолютна | Абсолютна | Абсолютна |
| **Підтримка часткової спеціалізації** | Заборонена стандартом | Повна підтримка | Емулюється через теги | Не потрібна |
| **Зручність для користувача** | Потрібно знати правила спеціалізації | Спеціалізація структури у namespace | Виклик внутрішніх функцій | Реалізація методу класу |
| **Швидкість компіляції** | Середня | Середня (багато структур) | Швидка | Найшвидша (локальний constexpr) |
| **Якість повідомлень про помилки** | Прихована підміна коду | Зрозумілий `static_assert` | Складні дампи SFINAE | Чіткі вказівки на порушений концепт |

---

## 8. Практичні висновки для проєктування архітектури

1. **Ніколи не дозволяйте користувачам спеціалізувати шаблони функцій.** Завжди робіть публічні функції неспеціалізованими точками входу.
2. Для бібліотек, що підтримують стандарти C++11, C++14 та C++17, **єдиним безпечним стандартом залишається ідіома делегування у допоміжну структуру-трейт** (`SerializerTraits<T>::write`).
3. Для нових проєктів на C++20 та C++23 використовуйте **концептуальні обмеження та вирази `if constexpr`**: вони забезпечують локалізацію логіки розгалуження, найкращу швидкість збірки та абсолютно прозору поведінку коду.
