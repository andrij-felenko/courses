# ⚙️ Розпарсинг vDSO у пам'яті процесу: пошук символів та прямий виклик

Цей практичний проєкт присвячено створенню власного аналізатора та завантажувача vDSO на мовах C та C++. Опитувач знаходить базову адресу мапування vDSO через допоміжний вектор Auxiliary Vector (`auxv`), здійснює розпарсинг бінарних структур ELF-заголовків безпосередньо в оперативній пам'яті процесу, знаходить вказівник на символ `__vdso_clock_gettime` та виконує порівняльний бенчмарк швидкодії прямого vDSO-виклику проти традиційного системного виклику `syscall`.

## Покроковий алгоритм розпарсингу vDSO у пам'яті

Коли програма намагається отримати доступ до vDSO в обхід системних бібліотек (`glibc`, `musl`) або функцій завантаження dynamic loading (`dlopen`/`dlsym`), вона має виконати послідовний алгоритм обходу внутрішніх структур ELF у віртуальному адресному просторі:

1. **Отримання адреси з Auxiliary Vector**: Процес викликає функцію `getauxval(AT_SYSINFO_EHDR)` для отримання вказівника на базову адресу відображення vDSO.
2. **Перевірка заголовка ELF (Elf64_Ehdr)**: За отриманою адресою зчитується магічне число `\x7fELF` (байти `0x7F 0x45 0x4C 0x46`). Якщо сигнатура збігається, структура вважається валідним заголовком ELF.
3. **Сканування заголовків програм (Elf64_Phdr)**: Програма обходить таблицю сегментів `Program Headers` і знаходить сегмент із типом `PT_DYNAMIC`. Цей сегмент вказує на динамічну секцію розв'язання символів.
4. **Розбір динамічних тегів (Elf64_Dyn)**: З секції `PT_DYNAMIC` зчитуються вказівники на динамічну таблицю символів (`DT_SYMTAB`), таблицю рядків імен символів (`DT_STRTAB`) та хеш-таблицю символів (`DT_HASH` або `DT_GNU_HASH`).
5. **Пошук адреси символу**: Програма сканує масив структур `Elf64_Sym`. Для кожного символу зчитується зсув його імені в таблиці `.dynstr`. Коли назва символу збігається з `__vdso_clock_gettime`, вилучається значення поля `st_value`.
6. **Обчислення підсумкової адреси**: Оскільки vDSO є позиційно-незалежним об'єктом (PIC), абсолютна адреса функції в пам'яті обчислюється як сума базової адреси vDSO та значення `st_value`:
   ```
   abs_func_addr = vdso_base_address + sym.st_value
   ```
7. **Виклик по вказівнику**: Отримана адреса приводиться до сигнатури вказівника на функцію C і викликається напряму.

## Розбір хешування символів: DT_HASH проти DT_GNU_HASH

У стандартному ELF розв'язання символів може виконуватися або простим послідовним обходом таблиці `.dynsym`, або за допомогою хеш-таблиць для прискорення пошуку. У vDSO ядра Linux використовуються два типи хеш-таблиць:

1. **Класичний `DT_HASH`**: Класична хеш-таблиця System V ELF, яка містить масиви `buckets` та `chains`. Значення хешу обчислюється за стандартним алгоритмом `elf_hash()`.
2. **Оптимізований `DT_GNU_HASH`**: Сучасний хеш-фільтр Блума, розроблений GNU, який дозволяє відкинути неіснуючі символи за кілька бітових операцій без обходу ланцюжків пам'яті.

У наведеній нижче практичній реалізації застосовано універсальний лінійний обхід `.dynsym`, який надійно працює на будь-якій версії ядра Linux незалежно від типу хеш-таблиці vDSO.

## Крайові випадки та обробка помилок

Під час практичного використання аналізатора vDSO необхідно враховувати наступні крайові випадки та виняткові ситуації:

- **Відсутність vDSO в Auxiliary Vector**: Якщо ядро завантажено з параметром `vdso=0` або якщо програма виконується під спеціалізованим емулятором (наприклад, деякі застарілі версії QEMU user mode), функція `getauxval(AT_SYSINFO_EHDR)` повертає `0`. Парсер має коректно обробити це значення і переключитися на фолбек через `syscall`.
- **Пошкодження ELF-заголовка**: Якщо вказівник з `auxv` вказує на пошкоджену ділянку пам'яті, первинна перевірка перших чотирьох байтів `memcmp(ehdr->e_ident, ELFMAG, SELFMAG)` повертає помилку, запобігаючи краху програми від читання сміттєвих вказівників.
- **Втрата символу залежно від архітектури**: На різних архітектурах ім'я символу часу може відрізнятися (наприклад, `__vdso_clock_gettime` на x86_64 та `__kernel_clock_gettime` на ARM64). У промисловому коді необхідно перевіряти обидві варіанти назв.

## Порівняльний аналіз прямого зчитування та стандартного libc

При стандартному розв'язанні функцій у C-бібліотеці (наприклад, `glibc`), динамічний лінкер виконує аналогічний обхід `AT_SYSINFO_EHDR` на етапі запуску процесу та кешує знайдені вказівники у внутрішній таблиці функцій. Наш практичний приклад реалізує цей алгоритм вручну, що дає повне розуміння того, як саме стандартні системні бібліотеки позбуваються накладних витрат системного виклику.

## Практична реалізація аналізатора vDSO

Нижче наведено вихідний код аналізатора та бенчмарку vDSO двома мовами — ідіоматичним C та C++ (`:::tabs`). Версія C++ використовує сучасні концепції RAII, тип `std::expected` для обробки помилок без винятків, `std::string_view` для безпечної роботи із символами та модуль `std::chrono` для точного вимірювання часу.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/auxv.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <elf.h>

/* Сигнатура функції clock_gettime у vDSO */
typedef int (*vdso_clock_gettime_t)(clockid_t clk_id, struct timespec *tp);

/* Пошук символу у vDSO за базовою адресою ELF */
static const Elf64_Sym *find_vdso_symbol(uintptr_t vdso_base, const char *sym_name) {
    const Elf64_Ehdr *ehdr = (const Elf64_Ehdr *)vdso_base;
    
    /* Перевірка магічного числа ELF */
    if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
        return NULL;
    }

    const Elf64_Phdr *phdr = (const Elf64_Phdr *)(vdso_base + ehdr->e_phoff);
    const Elf64_Dyn *dyn = NULL;

    /* Пошук сегмента PT_DYNAMIC */
    for (size_t i = 0; i < ehdr->e_phnum; i++) {
        if (phdr[i].p_type == PT_DYNAMIC) {
            dyn = (const Elf64_Dyn *)(vdso_base + phdr[i].p_offset);
            break;
        }
    }

    if (!dyn) return NULL;

    const Elf64_Sym *symtab = NULL;
    const char *strtab = NULL;

    /* Вилучення адрес таблиць символів та рядків */
    for (const Elf64_Dyn *d = dyn; d->d_tag != DT_NULL; d++) {
        if (d->d_tag == DT_SYMTAB) {
            symtab = (const Elf64_Sym *)(vdso_base + d->d_un.d_ptr);
        } else if (d->d_tag == DT_STRTAB) {
            strtab = (const char *)(vdso_base + d->d_un.d_ptr);
        }
    }

    if (!symtab || !strtab) return NULL;

    /* Лінійний обхід динамічної таблиці символів */
    for (size_t i = 0; symtab[i].st_name != 0 || i == 0; i++) {
        if (i > 0 && symtab[i].st_name != 0) {
            const char *name = strtab + symtab[i].st_name;
            if (strcmp(name, sym_name) == 0) {
                return &symtab[i];
            }
        }
    }

    return NULL;
}

int main(void) {
    /* Крок 1: Зчитування адреси vDSO з Auxiliary Vector */
    unsigned long aux_vdso = getauxval(AT_SYSINFO_EHDR);
    if (!aux_vdso) {
        fprintf(stderr, "Помилка: vDSO не знайдено в Auxiliary Vector\n");
        return EXIT_FAILURE;
    }

    printf("[+] Базова адреса vDSO з AT_SYSINFO_EHDR: 0x%lx\n", aux_vdso);

    /* Крок 2: Пошук символу __vdso_clock_gettime */
    const char *target_sym = "__vdso_clock_gettime";
    const Elf64_Sym *sym = find_vdso_symbol(aux_vdso, target_sym);

    if (!sym) {
        fprintf(stderr, "Помилка: Символ %s не знайдено у vDSO\n", target_sym);
        return EXIT_FAILURE;
    }

    /* Крок 3: Обчислення адреси вказівника на функцію */
    vdso_clock_gettime_t vdso_fn = (vdso_clock_gettime_t)(aux_vdso + sym->st_value);
    printf("[+] Знайдено символ %s за адресою: %p\n", target_sym, (void *)vdso_fn);

    struct timespec ts_vdso, ts_syscall;
    const int iterations = 5000000;

    /* Крок 4: Вимірювання часу виконання vDSO */
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < iterations; i++) {
        vdso_fn(CLOCK_REALTIME, &ts_vdso);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double vdso_time = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;

    /* Крок 5: Вимірювання часу виконання прямого системного виклику syscall */
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < iterations; i++) {
        syscall(SYS_clock_gettime, CLOCK_REALTIME, &ts_syscall);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double syscall_time = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;

    /* Крок 6: Вивід результатів бенчмарку */
    printf("\n=== Результати бенчмарку продуктивності (%d викликів) ===\n", iterations);
    printf("Час виконання vDSO:     %.4f сек (%.2f ns/call)\n", vdso_time, (vdso_time / iterations) * 1e9);
    printf("Час виконання syscall:  %.4f сек (%.2f ns/call)\n", syscall_time, (syscall_time / iterations) * 1e9);
    printf("Прискорення vDSO:       у %.2f разів швидше!\n", syscall_time / vdso_time);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <span>
#include <expected>
#include <chrono>
#include <cstring>
#include <sys/auxv.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <elf.h>

class VdsoParser {
public:
    using ClockGetTimeFn = int (*)(clockid_t, struct timespec*);

    // Фабричний метод створення парсера з валідацією auxv
    static std::expected<VdsoParser, std::string_view> create() noexcept {
        uintptr_t base = getauxval(AT_SYSINFO_EHDR);
        if (!base) {
            return std::unexpected("vDSO address missing in Auxiliary Vector");
        }
        return VdsoParser(base);
    }

    // Безпечний пошук символу vDSO без винятків
    [[nodiscard]] std::expected<ClockGetTimeFn, std::string_view> findSymbol(std::string_view sym_name) const noexcept {
        const auto* ehdr = reinterpret_cast<const Elf64_Ehdr*>(m_base);
        
        if (std::memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
            return std::unexpected("Invalid ELF header magic in vDSO");
        }

        const auto* phdr = reinterpret_cast<const Elf64_Phdr*>(m_base + ehdr->e_phoff);
        const Elf64_Dyn* dyn = nullptr;

        for (size_t i = 0; i < ehdr->e_phnum; ++i) {
            if (phdr[i].p_type == PT_DYNAMIC) {
                dyn = reinterpret_cast<const Elf64_Dyn*>(m_base + phdr[i].p_offset);
                break;
            }
        }

        if (!dyn) return std::unexpected("PT_DYNAMIC segment not found");

        const Elf64_Sym* symtab = nullptr;
        const char* strtab = nullptr;

        for (const auto* d = dyn; d->d_tag != DT_NULL; ++d) {
            if (d->d_tag == DT_SYMTAB) {
                symtab = reinterpret_cast<const Elf64_Sym*>(m_base + d->d_un.d_ptr);
            } else if (d->d_tag == DT_STRTAB) {
                strtab = reinterpret_cast<const char*>(m_base + d->d_un.d_ptr);
            }
        }

        if (!symtab || !strtab) return std::unexpected("Dynamic symbol table or string table missing");

        for (size_t i = 0; symtab[i].st_name != 0 || i == 0; ++i) {
            if (i > 0 && symtab[i].st_name != 0) {
                std::string_view name{strtab + symtab[i].st_name};
                if (name == sym_name) {
                    auto fn_addr = m_base + symtab[i].st_value;
                    return reinterpret_cast<ClockGetTimeFn>(fn_addr);
                }
            }
        }

        return std::unexpected("Requested symbol not found in vDSO");
    }

    [[nodiscard]] uintptr_t baseAddress() const noexcept { return m_base; }

private:
    explicit VdsoParser(uintptr_t base) noexcept : m_base(base) {}
    uintptr_t m_base;
};

int main() {
    auto parser_res = VdsoParser::create();
    if (!parser_res) {
        std::cerr << "Error: " << parser_res.error() << '\n';
        return 1;
    }

    const auto& parser = *parser_res;
    std::cout << "[+] vDSO base address: 0x" << std::hex << parser.baseAddress() << std::dec << '\n';

    constexpr std::string_view target_symbol = "__vdso_clock_gettime";
    auto fn_res = parser.findSymbol(target_symbol);

    if (!fn_res) {
        std::cerr << "Error finding symbol: " << fn_res.error() << '\n';
        return 1;
    }

    auto vdso_clock_gettime = *fn_res;
    std::cout << "[+] Found " << target_symbol << " at: " << reinterpret_cast<void*>(vdso_clock_gettime) << '\n';

    constexpr int iterations = 5000000;
    struct timespec ts{};

    // Бенчмарк vDSO викликів
    auto t0 = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iterations; ++i) {
        vdso_clock_gettime(CLOCK_REALTIME, &ts);
    }
    auto t1 = std::chrono::high_resolution_clock::now();

    // Бенчмарк прямого системного виклику syscall
    auto t2 = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iterations; ++i) {
        syscall(SYS_clock_gettime, CLOCK_REALTIME, &ts);
    }
    auto t3 = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double, std::milli> vdso_ms = t1 - t0;
    std::chrono::duration<double, std::milli> syscall_ms = t3 - t2;

    std::cout << "\n=== Performance Results (" << iterations << " calls) ===\n";
    std::cout << "vDSO time:     " << vdso_ms.count() << " ms (" << (vdso_ms.count() * 1e6 / iterations) << " ns/call)\n";
    std::cout << "Syscall time:  " << syscall_ms.count() << " ms (" << (syscall_ms.count() * 1e6 / iterations) << " ns/call)\n";
    std::cout << "Speedup ratio: " << (syscall_ms.count() / vdso_ms.count()) << "x faster\n";

    return 0;
}
```
:::

## Інструкція з компіляції та відлагодження

Для збірки наведеного сирцевого коду у середовищі Linux використовуйте стандартний компілятор GCC або Clang з підтримкою стандарту C++23 (для розширень `std::expected` та `std::span`):

```bash
# Компіляція C-версії
gcc -O3 -std=c11 vdso_dump.c -o vdso_dump_c

# Компіляція C++-версії (вимагає GCC 13+ або Clang 16+)
g++ -O3 -std=c++23 vdso_dump.cpp -o vdso_dump_cpp
```

Для аналізу отриманого покажчика під відлагоджувачем `gdb` можна використати наступну послідовність команд:

```text
(gdb) break main
(gdb) run
(gdb) info target
(gdb) x/10i vdso_fn
```

## Інтерпретація отриманих результатів

При запуску згенерованого бінарного файлу програма продемонструє суттєву відмінність у продуктивності між двома підходами:

1. **vDSO-виклик**: Повідомляє про час виконання близько **10–14 наносекунд на виклик**. Оскільки інструкції виконуються безпосередньо у просторі користувача, затримка визначається лише швидкістю читання регістра `rdtsc` та арифметичними операціями в CPU.
2. **Прямий системний виклик (`syscall`)**: Повідомляє про час виконання близько **150–220 наносекунд на виклик**. Затримка зумовлена апаратними перемиканнями Ring 3 у Ring 0, збереженням регістрів у `pt_regs` та обробкою бар'єрів KPTI.

Отже, використання vDSO забезпечує прискорення отримання системного часу у **13–18 разів**, позбавляючи процесор непотрібного навантаження при високій частоті запитів. Практичний розбір показує, що власна ініціалізація vDSO дозволяє створювати високопродуктивні рантайми та низькорівневі системні утиліти з прямою оптимізацією доступу до часу ядра.
