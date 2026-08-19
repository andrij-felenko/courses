# ⚙️ AddressSanitizer: виявлення Use-After-Free та висячого стека на практиці

Коли програма звертається до пам'яті за недійсним вказівником, операційна система найчастіше мовчить. Віртуальна сторінка пам'яті залишається відображеною в адресному просторі процесу, байти фізично доступні для читання й запису, а стандартний алокатор не повертає щойно звільнені блоки ядру негайно. У результаті пошкодження даних відбувається безшумно: функція записує нові значення поверх чужого стекового кадру або у звільнений вузол купи, а аварійне завершення трапляється через мільйони тактів в іншій частині системи.

Інструмент **AddressSanitizer** (скорочено **ASan**, розроблений 2011 року Костянтином Серебряним зі співавторами в Google) перетворює приховані дефекти пам'яті на миттєві контрольовані аварії в точці несанкціонованого доступу. Для цього він об'єднує компіляторне перетворення інструкцій доступу до пам'яті (інструментацію в LLVM/GCC) та власну бібліотеку часу виконання (runtime library) зі спеціалізованим алокатором.

## Математика тіньової пам'яті (Shadow Memory)

Головна архітектурна ідея AddressSanitizer — розділення всього віртуального адресного простору на дві частини: пам'ять програми та **тіньову пам'ять** (англ. *shadow memory*). Кожні 8 байтів звичайної пам'яті процесу відображаються рівно в **1 байт** тіньової пам'яті. Цей коефіцієнт стиснення 8:1 дає змогу кодувати стан доступності адрес із мінімальними накладними витратами на обчислення та пам'ять.

Для 64-розрядних систем (зокрема x86-64 Linux) адреса тіньового байта обчислюється однозначним бітовим зсувом і додаванням фіксованого базового зміщення:

```
ShadowAddress = (AppAddress >> 3) + 0x7fff8000
```

Оскільки кожен алокований блок пам'яті вирівнюється за адресою, кратною принаймні 8 байтам, будь-яка послідовна 8-байтна ділянка в пам'яті програми перебуває в одному з кількох станів:

- **0x00**: Усі 8 байтів повністю валідні для читання та запису.
- **0x01 .. 0x07**: Лише перші `k` байтів валідні, а решта `8 - k` байтів належать до забороненої червоної зони (наприклад, якщо об'єкт мав розмір 13 байтів: перший 8-байтний блок має тінь `0x00`, другий — `0x05`, тобто перші 5 байтів валідні, а 3 — заблоковані).
- **Від'ємні значення (0x80 .. 0xFF)**: Уся 8-байтна ділянка повністю отруєна (англ. *poisoned*) і недоступна.

Кожен тип забороненої зони має власний магічний код у тіньовому байті:

| Тіньовий байт | Назва стану | Походження блокування |
|---|---|---|
| `0x00` | Addressable | Пам'ять належить живому об'єкту |
| `0x01` .. `0x07` | Partial tail | Останній неповний блок живого об'єкта |
| `0xFD` | Heap Left / Freed | Пам'ять купи звільнена (`delete` / `free`) — маркер Use-After-Free |
| `0xFA` | Heap Redzone | Червона зона навколо виділеного блока в купі |
| `0xF1` | Stack Left Redzone | Ліва червона зона стекового кадру |
| `0xF2` | Stack Mid Redzone | Проміжна червона зона між локальними змінними |
| `0xF3` | Stack Right Redzone | Права червона зона стекового кадру |
| `0xF5` | Stack Use-After-Return | Кадр стека завершив роботу й був отруєний |
| `0xF8` | Stack Use-After-Scope | Локальна змінна вийшла з блоку `{ ... }` |
| `0xBB` | Global Redzone | Червона зона навколо глобальної або статичної змінної |

## Алокатор ASan та черга карантину (Quarantine Queue)

Чому звичайний системний алокатор пропускає більшість помилок Use-After-Free під час тестування? Якщо програма викликає `free(p)`, а потім негайно `malloc(sizeof(T))`, стандартний менеджер пам'яті (як-от `ptmalloc` у glibc або `jemalloc`) з високою ймовірністю поверне ту саму адресу `p` для нового виділення, щоб оптимізувати використання кешів процесора. Тоді старий висячий вказівник читає або перезаписує вже нові дані, але не викликає апаратної помилки сегментації (Segmentation Fault), маскуючи дефект аж до релізу.

AddressSanitizer замінює системні функції `malloc`, `calloc`, `free`, `realloc` та оператори `new`/`delete` власним алокатором. Коли виконується звільнення пам'яті:

1. Пам'ять об'єкта не повертається операційній системі та не віддається під наступні запити на виділення.
2. Усі тіньові байти, що відповідають тілу об'єкта, записуються магічним значенням `0xFD` (Freed Heap Region).
3. Звільнений блок поміщається у **чергу карантину** (англ. *quarantine queue*).
4. Блок залишається в карантині доти, доки сумарний обсяг звільненої пам'яті не перевищить ліміт карантину (за замовчуванням 256 МБ). Тільки після витіснення з черги за принципом FIFO пам'ять може бути повторно використана.
5. Навколо кожного блоку створюються штучні червоні зони (значення `0xFA` розміром від 16 до 2048 байтів), що унеможливлює непомітний вихід за межі масиву навіть на один байт.

Завдяки карантину будь-яке звернення до звільненого вузла гарантовано натрапляє на отруєну тінь `0xFD` і негайно перехоплюється.

## Інструментація коду компілятором у LLVM

Під час трансляції вихідного коду оптимізатор LLVM запускає компіляторний прохід `AddressSanitizerPass`. Прохід сканує проміжне представлення (LLVM IR) і знаходить усі інструкції читання (`load`) та запису (`store`).

Перед кожним зверненням компілятор вставляє код прямої перевірки тіньової пам'яті. Звичайний запис 4-байтного цілого числа:

```cpp
*ptr = 42;
```

Компілятор розгортає в таку еквівалентну послідовність низькорівневих перевірок:

```cpp
char* shadow = reinterpret_cast<char*>((reinterpret_cast<uintptr_t>(ptr) >> 3) + 0x7fff8000);
int8_t shadow_val = *shadow;

if (shadow_val != 0) {
    // Якщо байт не нульовий, перевіряємо, чи дозволений доступ до останнього байта
    if (shadow_val < 0 || (static_cast<int8_t>(reinterpret_cast<uintptr_t>(ptr) & 7) + 3) >= shadow_val) {
        __asan_report_store4(reinterpret_cast<uintptr_t>(ptr));
    }
}

*ptr = 42;
```

На рівні асемблера x86-64 для прямого 8-байтного звернення перевірка зводиться лише до чотирьох машинних інструкцій:

```nasm
movq    %rax, %rcx
shrq    $3, %rcx
movb    0x7fff8000(%rcx), %cl
testb   %cl, %cl
jne     .L_asan_report_error
movq    $42, (%rax)
```

Якщо тіньовий байт дорівнює нулю (дозволена зона), прапорець нуля процесора виставляється в 1, умовний перехід не спрацьовує, і запис виконується без жодної затримки на системні виклики.

## Відтворення Heap-Use-After-Free на практиці

Розгляньмо практичну ситуацію: внутрішній буфер динамічного масиву релокується під час зростання, тоді як зовнішній код утримує пряме посилання або вказівник на один із його елементів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int id;
    char name[32];
} Session;

typedef struct {
    Session* data;
    size_t size;
    size_t capacity;
} SessionVector;

void vector_init(SessionVector* v, size_t cap) {
    v->data = (Session*)malloc(cap * sizeof(Session));
    v->size = 0;
    v->capacity = cap;
}

void vector_push(SessionVector* v, int id, const char* name) {
    if (v->size >= v->capacity) {
        size_t new_cap = v->capacity * 2;
        Session* new_data = (Session*)malloc(new_cap * sizeof(Session));
        memcpy(new_data, v->data, v->size * sizeof(Session));
        free(v->data); // Старий буфер звільнено!
        v->data = new_data;
        v->capacity = new_cap;
    }
    v->data[v->size].id = id;
    strncpy(v->data[v->size].name, name, sizeof(v->data[v->size].name) - 1);
    v->data[v->size].name[sizeof(v->data[v->size].name) - 1] = '\0';
    v->size++;
}

int main(void) {
    SessionVector vec;
    vector_init(&vec, 2);
    vector_push(&vec, 101, "AdminAuth");
    vector_push(&vec, 102, "UserGuest");

    // Зберігаємо прямий вказівник на перший елемент
    Session* primary = &vec.data[0];

    // Додавання третього елемента викликає релокацію та free(v->data)
    vector_push(&vec, 103, "ServiceWorker");

    // Помилка: primary вказує на звільнений буфер (Heap-Use-After-Free)
    printf("Сесія ID: %d, Назва: %s\n", primary->id, primary->name);

    free(vec.data);
    return 0;
}
```
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>

struct Session {
    int id;
    std::string name;
};

int main() {
    std::vector<Session> sessions;
    sessions.reserve(2);
    sessions.push_back({101, "AdminAuth"});
    sessions.push_back({102, "UserGuest"});

    // Зберігаємо посилання на перший елемент
    const Session& primary = sessions[0];

    // Додавання третього елемента перевищує reserve(2) і спричиняє релокацію буфера
    sessions.push_back({103, "ServiceWorker"});

    // Помилка: primary дивиться на старий звільнений буфер (Heap-Use-After-Free)
    std::cout << "Сесія ID: " << primary.id << ", Назва: " << primary.name << '\n';

    return 0;
}
```
:::

Збережемо код у файл `uaf_demo.cpp` та скомпілюємо з підтримкою AddressSanitizer і налагоджувальними символами:

```bash
clang++ -O1 -g -fsanitize=address uaf_demo.cpp -o uaf_demo
./uaf_demo
```

### Розбір звіту ASan для Heap-Use-After-Free

Після запуску бінарника AddressSanitizer миттєво зупиняє виконання програми та генерує структурований аварійний звіт:

```text
=================================================================
==84920==ERROR: AddressSanitizer: heap-use-after-free on address 0x603000000040 at pc 0x0000004f21ab bp 0x7ffd9b8e0120 sp 0x7ffd9b8e0118
READ of size 4 at 0x603000000040 thread T0
    #0 0x4f21aa in main /home/user/uaf_demo.cpp:23:34
    #1 0x7f9b8c229d8f in __libc_start_call_main csu/../sysdeps/nptl/libc_start_call_main.h:58:16
    #2 0x7f9b8c229e3f in __libc_start_main csu/../csu/libc-start.c:392:3
    #3 0x41b2e4 in _start (/home/user/uaf_demo+0x41b2e4)

0x603000000040 is located 0 bytes inside of 64-byte region [0x603000000040,0x603000000080)
freed by thread T0 here:
    #0 0x4c332d in operator delete(void*, unsigned long) (/home/user/uaf_demo+0x4c332d)
    #1 0x4f2890 in std::allocator_traits<std::allocator<Session>>::deallocate(...) /usr/include/c++/13/bits/alloc_traits.h:516:13
    #2 0x4f2430 in std::vector<Session>::_M_realloc_insert(...) /usr/include/c++/13/bits/vector.tcc:513:7
    #3 0x4f2081 in main /home/user/uaf_demo.cpp:20:14

previously allocated by thread T0 here:
    #0 0x4c2acd in operator new(unsigned long) (/home/user/uaf_demo+0x4c2acd)
    #1 0x4f2710 in std::allocator_traits<std::allocator<Session>>::allocate(...) /usr/include/c++/13/bits/alloc_traits.h:482:20
    #2 0x4f22e0 in std::vector<Session>::reserve(unsigned long) /usr/include/c++/13/bits/vector.tcc:79:21
    #3 0x4f1f50 in main /home/user/uaf_demo.cpp:14:14

Shadow bytes around the buggy address:
  0x1c0600000000: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x1c0600000010: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
=>0x1c0600000020: fa fa fa fa fa fa fa fa[fd]fd fd fd fd fd fd fd
  0x1c0600000030: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
Shadow byte legend (one shadow byte represents 8 application bytes):
  Addressable:           00
  Partially addressable: 01 02 03 04 05 06 07 
  Heap left redzone:     fa
  Freed heap region:     fd
  Stack left redzone:    f1
  Stack right redzone:   f3
=================================================================
```

Звіт містить усю необхідну діагностику для негайної локалізації дефекту:
1. **Точка помилки (`READ of size 4`)**: показує точний файл і номер рядка (`uaf_demo.cpp:23`), де код спробував прочитати `primary.id`.
2. **Точка звільнення (`freed here`)**: відображає стек викликів, який знищив вихідний буфер усередині `std::vector::_M_realloc_insert` на рядку 20 під час `push_back`.
3. **Точка виділення (`previously allocated here`)**: документує місце первинного створення буфера у `reserve(2)` на рядку 14.
4. **Тіньовий дамп (`Shadow bytes`)**: байт `[fd]` наочно підтверджує, що пам'ять за цією адресою була помічена як звільнена з купи.

## Виявлення висячого стека (Stack-Use-After-Return)

Помилки звернення до стекових змінних, кадр яких уже розкручено (англ. *Stack-Use-After-Return*), вимагають додаткового налаштування. За замовчуванням ASan отруює червоні зони між стековими змінними та очищає змінні при виході з внутрішніх блоків (Use-After-Scope). Але звичайне повернення з функції зміщує вказівник стека `RSP` вгору без запису в тіньову пам'ять кожного разу, щоб не сповільнювати швидкі виклики функцій.

Для повного виявлення висячих посилань на стек використовується спеціальний режим **Fake Stack** (фальшивий стек).

### Приклад дефекту висячого стека

:::tabs
```c
#include <stdio.h>

const int* get_multiplier(void) {
    int factor = 10;
    return &factor; // Повертає адресу локальної змінної стека
}

void overwrite_stack(void) {
    volatile double array[32];
    for (int i = 0; i < 32; ++i) array[i] = 3.14159;
}

int main(void) {
    const int* p = get_multiplier();
    
    overwrite_stack(); // Перезаписує звільнений кадр
    
    // Невизначена поведінка: читання з розкрученого стека
    printf("Значення коефіцієнта: %d\n", *p);
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <string>

std::string_view format_greeting(const std::string& name) {
    std::string message = "Привіт, " + name + "!";
    return std::string_view(message); // Повертає view на тимчасовий локальний об'єкт
}

void overwrite_stack() {
    volatile double array[32];
    for (int i = 0; i < 32; ++i) array[i] = 3.14159;
}

int main() {
    std::string_view greeting = format_greeting("Олексій");
    
    overwrite_stack(); // Перезаписує пам'ять старого кадру
    
    // Помилка: читання мертвого стека через string_view
    std::cout << greeting << '\n';
    return 0;
}
```
:::

### Увімкнення та діагностика Fake Stack

Складемо програму з прапорцем `-fsanitize=address`:

```bash
clang++ -O1 -g -fsanitize=address stack_demo.cpp -o stack_demo
```

Запускаємо програму, передавши параметр середовища `ASAN_OPTIONS`:

```bash
export ASAN_OPTIONS=detect_stack_use_after_return=1:check_initialization_order=1
./stack_demo
```

Коли увімкнено `detect_stack_use_after_return=1`, середовище виконання ASan підміняє апаратний стек для локальних змінних: змінні розміщуються в динамічно виділених блоках пам'яті (Fake Stack). На виході з функції блок негайно отруюється байтами `0xF5` (Stack Use-After-Return).

AddressSanitizer миттєво фіксує несанкціонований доступ:

```text
=================================================================
==85104==ERROR: AddressSanitizer: stack-use-after-return on address 0x7f1e4a200020 at pc 0x0000004e924a bp 0x7ffd5102a9b0 sp 0x7ffd5102a170
READ of size 14 at 0x7f1e4a200020 thread T0
    #0 0x4e9249 in std::basic_string_view<char>::data() const ...
    #1 0x4e8fc1 in main /home/user/stack_demo.cpp:21:18

Address 0x7f1e4a200020 is located in stack of thread T0 at offset 32 in frame
    #0 0x4e8c50 in format_greeting(std::string const&) /home/user/stack_demo.cpp:5

  This frame has 1 object(s):
    [32, 64) 'message' <== Memory access at offset 32 is inside this variable
Shadow byte legend:
  Stack use after return: f5
=================================================================
```

## Ручне отруєння пам'яті у власних алокаторах

Якщо проект використовує власні структури пам'яті (арени, пули пам'яті, кільцеві буфери або кастомні контейнери), системний алокатор викликається рідко (наприклад, один раз виділяється велика арена на 100 МБ). У такому разі ASan не знає, коли окремий об'єкт всередині арени був «звільнений» логікою програми, оскільки системний виклик `free` не відбувається.

Для інтеграції власних алокаторів заголовок `<sanitizer/asan_interface.h>` надає інтерфейс прямого ручного отруєння:

- `ASAN_POISON_MEMORY_REGION(addr, size)`: позначає діапазон як заборонений для доступу (отруює відповідні тіньові байти).
- `ASAN_UNPOISON_MEMORY_REGION(addr, size)`: відновлює дозвіл на читання та запис для діапазону.

Ось приклад власного пулу пам'яті з підтримкою діагностики ASan:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <sanitizer/asan_interface.h>

typedef struct {
    char buffer[1024];
    size_t offset;
} SimpleArena;

void arena_init(SimpleArena* a) {
    a->offset = 0;
    // Спочатку вся пам'ять арени отруєна
    ASAN_POISON_MEMORY_REGION(a->buffer, sizeof(a->buffer));
}

void* arena_alloc(SimpleArena* a, size_t size) {
    if (a->offset + size > sizeof(a->buffer)) return NULL;
    void* ptr = &a->buffer[a->offset];
    a->offset += size;
    // Відкриваємо доступ лише до виділеного діапазону
    ASAN_UNPOISON_MEMORY_REGION(ptr, size);
    return ptr;
}

void arena_reset(SimpleArena* a) {
    a->offset = 0;
    // Знову отруюємо всю пам'ять арени при скиданні
    ASAN_POISON_MEMORY_REGION(a->buffer, sizeof(a->buffer));
}

int main(void) {
    SimpleArena arena;
    arena_init(&arena);

    int* val = (int*)arena_alloc(&arena, sizeof(int));
    *val = 100;

    arena_reset(&arena); // Логічне звільнення всієї арени

    // Спроба звернення після reset викличе миттєву помилку ASan!
    printf("Значення: %d\n", *val);

    return 0;
}
```
```cpp
#include <iostream>
#include <cstddef>
#include <vector>
#include <sanitizer/asan_interface.h>

template <size_t TotalBytes = 1024>
class CustomArena {
    alignas(std::max_align_t) std::byte storage_[TotalBytes];
    size_t offset_{0};

public:
    CustomArena() {
        // Позначаємо всю пам'ять як заблоковану
        ASAN_POISON_MEMORY_REGION(storage_, TotalBytes);
    }

    ~CustomArena() {
        // Очищаємо перед знищенням
        ASAN_UNPOISON_MEMORY_REGION(storage_, TotalBytes);
    }

    void* allocate(size_t bytes) {
        size_t aligned = (bytes + alignof(std::max_align_t) - 1) & ~(alignof(std::max_align_t) - 1);
        if (offset_ + aligned > TotalBytes) return nullptr;
        void* ptr = &storage_[offset_];
        offset_ += aligned;
        // Відкриваємо доступ лише для алокованого блоку
        ASAN_UNPOISON_MEMORY_REGION(ptr, bytes);
        return ptr;
    }

    void reset() {
        offset_ = 0;
        // При скиданні знову блокуємо весь масив
        ASAN_POISON_MEMORY_REGION(storage_, TotalBytes);
    }
};

int main() {
    CustomArena<512> arena;

    int* num = static_cast<int*>(arena.allocate(sizeof(int)));
    *num = 42;

    arena.reset(); // Скидання арени

    // Помилка: ASan перехопить Use-After-Free навіть у кастомній арені
    std::cout << "Число: " << *num << '\n';

    return 0;
}
```
:::

## Налагодження звітів ASan у GDB та керування опціями

Коли ASan виявляє аварію, процес за замовчуванням виводить звіт у консоль і завершує виконання. Проте в процесі розробки значно зручніше зупинити виконання безпосередньо у відладчику (GDB або LLDB) в момент першого невалідного звернення, щоб перевірити значення змінних та ланцюжок викликів.

Для цього у GDB достатньо встановити точку зупинки на спеціальну внутрішню функцію санітайзера:

```bash
gdb ./uaf_demo
(gdb) break __asan_on_error
(gdb) run
```

Коли спрацьовує дефект, GDB зупиняє виконання програми на точці помилки. Прямо у відладчику можна перевірити стан тіньової пам'яті за адресою через формулу відображення:

```gdb
(gdb) print *(char*)(((uintptr_t)primary >> 3) + 0x7fff8000)
$1 = -3 '\375'  # 0xFD — підтвердження стану Heap-Freed
```

Конфігурація поведінки санітайзера здійснюється через змінну середовища `ASAN_OPTIONS`. Найкорисніші прапорці для повсякденної діагностики:

- `abort_on_error=1`: замість виклику `_exit(1)` генерує сигнал `SIGABRT`, що дає змогу операційній системі створити дамп пам'яті (core dump).
- `quarantine_size_mb=512`: збільшує розмір черги карантину для довгих сценаріїв тестування.
- `strict_string_checks=1`: активує перевірку висячих вказівників і переповнень у стандартних функціях обробки рядків (`strlen`, `strcpy`, `memcmp`).
- `suppressions=asan.supp`: підключає файл винятків для ігнорування відомих багів у сторонніх закритих динамічних бібліотеках.

## Інтеграція в цикл безперервної інтеграції (CI/CD)

AddressSanitizer споживає приблизно у 1.5–2 рази більше процесорного часу та збільшує використання оперативної пам'яті у 2–3 рази. Ця плата робить його непридатним для фінальних релізних збірок під високим навантаженням у реальному часі, проте є обов'язковим інженерним стандартом для:

1. **Прогону модульних та інтеграційних тестів (Unit / Integration Tests)**: регулярне виконання тестового набору під ASan та UBSan (UndefinedBehaviorSanitizer) гарантує відсутність прихованого виходу за межі пам'яті та Use-After-Free.
2. **Фаззингу (Fuzz Testing через LLVM libFuzzer / AFL++)**: поєднання фаззера, який генерує мільйони псевдовипадкових вхідних даних, із санітайзером пам'яті дає змогу виявляти складні граничні випадки інвалідації посилань.
3. **Режиму розробки (Debug / Sanitized Builds)**: складання локальних тестових бінарників із санітайзерами скорочує час пошуку багів пам'яті від днів до кількох секунд.

Поєднання апаратно-підтримуваного та компіляторного аналізу AddressSanitizer із попередньою статичною діагностикою повністю виключає виникнення непомітних дефектів Use-After-Free у виробничому коді.
