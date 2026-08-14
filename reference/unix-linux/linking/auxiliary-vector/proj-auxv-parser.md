# ⚙️ Практична реалізація: парсинг auxv у просторі користувача

Двокомпонентний системний інструментарій мовами C та C++ здійснює безпосередній розбір та огляд допоміжного вектора ELF у просторі користувача. Перший модуль реалізує демаршалізацію бінарного псевдофайла `/proc/self/auxv` для вилучення системних характеристик поточного процесу з ядра, а другий модуль виконує низькорівневий обхід сирого стек-фрейму процесу в точці входу `_start` без використання системної бібліотеки C (glibc) чи будь-яких зовнішніх залежностей.

---

## 1. Демаршалізація бінарного потоку `/proc/self/auxv`

У користувацькому просторі операційної системи Linux псевдофайл `/proc/self/auxv` є найбільш універсальним і надійним джерелом даних про допоміжний вектор. На відміну від системної функції `getauxval()`, яка покладається на внутрішні глобальні змінні системної бібліотеки glibc, розбір `/proc/self/auxv` зчитує бінарний зліпок пам'яті, сформований безпосередньо ядром під час виконання системного виклику `execve`.

### Архітектурний механізм та особливості ядра

Коли користувацький процес запитує відкриття псевдофайла `/proc/self/auxv`, віртуальна файлова система Linux (VFS) та підсистема `procfs` звертаються до внутрішньої структури описувача процесу `struct task_struct` та об'єкта `mm_struct`. Ядро зберігає копію початкового допоміжного вектора у полях пам'яті процесу `mm->saved_auxv`.

Отримання даних через `/proc/self/auxv` має кілька суттєвих системних особливостей:
1. **Ізоляція привілеїв доступу**: Права на зчитування файла `/proc/<pid>/auxv` контролюються механізмом `PTRACE_MODE_READ_REALCREDS`. Звичайний процес може вільно читати власний вектор `/proc/self/auxv`. Проте доступ до вектора іншого процесу дозволено лише за умови, що спостерігач має той самий ідентифікатор користувача (`UID`) чи права суперкористувача `root`.
2. **Багатоархітектурність та сумісність**: Якщо 32-бітний бінарний файл виконується у 64-бітному ядрі Linux (наприклад, через шар сумісності x86_32 на x86_64), ядро гарантує, що псевдофайл `/proc/self/auxv` віддасть масив 32-бітних структур `Elf32_auxv_t` розміром 8 байтів кожна, адаптуючи бінарне представлення під розрядність процесу.
3. **Бінарна форматна узгодженість**: Дані віддаються у байтовому порядку (endianness) цільового процесу. На x86_64 та ARM64 (Little Endian) байти значень записано у стандартному порядку «від молодшого до старшого».

### Алгоритм демаршалізації бінарного масиву

Бінарний потік розглядається як послідовний масив структур `Elf64_auxv_t` (для 64-бітних архітектур) або `Elf32_auxv_t` (для 32-бітних). Кожен крок ітерації читає рівно 16 байтів даних з файла у буферний об'єкт. Послідовність кроків обробки включає:

1. **Відкриття файлового дескриптора**: Файл `/proc/self/auxv` відкривається системним викликом `open(2)` у режимі лише для читання (`O_RDONLY`).
2. **Послідовне зчитування структур**: У циклі системним викликом `read(2)` зчитуються блоки розміром `sizeof(Elf64_auxv_t)` у змінну буфера.
3. **Перевірка умові завершення**: Отриманий ключ порівнюється з константами `AT_*`. Якщо `a_type == AT_NULL` (числове значення `0`), розбір вектора миттєво припиняється, оскільки досягнуто термінатора масиву.
4. **Інтерпретація полів об'єднання `a_un`**:
   - Якщо тип запису відповідає симболічному вказівнику на текстовий рядок у пам'яті (наприклад, `AT_EXECFN` або `AT_PLATFORM`), значення `a_un.a_ptr` перетворюється на вказівник на рядок символів (`const char*`) і виводиться як текст.
   - Для всіх інших ключів поле `a_un.a_val` виводиться як 64-бітне ціле число та у шестнадцятковому форматі адреси.

Нижче наведено повну реалізацію демаршалізатора двома мовами з використанням суворих стандартів безпеки та ідіоматичних конструкцій C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>

static const char* auxv_type_to_string(uint64_t type) {
    switch (type) {
        case AT_NULL:          return "AT_NULL";
        case AT_IGNORE:        return "AT_IGNORE";
        case AT_EXECFD:        return "AT_EXECFD";
        case AT_PHDR:          return "AT_PHDR";
        case AT_PHENT:         return "AT_PHENT";
        case AT_PHNUM:         return "AT_PHNUM";
        case AT_PAGESZ:        return "AT_PAGESZ";
        case AT_BASE:          return "AT_BASE";
        case AT_FLAGS:         return "AT_FLAGS";
        case AT_ENTRY:         return "AT_ENTRY";
        case AT_NOTELF:        return "AT_NOTELF";
        case AT_UID:           return "AT_UID";
        case AT_EUID:          return "AT_EUID";
        case AT_GID:           return "AT_GID";
        case AT_EGID:          return "AT_EGID";
        case AT_PLATFORM:      return "AT_PLATFORM";
        case AT_HWCAP:         return "AT_HWCAP";
        case AT_CLKTCK:        return "AT_CLKTCK";
        case AT_SECURE:        return "AT_SECURE";
        case AT_BASE_PLATFORM: return "AT_BASE_PLATFORM";
        case AT_RANDOM:        return "AT_RANDOM";
        case AT_HWCAP2:        return "AT_HWCAP2";
        case AT_EXECFN:        return "AT_EXECFN";
        case AT_SYSINFO_EHDR:  return "AT_SYSINFO_EHDR";
        default:               return "AT_UNKNOWN";
    }
}

int parse_proc_auxv(void) {
    int fd = open("/proc/self/auxv", O_RDONLY);
    if (fd < 0) {
        perror("Помилка: не вдалося відкрити /proc/self/auxv");
        return -1;
    }

    Elf64_auxv_t entry;
    ssize_t bytes_read;

    printf("=== ДЕМАРШАЛІЗАЦІЯ /proc/self/auxv (C) ===\n");
    while ((bytes_read = read(fd, &entry, sizeof(entry))) == sizeof(entry)) {
        if (entry.a_type == AT_NULL) {
            printf("[%2lu] %-18s (0x00) -> КІНЕЦЬ ВЕКТОРА\n", (unsigned long)entry.a_type, "AT_NULL");
            break;
        }

        const char* name = auxv_type_to_string(entry.a_type);
        if (entry.a_type == AT_EXECFN || entry.a_type == AT_PLATFORM) {
            printf("[%2lu] %-18s -> %s\n", (unsigned long)entry.a_type, name, (const char*)entry.a_un.a_ptr);
        } else {
            printf("[%2lu] %-18s -> 0x%lx (%lu)\n", 
                   (unsigned long)entry.a_type, name, 
                   (unsigned long)entry.a_un.a_val, 
                   (unsigned long)entry.a_un.a_val);
        }
    }

    close(fd);
    return 0;
}

int main(void) {
    return parse_proc_auxv();
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <iomanip>
#include <filesystem>
#include <system_error>
#include <elf.h>

class AuxvProcParser {
public:
    static constexpr std::string_view type_to_string(uint64_t type) noexcept {
        switch (type) {
            case AT_NULL:          return "AT_NULL";
            case AT_IGNORE:        return "AT_IGNORE";
            case AT_EXECFD:        return "AT_EXECFD";
            case AT_PHDR:          return "AT_PHDR";
            case AT_PHENT:         return "AT_PHENT";
            case AT_PHNUM:         return "AT_PHNUM";
            case AT_PAGESZ:        return "AT_PAGESZ";
            case AT_BASE:          return "AT_BASE";
            case AT_FLAGS:         return "AT_FLAGS";
            case AT_ENTRY:         return "AT_ENTRY";
            case AT_UID:           return "AT_UID";
            case AT_EUID:          return "AT_EUID";
            case AT_GID:           return "AT_GID";
            case AT_EGID:          return "AT_EGID";
            case AT_PLATFORM:      return "AT_PLATFORM";
            case AT_HWCAP:         return "AT_HWCAP";
            case AT_CLKTCK:        return "AT_CLKTCK";
            case AT_SECURE:        return "AT_SECURE";
            case AT_RANDOM:        return "AT_RANDOM";
            case AT_HWCAP2:        return "AT_HWCAP2";
            case AT_EXECFN:        return "AT_EXECFN";
            case AT_SYSINFO_EHDR:  return "AT_SYSINFO_EHDR";
            default:               return "AT_UNKNOWN";
        }
    }

    static void parse() {
        std::ifstream file("/proc/self/auxv", std::ios::binary);
        if (!file.is_open()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити /proc/self/auxv");
        }

        std::cout << "=== ДЕМАРШАЛІЗАЦІЯ /proc/self/auxv (C++) ===\n";

        Elf64_auxv_t entry{};
        while (file.read(reinterpret_cast<char*>(&entry), sizeof(entry))) {
            if (entry.a_type == AT_NULL) {
                std::cout << "[" << std::setw(2) << entry.a_type << "] " 
                          << std::left << std::setw(18) << "AT_NULL" 
                          << " -> КІНЕЦЬ ВЕКТОРА\n";
                break;
            }

            const auto name = type_to_string(entry.a_type);
            std::cout << "[" << std::setw(2) << entry.a_type << "] " 
                      << std::left << std::setw(18) << name << " -> ";

            if (entry.a_type == AT_EXECFN || entry.a_type == AT_PLATFORM) {
                const char* str_ptr = reinterpret_cast<const char*>(entry.a_un.a_ptr);
                std::cout << (str_ptr ? str_ptr : "null") << "\n";
            } else {
                std::cout << "0x" << std::hex << entry.a_un.a_val 
                          << std::dec << " (" << entry.a_un.a_val << ")\n";
            }
        }
    }
};

int main() {
    try {
        AuxvProcParser::parse();
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## 2. Низькорівневий обхід сирого стека без системної бібліотеки C

При створенні власних мовних рантаймів (наприклад, розробці компіляторів або системних фреймворків для мов Go, Rust, Zig, чи баре-метал операційних систем) розробник працює в автономному середовищі (`-nostdlib`, `-ffreestanding`). У цьому стані стандартна C-бібліотека (glibc) відсутня, а функція `getauxval()` недоступна. Єдиним можливим способом отримати параметри завантаження є ручний аналіз сирого стек-фрейму у точці входу `_start`.

### Архітектура ассемблерного старту та передача регістрів

На архітектурі x86_64 згідно зі специфікацією System V AMD64 ABI, коли ядро закінчує виконання `execve` і передає керування ассемблерній точці входу `_start`, стан регістрів та стека відповідає наступним правилам:
- Вказівник стека `rsp` вказує на 64-бітне ціле число `argc`.
- Вказівник вершини стека `rsp` вирівняний ядром на межу 16 байтів перед передачею керування.
- Регістр `rdx` містить вказівник на функцію очищення фіналізаторів динамічного лінкера (або `NULL`).

Ассемблерний пролог точки входу `_start` копіює поточне значення `rsp` у перший аргумент виклику функції C (`rdi` на x86_64) і викликає C-функцію розбору стека:

```asm
.global _start
.type _start, @function
_start:
    xor %rbp, %rbp          /* Обнуляємо rbp для коректного unwinding відлагоджувача */
    mov (%rsp), %rdi        /* Перший аргумент C: argc (або сам %rsp) */
    mov %rsp, %rdi          /* Передаємо початковий вказівник %rsp у C-функцію */
    call parse_raw_stack_frame
    
    mov $60, %rax           /* Системний виклик exit (sys_exit) */
    xor %rdi, %rdi          /* Код повернення 0 */
    syscall
```

### Детальний алгоритм обходу фрейму стека

Отримавши початкову адресу `rsp` у просторі C, обхід здійснюється кроками за такою математичною та логічною схемою:

1. **Читання кількості аргументів `argc`**: Значення знаходиться за первинною адресою `*raw_rsp`.
2. **Розрахунок позиції `argv`**: Масив `argv` починається за адресою `raw_rsp + 1`. Він містить `argc` 64-бітних вказівників, за якими йде один нульовий термінатор `NULL`.
3. **Розрахунок позиції `envp`**: Масив `envp` починається одразу за нульовим вказівником `argv`, тобто за адресою `raw_rsp + 1 + argc + 1`.
4. **Пошук кінця масиву `envp`**: Цикл сканує елементи `envp` по 8 байтів до тих пір, поки не виявить нульовий термінатор `NULL` (`0x0000000000000000`).
5. **Початок масиву `auxv`**: Зсув на одне 64-бітне слово за нульовий термінатор `envp` дає точну віртуальну адресу першої структури `Elf64_auxv_t`.
6. **Ітерація векторів `auxv`**: Програмується цикл читання 16-байтових елементів `auxv` до появи запису з `a_type == AT_NULL`.

Нижче наведено приклад коду обходу сирого стека:

:::tabs
```c
#include <stdint.h>
#include <elf.h>

/* Функція ручного аналізу стека без залучення glibc */
void parse_raw_stack_frame(uint64_t *raw_rsp) {
    if (!raw_rsp) return;

    /* 1. Читаємо argc */
    uint64_t argc = *raw_rsp;
    uint64_t *argv = raw_rsp + 1;
    
    /* 2. Обчислюємо позицію envp: пропускаємо argc вказівників + 1 NULL термінатор */
    uint64_t *envp = argv + argc + 1;
    
    /* 3. Проходити масив envp до нульового термінатора */
    uint64_t *env_runner = envp;
    while (*env_runner != 0) {
        env_runner++;
    }
    
    /* 4. Зсув за NULL термінатор envp на початок auxv */
    env_runner++; 
    Elf64_auxv_t *auxv = (Elf64_auxv_t *)env_runner;

    /* 5. Цикл читання записів auxv */
    while (auxv->a_type != AT_NULL) {
        if (auxv->a_type == AT_PAGESZ) {
            uint64_t page_size = auxv->a_un.a_val;
            (void)page_size;
        } else if (auxv->a_type == AT_SYSINFO_EHDR) {
            void *vdso_ptr = auxv->a_un.a_ptr;
            (void)vdso_ptr;
        }
        auxv++;
    }
}
```
```cpp
#include <cstdint>
#include <span>
#include <optional>
#include <elf.h>

struct RawAuxvResult {
    std::uint64_t argc{0};
    const Elf64_auxv_t* auxv_head{nullptr};
};

class RawStackWalker {
public:
    static std::optional<RawAuxvResult> inspect(const std::uint64_t* raw_rsp) noexcept {
        if (!raw_rsp) return std::nullopt;

        const std::uint64_t argc = *raw_rsp;
        const std::uint64_t* argv = raw_rsp + 1;
        const std::uint64_t* envp = argv + argc + 1;

        const std::uint64_t* env_runner = envp;
        while (*env_runner != 0) {
            ++env_runner;
        }
        ++env_runner; // Зсув за NULL термінатор envp

        return RawAuxvResult{
            .argc = argc,
            .auxv_head = reinterpret_cast<const Elf64_auxv_t*>(env_runner)
        };
    }
};
```
:::

---

## 3. Практичні застереження та крайові випадки

1. **Гарантії вирівнювання**: Структури `Elf64_auxv_t` вимагають строгого вирівнювання за межею 8 байтів. Завдяки тому, що ядро вирівнює початковий `rsp` на 16 байтів, а всі елементи `argv` та `envp` мають розмір 8 байтів, вказівник на `auxv` завжди гарантовано вирівняний.
2. **Безпека при відсутності змінних середовища**: Якщо програма запускається у повністю очищеному оточенні без змінних середовища, масив `envp` містить рівно один елемент `NULL`. Алгоритм коректно пропустить цей єдиний `NULL` і перейде до `auxv`.
3. **Валідація вказівників на рядки**: При використанні полів `AT_EXECFN` чи `AT_PLATFORM` вказівники `a_ptr` посилаються на інформаційний блок рядків у вершині того самого стека. При написанні безпечних системних рантаймів перед розімкненням вказівника слід перевіряти, що адреса `a_ptr` знаходиться у межах дійсного адресного простору процесу.
