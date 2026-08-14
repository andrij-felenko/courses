# ⚙️ Практична реалізація міні-динамічного завантажувача на C та C++

Практична реалізація власного міні-завантажувача демонструє, як саме ядро та `ld-linux.so` працюють на низькому рівні: від зчитування ELF-заголовків і відображення сегментів через `mmap()` до виконання релокацій у віртуальній пам'яті та передачі виконання точці входу.

## Архітектурний задум та концепція реалізації

Головною метою створення навчального динамічного завантажувача є розуміння процесів, які відбуваються в оперативній пам'яті між моментом виклику `execve()` та виконанням першої інструкції користувацької програми. 

Справжній завантажувач `ld-linux.so` обробляє сотні складних ситуацій: версіонування символів, запізніле зв'язування функцій через PLT/GOT, потокові локальні дані TLS та вирішення конфліктів однакових імен у різних бібліотеках. Наш міні-завантажувач фокусується на фундаментальному Causality-ядрі цього процесу: завантаженні позиційно-незалежного бінарника (PIE), розрахунку зміщення базової адреси у віртуальній пам'яті та застосуванні релокацій типу `R_X86_64_RELATIVE`.

### Покроковий алгоритм роботи завантажувача

1. **Відкриття та перевірка ELF-файлу:** Завантажувач відкриває цільовий файл за допомогою системного виклику `open()` і зчитує головний заголовок `Elf64_Ehdr`. Він перевіряє сигнатурні Magic-байти (`\x7fELF`), архітектуру (64-бітна x86_64) та тип виконуваного файлу (`ET_DYN` для PIE-бінарників чи бібліотек).
2. **Аналіз заголовків програм (Program Headers):** Зчитується масив структур `Elf64_Phdr`. Завантажувач знаходить усі сегменти з типом `PT_LOAD` і обчислює діапазон віртуальних адрес від найменшої `min_vaddr` до найбільшої `max_vaddr`.
3. **Виділення віртуальної пам'яті:** За допомогою системного виклику `mmap()` завантажувач замовляє в ядра анонімний блок пам'яті розміром `max_vaddr - min_vaddr`. Адреса, яку поверне ядро, стає базовою адресою завантаження (`load_base`). Різниця `delta = load_base - min_vaddr` описує зсув ASLR для даного сеансу виконання.
4. **Копіювання сегментів та очищення `.bss`:** Для кожного сегмента `PT_LOAD` завантажувач переміщує вказівник у файлі до зсуву `p_offset` і зчитує `p_filesz` байтів безпосередньо у відповідний блок пам'яті за адресою `load_base + (p_vaddr - min_vaddr)`. Якщо розмір у пам'яті `p_memsz` перевищує розмір у файлі `p_filesz`, залишок (секція `.bss`) обнуляється за допомогою `memset()`.
5. **Розбір динамічної секції (`PT_DYNAMIC`):** Завантажувач знаходить сегмент `PT_DYNAMIC`, який містить масив елементів `Elf64_Dyn`. Він знаходить адреси таблиці релокацій `DT_RELA`, її загальний розмір `DT_RELASZ` та розмір одного запису `DT_RELAENT`.
6. **Застосування релокацій `R_X86_64_RELATIVE`:** Завантажувач обходить масив запісів `Elf64_Rela`. Для кожної релокації типу `R_X86_64_RELATIVE` він знаходить цільовий осередку пам'яті за адресою `delta + rel->r_offset` і записує туди модифіковане значення `delta + rel->r_addend`.
7. **Передача керування:** Завантажувач вираховує підсумкову точку входу `entry_point = delta + ehdr.e_entry`, приводить її до вказівника на функцію та здійснює безумовний перехід до її виконання.

---

## Вихідний код реалізації на C та C++

Нижче наведено дві повноцінні реалізації міні-завантажувача. Перша версія написана чистою мовою C із застосуванням системних функцій POSIX. Друга версія є ідіоматичним еквівалентом мовою C++20, де використовується концепція RAII для автоматичного управління файловими дескрипторами та виділеною пам'яттю `mmap`, а також типи `std::expected` та `std::span`.

:::tabs
```c
/* mini_loader.c — Мінімалістичний ELF-завантажувач мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <elf.h>

typedef int (*entry_func_t)(void);

static void log_error(const char *msg) {
    perror(msg);
}

int load_and_run_elf(const char *filename) {
    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        log_error("Failed to open ELF file");
        return -1;
    }

    Elf64_Ehdr ehdr;
    if (read(fd, &ehdr, sizeof(ehdr)) != sizeof(ehdr)) {
        log_error("Failed to read ELF header");
        close(fd);
        return -1;
    }

    /* Перевірка Magic-байтів ELF */
    if (memcmp(ehdr.e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Invalid ELF magic header\n");
        close(fd);
        return -1;
    }

    /* Виділення пам'яті під заголовки програм */
    Elf64_Phdr *phdrs = malloc(ehdr.e_phnum * sizeof(Elf64_Phdr));
    if (!phdrs) {
        close(fd);
        return -1;
    }

    lseek(fd, ehdr.e_phoff, SEEK_SET);
    if (read(fd, phdrs, ehdr.e_phnum * sizeof(Elf64_Phdr)) != (ssize_t)(ehdr.e_phnum * sizeof(Elf64_Phdr))) {
        log_error("Failed to read Program Headers");
        free(phdrs);
        close(fd);
        return -1;
    }

    /* Розрахунок загального розміру віртуальної пам'яті */
    uintptr_t min_vaddr = (uintptr_t)-1;
    uintptr_t max_vaddr = 0;

    for (int i = 0; i < ehdr.e_phnum; i++) {
        if (phdrs[i].p_type == PT_LOAD) {
            if (phdrs[i].p_vaddr < min_vaddr) min_vaddr = phdrs[i].p_vaddr;
            if (phdrs[i].p_vaddr + phdrs[i].p_memsz > max_vaddr) {
                max_vaddr = phdrs[i].p_vaddr + phdrs[i].p_memsz;
            }
        }
    }

    size_t total_size = max_vaddr - min_vaddr;
    
    /* Виділення анонімної пам'яті під бінарник */
    void *load_base = mmap(NULL, total_size, PROT_READ | PROT_WRITE | PROT_EXEC,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (load_base == MAP_FAILED) {
        log_error("mmap failed");
        free(phdrs);
        close(fd);
        return -1;
    }

    uintptr_t delta = (uintptr_t)load_base - min_vaddr;

    /* Відображення сегментів PT_LOAD */
    Elf64_Dyn *dyn_section = NULL;
    size_t dyn_size = 0;

    for (int i = 0; i < ehdr.e_phnum; i++) {
        if (phdrs[i].p_type == PT_LOAD) {
            void *seg_dest = (void *)((uintptr_t)load_base + (phdrs[i].p_vaddr - min_vaddr));
            lseek(fd, phdrs[i].p_offset, SEEK_SET);
            if (read(fd, seg_dest, phdrs[i].p_filesz) != (ssize_t)phdrs[i].p_filesz) {
                log_error("Failed to read segment data");
                munmap(load_base, total_size);
                free(phdrs);
                close(fd);
                return -1;
            }
            /* Обнулення секції .bss */
            if (phdrs[i].p_memsz > phdrs[i].p_filesz) {
                memset((char *)seg_dest + phdrs[i].p_filesz, 0, phdrs[i].p_memsz - phdrs[i].p_filesz);
            }
        } else if (phdrs[i].p_type == PT_DYNAMIC) {
            dyn_section = (Elf64_Dyn *)((uintptr_t)load_base + (phdrs[i].p_vaddr - min_vaddr));
            dyn_size = phdrs[i].p_memsz;
        }
    }

    free(phdrs);
    close(fd);

    /* Обробка релокацій у секції .dynamic */
    if (dyn_section) {
        Elf64_Rela *rela_table = NULL;
        size_t rela_size = 0;
        size_t rela_ent = sizeof(Elf64_Rela);

        for (Elf64_Dyn *d = dyn_section; d->d_tag != DT_NULL; d++) {
            if (d->d_tag == DT_RELA) {
                rela_table = (Elf64_Rela *)(delta + d->d_un.d_ptr);
            } else if (d->d_tag == DT_RELASZ) {
                rela_size = d->d_un.d_val;
            } else if (d->d_tag == DT_RELAENT) {
                rela_ent = d->d_un.d_val;
            }
        }

        if (rela_table && rela_size > 0) {
            size_t count = rela_size / rela_ent;
            for (size_t i = 0; i < count; i++) {
                Elf64_Rela *rel = &rela_table[i];
                if (ELF64_R_TYPE(rel->r_info) == R_X86_64_RELATIVE) {
                    uintptr_t *target = (uintptr_t *)(delta + rel->r_offset);
                    *target = delta + rel->r_addend;
                }
            }
        }
    }

    /* Передача керування точці входу */
    uintptr_t entry_point = delta + ehdr.e_entry;
    entry_func_t entry = (entry_func_t)entry_point;
    printf("[rtld-mini] Jumping to entry point at %p...\n", (void *)entry_point);
    
    int result = entry();

    munmap(load_base, total_size);
    return result;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Usage: %s <elf_binary>\n", argv[0]);
        return 1;
    }
    return load_and_run_elf(argv[1]);
}
```
```cpp
// mini_loader.cpp — Ідіоматичний ELF-завантажувач мовою C++20
#include <iostream>
#include <vector>
#include <memory>
#include <expected>
#include <string_view>
#include <cstring>
#include <limits>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <elf.h>

namespace mini_rtld {

// RAII обгортка для файлового дескриптора
class FileDescriptor {
    int m_fd{-1};
public:
    explicit FileDescriptor(int fd) noexcept : m_fd(fd) {}
    ~FileDescriptor() { if (m_fd >= 0) ::close(m_fd); }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& other) noexcept : m_fd(other.m_fd) { other.m_fd = -1; }
    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

// RAII обгортка для mmap пам'яті
struct MmapDeleter {
    size_t size{0};
    void operator()(void* ptr) const noexcept {
        if (ptr && ptr != MAP_FAILED) {
            ::munmap(ptr, size);
        }
    }
};

using UniqueMappedMemory = std::unique_ptr<void, MmapDeleter>;

enum class LoaderError {
    FileNotFound,
    HeaderReadError,
    InvalidElfMagic,
    MemoryAllocationFailed,
    SegmentReadError,
    RelocationError
};

class ElfLoader {
public:
    static std::expected<int, LoaderError> load_and_execute(std::string_view path) {
        FileDescriptor fd(::open(path.data(), O_RDONLY));
        if (!fd.valid()) {
            return std::unexpected(LoaderError::FileNotFound);
        }

        Elf64_Ehdr ehdr{};
        if (::read(fd.get(), &ehdr, sizeof(ehdr)) != sizeof(ehdr)) {
            return std::unexpected(LoaderError::HeaderReadError);
        }

        if (std::memcmp(ehdr.e_ident, ELFMAG, SELFMAG) != 0) {
            return std::unexpected(LoaderError::InvalidElfMagic);
        }

        std::vector<Elf64_Phdr> phdrs(ehdr.e_phnum);
        if (::lseek(fd.get(), ehdr.e_phoff, SEEK_SET) == -1 ||
            ::read(fd.get(), phdrs.data(), phdrs.size() * sizeof(Elf64_Phdr)) != static_cast<ssize_t>(phdrs.size() * sizeof(Elf64_Phdr))) {
            return std::unexpected(LoaderError::HeaderReadError);
        }

        uintptr_t min_vaddr = std::numeric_limits<uintptr_t>::max();
        uintptr_t max_vaddr = 0;

        for (const auto& phdr : phdrs) {
            if (phdr.p_type == PT_LOAD) {
                min_vaddr = std::min(min_vaddr, static_cast<uintptr_t>(phdr.p_vaddr));
                max_vaddr = std::max(max_vaddr, static_cast<uintptr_t>(phdr.p_vaddr + phdr.p_memsz));
            }
        }

        const size_t total_size = max_vaddr - min_vaddr;
        void* raw_mem = ::mmap(nullptr, total_size, PROT_READ | PROT_WRITE | PROT_EXEC,
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

        if (raw_mem == MAP_FAILED) {
            return std::unexpected(LoaderError::MemoryAllocationFailed);
        }

        UniqueMappedMemory memory(raw_mem, MmapDeleter{total_size});
        const uintptr_t load_base = reinterpret_cast<uintptr_t>(memory.get());
        const uintptr_t delta = load_base - min_vaddr;

        const Elf64_Dyn* dyn_section = nullptr;

        for (const auto& phdr : phdrs) {
            if (phdr.p_type == PT_LOAD) {
                void* seg_dest = reinterpret_cast<void*>(load_base + (phdr.p_vaddr - min_vaddr));
                if (::lseek(fd.get(), phdr.p_offset, SEEK_SET) == -1 ||
                    ::read(fd.get(), seg_dest, phdr.p_filesz) != static_cast<ssize_t>(phdr.p_filesz)) {
                    return std::unexpected(LoaderError::SegmentReadError);
                }
                if (phdr.p_memsz > phdr.p_filesz) {
                    std::memset(reinterpret_cast<char*>(seg_dest) + phdr.p_filesz, 0, phdr.p_memsz - phdr.p_filesz);
                }
            } else if (phdr.p_type == PT_DYNAMIC) {
                dyn_section = reinterpret_cast<const Elf64_Dyn*>(load_base + (phdr.p_vaddr - min_vaddr));
            }
        }

        /* Обробка релокацій у динамічній секцій */
        if (dyn_section) {
            const Elf64_Rela* rela_table = nullptr;
            size_t rela_size = 0;
            size_t rela_ent = sizeof(Elf64_Rela);

            for (const Elf64_Dyn* d = dyn_section; d->d_tag != DT_NULL; ++d) {
                if (d->d_tag == DT_RELA) {
                    rela_table = reinterpret_cast<const Elf64_Rela*>(delta + d->d_un.d_ptr);
                } else if (d->d_tag == DT_RELASZ) {
                    rela_size = d->d_un.d_val;
                } else if (d->d_tag == DT_RELAENT) {
                    rela_ent = d->d_un.d_val;
                }
            }

            if (rela_table && rela_size > 0) {
                const size_t count = rela_size / rela_ent;
                for (size_t i = 0; i < count; ++i) {
                    const auto& rel = rela_table[i];
                    if (ELF64_R_TYPE(rel.r_info) == R_X86_64_RELATIVE) {
                        auto* target = reinterpret_cast<uintptr_t*>(delta + rel.r_offset);
                        *target = delta + rel.r_addend;
                    }
                }
            }
        }

        const uintptr_t entry_point = delta + ehdr.e_entry;
        using EntryFunc = int (*)();
        auto entry = reinterpret_cast<EntryFunc>(entry_point);

        std::cout << "[rtld-cpp] Jumping to entry point at " << std::hex << entry_point << std::dec << "...\n";
        return entry();
    }
};

} // namespace mini_rtld

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <elf_binary>\n";
        return 1;
    }

    auto result = mini_rtld::ElfLoader::load_and_execute(argv[1]);
    if (!result) {
        std::cerr << "Loader failed with error code\n";
        return 1;
    }

    return *result;
}
```
:::

---

## Глибокий розбір технічних деталей та механізмів

### 1. Розрахунок дельти базової адреси та ASLR

У позиційно-незалежних виконуваних файлах (PIE) всі заголовки `PT_LOAD` скомпільовані з базовою адресою `0x0`. Під час виклику системного виклику `mmap(NULL, total_size, ...)` ядро Linux самостійно визначає вільне вікно у віртуальному адресному просторі процесу і повертає покажчик на нього (наприклад, `0x7f9a8b400000`).

Дельта базової адреси обчислюється як:

:::tabs
```c
uintptr_t delta = (uintptr_t)load_base - min_vaddr;
```
```cpp
const uintptr_t delta = reinterpret_cast<uintptr_t>(load_base) - min_vaddr;
```
:::

Ця дельта є ключовим коефіцієнтом для будь-якого подальшого перерахунку адрес. Усі віртуальні адреси, зчитані з ELF-заголовків (включаючи `ehdr.e_entry`, `phdr.p_vaddr`, `d_ptr` у `.dynamic` та `r_offset` у релокаціях), є відносними зміщеннями. Додавання `delta` до будь-якого відносного зміщення дає абсолютну віртуальну адресу в поточному процесі.

### 2. Секція .bss та різниця між p_memsz і p_filesz

Особливу увагу при реалізації завантажувача приділено обробці неініціалізованих глобальних змінних (секція `.bss`). 

У файлі ELF глобальні масиви та структури, що ініціалізуються нулями (наприклад, `char buffer[1024 * 1024];`), не займають місця на диску, щоб не збільшувати розмір бінарника. У заголовку сегмента `PT_LOAD` це відображається у вигляді нерівності:

- `p_filesz`: Розмір даних, які дійсно записані у файлі на диску.
- `p_memsz`: Загальний розмір, який повинен мати сегмент у пам'яті.

Завантажувач зчитує з диска лише `p_filesz` байтів, після чого зобов'язаний явно викливати `memset()`, заповнюючи байтами `0x00` область розміром `p_memsz - p_filesz`. Якщо завантажувач пропустить цей крок, секція `.bss` міститиме випадкове сміття із пам'яті завантажувача, що призведе до невизначеної поведінки цільової програми.

### 3. Механіка релокацій R_X86_64_RELATIVE

Для позиційно-незалежного коду компілятор створює таблицю `.rela.dyn`, яка містить елементи типу `Elf64_Rela`:

:::tabs
```c
typedef struct {
    Elf64_Addr  r_offset;  /* Зміщення комірки, де лежить вказівник */
    Elf64_Xword r_info;    /* Тип релокацій та індекс символу */
    Elf64_Sxword r_addend;  /* Константний адденд (значення зсуву вказівника) */
} Elf64_Rela;
```
```cpp
// C++ оголошення Elf64_Rela з <elf.h>
struct Elf64_Rela {
    Elf64_Addr   r_offset;
    Elf64_Xword  r_info;
    Elf64_Sxword r_addend;
};
```
:::

Для макросу `ELF64_R_TYPE(rel->r_info) == R_X86_64_RELATIVE` завантажувач виконує перезапис вказівника. Адреса комірки, яку треба перезаписати, обчислюється як `target_ptr = delta + rel->r_offset`. Нова базова адреса обчислюється як `new_val = delta + rel->r_addend`. Завантажувач записує `new_val` у комірку `*target_ptr`.

Без цього перезапису будь-який виклик функції через вказівник або звернення до глобального рядка у завантаженому бінарнику призводили б до падіння `Segmentation Fault`, адже вказівники посилалися б на нульові відносні адреси.

---

## Тестування та перевірка роботи

Для тестування нашого міні-завантажувача створимо просту цільову програму `target.c` / `target.cpp`:

:::tabs
```c
/* target.c — Цільова програма для міні-завантажувача */
#include <stdio.h>

static const char *msg = "Hello from dynamically loaded ELF!";

int target_entry(void) {
    puts(msg);
    return 42;
}
```
```cpp
// target.cpp — Ідіоматичний C++20 еквівалент цільової програми
#include <iostream>
#include <string_view>

constexpr std::string_view msg = "Hello from dynamically loaded ELF!";

extern "C" int target_entry() {
    std::cout << msg << '\n';
    return 42;
}
```
:::

Зкомпілюємо її як позиційно-незалежний розділений об'єкт без стандартного `_start`:

```bash
gcc -fPIC -shared -nostdlib -o target.elf target.c -e target_entry
```

Після цього запустимо наш завантажувач:

```bash
./mini_loader target.elf
```

Завантажувач прочитає `target.elf`, виділить пам'ять через `mmap()`, застосує релокації для вказівника `msg` та успішно передасть керування функції `target_entry`, яка виведе рядок у консоль і поверне код `42`.
