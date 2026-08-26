# ⚙️ Реалізація захищеного буфера та виявлення переповнень

Запобігання переповненню буфера на рівні вихідного коду вимагає переходу від небезпечних функцій роботи з сирою пам'яттю до захищених абстракцій з явним контролем меж. Якщо компіляторні механізми (SSP) спрацьовують постфактум — у момент спроби повернення з пошкодженої функції, то захищені патерни програмування запобігають самому факту виходу за межі виділеної пам'яті.

У мовах C та C++ робота з масивами традиційно страждає від проблеми деградації типів (*array decay*): передача масиву `char buffer[64]` у функцію неявно перетворює його на голий числовий покажчик `char*`. Викликана функція втрачає будь-яку інформацію про місткість виділеного блоку пам'яті і змушена повністю покладатися на чесність вхідних даних або наявність завершального байта `0x00`.

## 1. Захищене копіювання: перехід від strcpy до обмежених операцій

Класична помилка розробників полягає у використанні функцій `strcpy()` або `strcat()`, які виконують копіювання в циклі, доки не зустрінуть нульовий байт у вихідному рядку. Якщо довжина вхідних даних перевищує розмір буфера призначення, операція продовжує безконтрольний запис у суміжні комірки пам'яті.

Правильна інженерна реалізація вимагає обов'язкового передавання максимальної місткості цільового буфера та явної перевірки розміру до початку копіювання. Особливу увагу слід звертати на помилку «зсуву на одиницю» (*Off-by-One Error*): для зберігання нуль-термінованого рядка довжиною `N` символів буфер повинен мати розмір щонайменше `N + 1` байтів.

Нижче наведено порівняння захищеної реалізації на C з контролем довжини та сучасного ідіоматичного підходу на C++23 з використанням безпечних типів-обгорток `std::span` та `std::expected`.

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#define MAX_BUFFER_SIZE 64

// Безпечне копіювання з явним контролем довжини та гарантією нуль-термінатора
bool safe_copy_string(char *dest, size_t dest_cap, const char *src) {
    if (!dest || !src || dest_cap == 0) {
        return false;
    }
    
    size_t src_len = strlen(src);
    // Перевірка: довжина рядка разом із нульовим байтом не повинна перевищувати місткість
    if (src_len >= dest_cap) {
        // Дані перевищують місткість буфера — відкидаємо копіювання
        return false;
    }
    
    memcpy(dest, src, src_len);
    dest[src_len] = '\0';
    return true;
}

int main(void) {
    char destination[MAX_BUFFER_SIZE];
    const char *untrusted_input = "Untrusted input string payload";

    if (safe_copy_string(destination, sizeof(destination), untrusted_input)) {
        printf("Успішно скопійовано: %s\n", destination);
    } else {
        printf("Помилка: вхідні дані перевищують розмір буфера!\n");
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <expected>
#include <algorithm>

constexpr size_t MaxBufferSize = 64;

enum class BufferError {
    CapacityExceeded,
    EmptyBuffer
};

// Ідіоматичний підхід C++23 з використанням std::span та std::expected
template <size_t N>
std::expected<void, BufferError> safe_copy(std::array<char, N>& dest, std::string_view src) {
    if (src.empty()) {
        return std::unexpected(BufferError::EmptyBuffer);
    }
    
    if (src.size() >= N) {
        return std::unexpected(BufferError::CapacityExceeded);
    }
    
    std::copy(src.begin(), src.end(), dest.begin());
    dest[src.size()] = '\0';
    return {};
}

int main() {
    std::array<char, MaxBufferSize> destination{};
    std::string_view untrusted_input = "Untrusted input string payload";

    auto result = safe_copy(destination, untrusted_input);
    if (result.has_value()) {
        std::cout << "Успішно скопійовано: " << destination.data() << '\n';
    } else {
        std::cerr << "Помилка: вхідні дані перевищують розмір буфера!\n";
    }
    return 0;
}
```
:::

## 2. Реалізація буфера з користувацькою канаркою (Canary Guard)

Для контролю цілісності пам'яті в критичних підсистемах або вбудованих середовищах (де компіляторний захист SSP може бути вимкненим або недоступним через обмеження платформи), застосовують патерн вартового значення (Canary Pattern).

Ідея полягає у фізичному оточенні буфера фіксованими 64-бітними магічними константами — *головною канаркою* (`head_canary`) на початку та *хвостовою канаркою* (`tail_canary`) в кінці. Оскільки запис у буфер виконується знизу вгору, будь-яке переповнення масиву обов'язково зачепить і модифікує значення хвостової канарки. Періодична або передчасна перевірка вартових значень дозволяє виявити факт псування пам'яті до того, як пошкоджені структури будуть використані іншими підсистемами програми.

Нижче наведено робочу реалізацію захищеної структури на C та шаблонного класу на C++, що демонструють миттєву фіксацію переповнення.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define CANARY_HEAD 0xDEADBEEFCAFE0001ULL
#define CANARY_TAIL 0xDEADBEEFCAFE0002ULL

typedef struct {
    uint64_t head_canary;
    char raw_data[64];
    uint64_t tail_canary;
} GuardedBuffer;

void guarded_buffer_init(GuardedBuffer *gb) {
    if (!gb) return;
    gb->head_canary = CANARY_HEAD;
    gb->tail_canary = CANARY_TAIL;
    memset(gb->raw_data, 0, sizeof(gb->raw_data));
}

bool guarded_buffer_verify(const GuardedBuffer *gb) {
    if (!gb) return false;
    return (gb->head_canary == CANARY_HEAD) && (gb->tail_canary == CANARY_TAIL);
}

void guarded_buffer_write(GuardedBuffer *gb, const char *src, size_t len) {
    if (len > sizeof(gb->raw_data)) {
        printf("[!] Спроба переповнення: запис %zu байтів у буфер на %zu байтів\n",
               len, sizeof(gb->raw_data));
    }
    // Навмисна емуляція некоректного копіювання для демонстрації виявлення
    memcpy(gb->raw_data, src, len);
}

int main(void) {
    GuardedBuffer buffer;
    guarded_buffer_init(&buffer);

    // Спроба записати 80 байтів (переповнення на 16 байтів у tail_canary)
    char payload[80];
    memset(payload, 'A', sizeof(payload));

    guarded_buffer_write(&buffer, payload, sizeof(payload));

    if (!guarded_buffer_verify(&buffer)) {
        printf("[АЛАРМ] Пошкодження пам'яті виявлено! Tail Canary спотворено: 0x%llX\n",
               (unsigned long long)buffer.tail_canary);
    } else {
        printf("[OK] Цілісність буфера збережено.\n");
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <cstdint>
#include <cstring>
#include <format>
#include <algorithm>
#include <span>

template <size_t Capacity>
class GuardedBuffer {
private:
    static constexpr uint64_t HeadCanaryValue = 0xDEADBEEFCAFE0001ULL;
    static constexpr uint64_t TailCanaryValue = 0xDEADBEEFCAFE0002ULL;

    uint64_t head_canary_{HeadCanaryValue};
    std::array<char, Capacity> storage_{};
    uint64_t tail_canary_{TailCanaryValue};

public:
    GuardedBuffer() = default;

    [[nodiscard]] bool is_valid() const noexcept {
        return head_canary_ == HeadCanaryValue && tail_canary_ == TailCanaryValue;
    }

    [[nodiscard]] uint64_t tail_canary() const noexcept {
        return tail_canary_;
    }

    // Безпечний ідіоматичний запис через std::span
    bool write_safe(std::span<const char> src) noexcept {
        if (src.size() > Capacity) {
            return false;
        }
        std::copy(src.begin(), src.end(), storage_.begin());
        return true;
    }

    // Небезпечний запис для демонстрації роботи канарки
    void write_raw_unchecked(const char* src, size_t len) noexcept {
        std::memcpy(storage_.data(), src, len);
    }
};

int main() {
    GuardedBuffer<64> buffer;

    std::array<char, 80> attack_payload{};
    attack_payload.fill('A');

    std::cout << "[*] Запис 80 байтів у захищений буфер розміром 64 байти...\n";
    buffer.write_raw_unchecked(attack_payload.data(), attack_payload.size());

    if (!buffer.is_valid()) {
        std::cout << std::format("[АЛАРМ] Пошкодження пам'яті виявлено! Tail Canary = 0x{:X}\n",
                                 buffer.tail_canary());
    } else {
        std::cout << "[OK] Цілісність буфера збережено.\n";
    }
    return 0;
}
```
:::

## 3. Вплив вирівнювання пам'яті на ефективність канарок (Struct Padding)

При самостійній реалізації захисних структур із канарками необхідно враховувати правила апаратного вирівнювання даних (*Data Alignment*). На 64-бітній архітектурі x86-64 змінні типу `uint64_t` вимагають вирівнювання за адресами, кратними 8 байтам.

Якщо внутрішній буфер має розмір, не кратний 8 байтам (наприклад, `char raw_data[65]`), компілятор автоматично вставить 7 байтів невикористовуваного заповнення (*padding*) між кінцем масиву та полем `tail_canary`:

```
[ head_canary: 8 байтів ]
[ raw_data   : 65 байтів ]
[ padding    : 7 байтів  ] <- Невидима буферна зона компілятора!
[ tail_canary: 8 байтів ]
```

У такій структурі переповнення буфера на 1..7 байтів перезапише байти паддінгу, але **не досягне значення `tail_canary`**. У результаті функція верифікації поверне хибнопозитивний статус `is_valid() == true`, вважаючи пам'ять неушкодженою, тоді як неконтрольований запис уже відбувся.

Щоб усунути цей крайовий ефект, інженери застосовують два підходи:
1. Округлення розміру масиву до кратності 8 байтів (`sizeof(raw_data) % 8 == 0`);
2. Використання директиви упаковки структури `#pragma pack(push, 1)` або атрибута `__attribute__((packed))`, що змушує компілятор розміщувати хвостову канарку безпосередньо за останнім байтом масиву без проміжних прогалин.

## 4. Сторожові сторінки пам'яті ядра (Guard Pages через mmap)

Для динамічно виділених буферів критичної важливості (наприклад, криптографічних ключів або структур автентифікації) застосовується механізм апаратних сторожових сторінок (*Guard Pages*).

Замість виділення пам'яті через стандартний `malloc()` розробник виділяє три послідовні сторінки віртуальної пам'яті за допомогою системного виклику `mmap()`. Середня сторінка використовується для розміщення даних програми (`PROT_READ | PROT_WRITE`), тоді як перша та третя сторінки блокуються викликом `mprotect(addr, page_size, PROT_NONE)`:

```
[ Guard Page: PROT_NONE ] <- Звернення викликає апаратний SIGSEGV
[ Data Page : RW        ] <- Робочий буфер програми
[ Guard Page: PROT_NONE ] <- Переповнення миттєво падає у пастку MMU
```

Будь-яка спроба лінійного переповнення буфера за межі робочої сторінки або читання пам'яті до її початку негайно фіксується апаратним блоком MMU, викликаючи виняток сторінкового збою та аварійне завершення процесу без можливості виконання шеллкоду.

## 5. Практичні рекомендації щодо проектування захищених інтерфейсів

1. **Повна відмова від застарілих строкових функцій**: Виклики функцій `gets()`, `strcpy()`, `strcat()`, `sprintf()`, `scanf("%s")` повинні бути повністю заборонені в кодовій базі на рівні правил статичного аналізатора коду (`clang-tidy`, правила `cert-err33-c`, `clang-analyzer-security.insecureAPI.strcpy`).
2. **Перевірка місткості до виконання операції**: Будь-яка функція обробки даних має перевіряти умову `input_length < buffer_capacity` до початку запису в пам'ять, а не покладатися на зупинку копіювання при виявленні нульового байта.
3. **Використання об'єктів з фіксованими межами**: У сучасній розробці на C++ слід віддавати перевагу контейнерам `std::string`, `std::vector`, масивам фіксованого розміру `std::array` та неволодіючим представленням `std::string_view` і `std::span`, які гарантують збереження інформації про довжину масиву на всіх рівнях виклику.
4. **Контроль індексації у налагоджувальних збірках**: Для виявлення прихованих помилок виходу за межі діапазону в C++ слід використовувати метод `.at()` замість неперевіреного оператора індексації `[]`, або компілювати код із прапорцем `-D_GLIBCXX_ASSERTIONS`, який активує динамічні перевірки меж стандартних контейнерів.
5. **Стратегія обробки помилок переповнення**: При виявленні виходу за межі буфера функція повинна негайно очищати вихідний буфер (наприклад, `dest[0] = '\0'`) та повертати явний статус помилки (`false` або `std::unexpected`), запобігаючи використанню частково скопійованих або обрізаних даних у подальшій бізнес-логіці програми.
