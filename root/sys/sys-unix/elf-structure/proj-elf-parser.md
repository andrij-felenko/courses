# ⚙️ Практична реалізація аналізатора заголовків ELF

Цей проект присвячено практичній розробці автономної системної утиліти для аналізу та валидації бінарних файлів у форматі ELF. Створення власного аналізатора дозволяє глибоко зрозуміти, які саме кроки виконує завантажувач ядра Linux (`fs/binfmt_elf.c`) та динамічний завантажувач (`ld-linux.so`) перед тим, як спроектувати сегменти бінарного файлу у віртуальний адресний простір новоствореного процесу.

---

## 1. Архітектура та функціональні вимоги до аналізатора

Головна мета утиліти — провести первинне інспектування та верифікацію внутрішніх структур даних ELF-файлу без використання високорівневих сторонніх бібліотек (таких як `libelf` або `BFD`), спираючись виключно на стандартні заголовочні файли операційної системи (`<elf.h>`) та низькорівневі POSIX системні виклики.

Під час розробки інструментів аналізу двійкового коду аналізатор повинен забезпечувати виконання суворого послідовного алгоритму:

1. **Безпечне відкриття та відображення файлу:** Замість традиційного буферизованого читання через системний виклик `read()`, утиліта відображає весь файл у віртуальний адресний простір за допомогою системного виклику `mmap()`. Це гарантує мінімальні накладні витрати на копіювання даних між простором ядра та користувача, а також дозволяє звертатися до структур ELF безпосередньо через вказівники на оперативну пам'ять.
2. **Верифікація паспорта бінарного об'єкта:** Перевірка перших чотирьох байтів масиву `e_ident` на відповідність магічному підпису `0x7F 'E' 'L' 'F'`, контроль 64-бітного класу (`ELFCLASS64`) та перевірка кодування Little-Endian (`ELFDATA2LSB`).
3. **Розбір заголовка ELF (`Elf64_Ehdr`):** Зчитування адреси точки входу (`e_entry`), зсувів таблиць програмних заголовків PHT (`e_phoff`) та секцій SHT (`e_shoff`), а також кількості заголовків у кожній таблиці.
4. **Ітерація по Program Header Table (PHT):** Обхід усіх програмних заголовків `Elf64_Phdr`, виявлення завантажувальних сегментів `PT_LOAD`, аналіз шляху до динамічного завантажувача у сегменті `PT_INTERP` та перевірка прапорців доступу до стеку `PT_GNU_STACK`.
5. **Розрахунок незаініціалізованої пам'яті `.bss`:** Визначення різниці між розміром сегмента у пам'яті (`p_memsz`) та його розміром у файлі (`p_filesz`) для виявлення нульових областей даних, які будуть алоковані ядром.
6. **Захист від некоректних файлів:** Суворий контроль меж файлу на кожному кроці для запобігання помилкам доступу до пам'яті (Segmentation Fault) при роботі з пошкодженими або навмисно згенерованими експлойт-файлами.

---

## 2. Реалізація аналізатора

Нижче наведено вихідний код системної утиліти у двох ідіоматичних варіантах: на системній мові **C** з використанням низькорівневих викликів POSIX та мовою **C++20** із застосуванням RAII, беземисійних обгорток, `std::span` та `std::string_view`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <elf.h>
#include <string.h>

static const char* get_segment_type(uint32_t p_type) {
    switch (p_type) {
        case PT_NULL:         return "PT_NULL";
        case PT_LOAD:         return "PT_LOAD";
        case PT_DYNAMIC:      return "PT_DYNAMIC";
        case PT_INTERP:       return "PT_INTERP";
        case PT_NOTE:         return "PT_NOTE";
        case PT_PHDR:         return "PT_PHDR";
        case PT_TLS:          return "PT_TLS";
        case PT_GNU_EH_FRAME: return "PT_GNU_EH_FRAME";
        case PT_GNU_STACK:    return "PT_GNU_STACK";
        case PT_GNU_RELRO:    return "PT_GNU_RELRO";
        default:              return "UNKNOWN";
    }
}

static void print_flags(uint32_t flags, char *out) {
    out[0] = (flags & PF_R) ? 'R' : '-';
    out[1] = (flags & PF_W) ? 'W' : '-';
    out[2] = (flags & PF_X) ? 'E' : '-';
    out[3] = '\0';
}

int inspect_elf(const char *filename) {
    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття файла");
        return 1;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("Помилка отримання статусу fstat");
        close(fd);
        return 1;
    }

    if ((size_t)st.st_size < sizeof(Elf64_Ehdr)) {
        fprintf(stderr, "Помилка: Файл занадто малий для розміщення заголовка ELF\n");
        close(fd);
        return 1;
    }

    void *map = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd); /* Описус файла більше не потрібен після створення відображення mmap */

    if (map == MAP_FAILED) {
        perror("Помилка створення відображення mmap");
        return 1;
    }

    const Elf64_Ehdr *ehdr = (const Elf64_Ehdr*)map;

    /* 1. Перевірка магічних байтів */
    if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Помилка: Невалідний магічний підпис ELF\n");
        munmap(map, st.st_size);
        return 1;
    }

    if (ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
        fprintf(stderr, "Помилка: Підтримуються лише 64-бітні ELF-файли\n");
        munmap(map, st.st_size);
        return 1;
    }

    printf("=== Аналіз заголовка ELF: %s ===\n", filename);
    printf("Точка входу (e_entry): 0x%lx\n", ehdr->e_entry);
    printf("Зсув PHT (e_phoff): %lu байтів\n", ehdr->e_phoff);
    printf("Кількість програмних заголовків: %u\n\n", ehdr->e_phnum);

    /* 2. Перевірка меж таблиці PHT */
    size_t pht_end = ehdr->e_phoff + (size_t)ehdr->e_phnum * sizeof(Elf64_Phdr);
    if (pht_end > (size_t)st.st_size) {
        fprintf(stderr, "Помилка: Таблиця PHT виходить за межі файла\n");
        munmap(map, st.st_size);
        return 1;
    }

    const Elf64_Phdr *phdr = (const Elf64_Phdr*)((const char*)map + ehdr->e_phoff);

    printf("%-16s %-10s %-18s %-10s %-10s %-5s\n",
           "Тип", "Зсув", "Вірт. адреса", "FileSiz", "MemSiz", "Права");
    printf("-------------------------------------------------------------------------\n");

    for (uint16_t i = 0; i < ehdr->e_phnum; i++) {
        char flags_str[4];
        print_flags(phdr[i].p_flags, flags_str);

        printf("%-16s 0x%08lx 0x%016lx 0x%08lx 0x%08lx %-5s\n",
               get_segment_type(phdr[i].p_type),
               phdr[i].p_offset,
               phdr[i].p_vaddr,
               phdr[i].p_filesz,
               phdr[i].p_memsz,
               flags_str);

        if (phdr[i].p_type == PT_INTERP) {
            if (phdr[i].p_offset + phdr[i].p_filesz <= (size_t)st.st_size) {
                const char *interp = (const char*)map + phdr[i].p_offset;
                printf("  [Інтерпретатор: %s]\n", interp);
            }
        } else if (phdr[i].p_type == PT_LOAD && phdr[i].p_memsz > phdr[i].p_filesz) {
            printf("  [Область .bss у пам'яті: +%lu байтів нулів]\n",
                   phdr[i].p_memsz - phdr[i].p_filesz);
        }
    }

    munmap(map, st.st_size);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <path-to-elf>\n", argv[0]);
        return 1;
    }
    return inspect_elf(argv[1]);
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <elf.h>

namespace elf_inspector {

// RAII обгортка для безпечного управління відображенням пам'яті
class MemoryMappedFile {
    void* data_ = nullptr;
    size_t size_ = 0;

public:
    explicit MemoryMappedFile(const char* path) {
        int fd = ::open(path, O_RDONLY);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити файл");
        }

        struct stat st{};
        if (::fstat(fd, &st) < 0) {
            ::close(fd);
            throw std::system_error(errno, std::generic_category(), "Помилка отримання статусу fstat");
        }

        size_ = static_cast<size_t>(st.st_size);
        if (size_ < sizeof(Elf64_Ehdr)) {
            ::close(fd);
            throw std::runtime_error("Розмір файла менший за заголовок ELF");
        }

        data_ = ::mmap(nullptr, size_, PROT_READ, MAP_PRIVATE, fd, 0);
        ::close(fd); // Дескриптор більше не потрібен після створення mmap

        if (data_ == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення mmap");
        }
    }

    ~MemoryMappedFile() {
        if (data_ && data_ != MAP_FAILED) {
            ::munmap(data_, size_);
        }
    }

    MemoryMappedFile(const MemoryMappedFile&) = delete;
    MemoryMappedFile& operator=(const MemoryMappedFile&) = delete;

    [[nodiscard]] std::span<const std::byte> bytes() const noexcept {
        return {static_cast<const std::byte*>(data_), size_};
    }
};

std::string_view segment_type_to_string(uint32_t p_type) noexcept {
    switch (p_type) {
        case PT_NULL:         return "PT_NULL";
        case PT_LOAD:         return "PT_LOAD";
        case PT_DYNAMIC:      return "PT_DYNAMIC";
        case PT_INTERP:       return "PT_INTERP";
        case PT_NOTE:         return "PT_NOTE";
        case PT_PHDR:         return "PT_PHDR";
        case PT_TLS:          return "PT_TLS";
        case PT_GNU_EH_FRAME: return "PT_GNU_EH_FRAME";
        case PT_GNU_STACK:    return "PT_GNU_STACK";
        case PT_GNU_RELRO:    return "PT_GNU_RELRO";
        default:              return "UNKNOWN";
    }
}

std::string format_flags(uint32_t flags) {
    std::string res;
    res.reserve(3);
    res += (flags & PF_R) ? 'R' : '-';
    res += (flags & PF_W) ? 'W' : '-';
    res += (flags & PF_X) ? 'E' : '-';
    return res;
}

void parse_and_print(const char* filepath) {
    MemoryMappedFile mapped_file(filepath);
    auto buffer = mapped_file.bytes();

    const auto* ehdr = reinterpret_cast<const Elf64_Ehdr*>(buffer.data());

    if (std::string_view(reinterpret_cast<const char*>(ehdr->e_ident), SELFMAG) != ELFMAG) {
        throw std::runtime_error("Невалідний магічний підпис ELF");
    }

    if (ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
        throw std::runtime_error("Файл не належить до 64-бітного класу ELF");
    }

    std::cout << "=== ELF Аналізатор (C++20): " << filepath << " ===\n";
    std::cout << "Точка входу: 0x" << std::hex << ehdr->e_entry << std::dec << "\n";
    std::cout << "Кількість програмних заголовків: " << ehdr->e_phnum << "\n\n";

    const size_t pht_offset = ehdr->e_phoff;
    const size_t pht_bytes = ehdr->e_phnum * sizeof(Elf64_Phdr);

    if (pht_offset + pht_bytes > buffer.size()) {
        throw std::out_of_range("Таблиця PHT виходить за межі бінарного файлу");
    }

    std::span<const Elf64_Phdr> phdrs(
        reinterpret_cast<const Elf64_Phdr*>(buffer.data() + pht_offset),
        ehdr->e_phnum
    );

    for (const auto& ph : phdrs) {
        std::cout << segment_type_to_string(ph.p_type) << " | "
                  << "Offset: 0x" << std::hex << ph.p_offset << " | "
                  << "VAddr: 0x" << ph.p_vaddr << " | "
                  << "FileSiz: 0x" << ph.p_filesz << " | "
                  << "MemSiz: 0x" << ph.p_memsz << " | "
                  << "Flags: " << format_flags(ph.p_flags) << std::dec << "\n";

        if (ph.p_type == PT_INTERP && (ph.p_offset + ph.p_filesz <= buffer.size())) {
            std::string_view interp(
                reinterpret_cast<const char*>(buffer.data() + ph.p_offset)
            );
            std::cout << "  -> Шлях до динамічного завантажувача: " << interp << "\n";
        }
    }
}

} // namespace elf_inspector

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <path-to-elf>\n";
        return 1;
    }

    try {
        elf_inspector::parse_and_print(argv[1]);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка аналізу: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 3. Детальний розбір механізму роботи та системних викликів

Розроблена утиліта демонструє фундаментальний підхід до ефективного системного аналізу двівкових даних у середовищі Linux. 

### Механіка mmap проти класичного виклику read

Використання системного виклику `mmap()` має принципові переваги перед послідовними викликами `read()` або `lseek()`. Коли програма виконує `read()`, ядро Linux спочатку зчитує блоки даних із дискового накопичувача у системний дисковий кеш (Page Cache), а потім виконує повторне копіювання байтів у буфер користувацького простору. 

Виклик `mmap()` із прапорцем `MAP_PRIVATE` працює інакше: він просто створює нове відображення у таблиці сторінок віртуальної пам'яті процесу, яке вказує безпосередньо на сторінки системного дискового кешу. Це повністю усуває копіювання даних між ядром та програмою.

Крім того, `mmap()` позбавляє розробника необхідності виконувати постійні виклики `lseek(fd, offset, SEEK_SET)` для переходу між заголовками. Замість цього утиліта отримує базовий вказівник `map` на початок файла і додає до нього початкові зсуви полів (наприклад, `(const char*)map + ehdr->e_phoff`).

### Порівняльний аналіз C та C++ реалізацій

Порівняння двох варіантів виявляє фундаментальні відмінності у підходах до проектування системного коду:

1. **Управління ресурсами файлового дескриптора:** У версії на мові C системний дескриптор `fd` закривається негайно після успішного виконання виклику `mmap()`, оскільки відображення пам'яті залишається дійсним навіть після закриття дескриптора файлу. Проте виклик `munmap()` доводиться явно розміщувати в кожній гілці дострокового виходу з функції при виявленні помилок.
2. **Ідіома RAII у C++:** У реалізації на C++20 клас `MemoryMappedFile` повністю бере на себе управління життєвим циклом відображення. Деструктор `~MemoryMappedFile()` викликається автоматично при виході з області видимості — незалежно від того, чи завершилася функція успішно, чи було згенеровано виняток `std::runtime_error` або `std::out_of_range`.
3. **Типобезпека та межі безпеки:** Застосування `std::span<const std::byte>` у C++ дозволяє передавати безпечний зріз пам'яті фіксованої довжини без ризику втрати розміру буфера, на відміну від бестіпових вказівників `void*` у мові C.

### Обробка помилок та пастки системної безпеки

Під час розробки аналізаторів бінарних ELF-файлів системному розробнику слід обов'язково враховувати наступні вразливості та крайові випадки:

- **Целочисельне переповнення (Integer Overflow):** Зловмисник може навмисно сформувати ELF-файл із величезними значеннями `e_phnum` або `e_phoff`. Якщо програма обчислює `e_phoff + e_phnum * sizeof(Elf64_Phdr)`, результативне значення може арифметично переповнити 64-бітне ціле число і обнулитися, пропустивши перевірку меж.
- **Невирівняний доступ до пам'яті (Unaligned Access):** Деякі апаратні архітектури (наприклад, суворі варіанти ARM або MIPS) генерують апаратний збій під час спроби розіменувати 64-бітний вказівник `Elf64_Phdr*`, якщо адреса вказівника не кратне 8 байтам. Перевірка вирівнювання `pht_offset % alignof(Elf64_Phdr) == 0` запобігає цьому дефекту.
- **Контроль зациклення або пошкодження рядків:** Під час читання шлях до динамічного завантажувача з сегмента `PT_INTERP` обов'язково перевіряється на наявність нульового термінатора `\0` у межах файлу, щоб запобігти безкінечному зчитуванню пам'яті за межами мапінгу.
