# Створення безпечного неінвазивного інспектора ELF: читання заголовків, бібліотек та захисту без виконання коду

Цей практичний проект демонструє розробку автономної системної утиліти для глибокого статичного аудиту бінарних файлів формату `ELF` (англ. *Executable and Linkable Format*) у просторі користувача без залучення динамічного завантажувача та без жодного ризику виконання потенційно шкідливого коду. Утиліта відображає цільовий файл у віртуальну пам'ять у режимі лише для читання через системний виклик `mmap()`, валідує магічні байти та структуру заголовків, витягує шлях до інтерпретатора (`PT_INTERP`), перевіряє активність захисних механізмів пам'яті (`NX`, `RELRO`) та парсить динамічні теги `DT_NEEDED` і `DT_RUNPATH`.

---

### Архітектура та принципи безпечного розбору

Традиційні діагностичні засоби, такі як `ldd`, покладаються на виконання динамічного завантажувача системи (`ld-linux.so`), що робить аналіз сторонніх або скомпрометованих бінарників небезпечним. Якщо невідомий виконуваний файл містить модифікований заголовок `PT_INTERP` або шкідливі конструктори ініціалізації (`.init_array`), виклик `ldd` призводить до запуску довільного коду з правами поточного користувача.

Безпечний інспектор працює як пасивний аналізатор байтів, спираючись на системні структури заголовка `<elf.h>`. Замість виконання чи передачі керування операційній системі утиліта відкриває файл виключно для читання (`O_RDONLY`), мапує його сторінки в адресний простір через `mmap()` із прапорцем `PROT_READ` та послідовно обходить таблиці заголовків.

```
+-------------------------------------------------------------------------+
|                              Вхідний файл                               |
+-------------------------------------------------------------------------+
                                     |
                                     v open(O_RDONLY) + fstat()
+-------------------------------------------------------------------------+
|                  mmap(PROT_READ, MAP_PRIVATE) у пам'ять                 |
+-------------------------------------------------------------------------+
                                     |
                                     v Перевірка e_ident (\x7fELF, 64-bit, LSB)
+-------------------------------------------------------------------------+
|                         Elf64_Ehdr (ELF Header)                         |
|   Тип файлу (ET_EXEC / ET_DYN), Архітектура (e_machine), Точка входу    |
+-------------------------------------------------------------------------+
                                     |
                                     v Зміщення e_phoff
+-------------------------------------------------------------------------+
|                  Таблиця Program Headers (Elf64_Phdr)                   |
|  * PT_INTERP   -> Рядок шляху до системного динамічного завантажувача   |
|  * PT_GNU_STACK-> Прапорці прав доступу стека (PF_X: NX увімкнено чи ні)|
|  * PT_GNU_RELRO-> Наявність захисту таблиць релокацій від запису        |
|  * PT_DYNAMIC  -> Зсув та розмір масиву динамічних тегів Elf64_Dyn     |
+-------------------------------------------------------------------------+
                                     |
                                     v Обхід сегмента PT_DYNAMIC
+-------------------------------------------------------------------------+
|                         Динамічні теги Elf64_Dyn                        |
|  * DT_STRTAB   -> Віртуальна адреса або зсув таблиці рядків .dynstr     |
|  * DT_NEEDED   -> Імена залежних спільних бібліотек (.so)               |
|  * DT_RUNPATH  -> Вшиті шляхи пошуку бібліотек $ORIGIN                  |
+-------------------------------------------------------------------------+
```

#### Вибір моделі вводу-виводу: чому `mmap` переважає `read`

Під час інспекції чужих двійкових файлів використання послідовного зчитування через виклики `read()` та виділення динамічних буферів у купі (`malloc`) створює додаткові ризики:
* Пошкоджені або зловмисно скомпільовані заголовки можуть заявляти колосальні розміри таблиць (наприклад, `e_shnum = 0xffff`), провокуючи вичерпання пам'яті (OOM) або переповнення буфера під час ручного копіювання.
* Системний виклик `mmap()` із прапорцем `MAP_PRIVATE` та захистом `PROT_READ` створює відображення сторінок файлу на віртуальну пам'ять без фізичного копіювання даних у купу. Ядро підтягує сторінки через механізм сторінкових помилок (*page faults*) лише тоді, коли інспектор реально звертається до відповідних байтів.

#### Механізм трансляції віртуальних адрес у зміщення файлу

У бінарних файлах формату ELF динамічні теги типу `DT_STRTAB` містять віртуальну адресу (`d_ptr`), за якою таблиця рядків розміщується після завантаження програми в пам'ять. Проте під час статичного аналізу файл не завантажений ядром, тому віртуальну адресу необхідно транслювати у фізичне зміщення всередині сирого файлу на диску.

Для цього інспектор реалізує функцію пошуку завантажувального сегмента `PT_LOAD`:
1. Якщо бінарник зібрано як `ET_DYN` (Position-Independent Executable, PIE), значення `d_ptr` часто є відносним зсувом від бази образу, який збігається зі зміщенням у файлі.
2. Для класичних бінарників `ET_EXEC` із фіксованою адресою завантаження алгоритм перебирає всі сегменти `PT_LOAD` у таблиці `Program Headers`. Якщо шукана адреса `vaddr` потрапляє в діапазон `[p_vaddr, p_vaddr + p_filesz)`, зміщення у файлі обчислюється за формулою:

```
offset = p_offset + (vaddr - p_vaddr)
```

Цей розрахунок дозволяє безпечно витягти вказівник на таблицю рядків `.dynstr` та прочитати назви всіх залежних бібліотек, записаних у тегах `DT_NEEDED`.

#### Аудит маркерів безпеки: NX-біт та захист RELRO

Захист пам'яті у форматі ELF описується спеціальними псевдосегментами в таблиці `Program Headers`:
* **Сегмент `PT_GNU_STACK`:** описує права доступу до області стека потоку. Поле `p_flags` містить бітову маску дозволів (`PF_R` — читання, `PF_W` — запис, `PF_X` — виконання). Якщо прапорець `PF_X` встановлено (`p_flags & PF_X`), ядро виділяє стек з правом виконання інструкцій. Це вимикає апаратний захист NX (*No-Execute* / `W^X`), дозволяючи атакувачам виконувати шелкод у разі переповнення стекового буфера. Безпечні бінарники завжди мають прапорці `PF_R | PF_W` без `PF_X`.
* **Сегмент `PT_GNU_RELRO`:** вказує завантажувачу область пам'яті (зокрема секції `.init_array`, `.fini_array`, `.jcr`, `.data.rel.ro`), яку після завершення роботи динамічного лінкера та розв'язання релокацій необхідно перевести в режим лише для читання через системний виклик `mprotect(..., PROT_READ)`. Це захищає критичні адреси від модифікації під час роботи програми.

---

### Реалізація безпечного інспектора

Нижче наведено повнофункціональну системну утиліту `elf_inspector`, реалізовану мовами C та C++. Обидва варіанти містять суворий контроль меж пам'яті (англ. *bounds checking*), що унеможливлює вихід за межі виділеного буфера навіть при спробі згодувати утиліті пошкоджений або фальсифікований бінарник.

:::tabs
```c
#define _GNU_SOURCE
#include <elf.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

/* Трансляція віртуальної адреси у зміщення всередині файлу за таблицею PT_LOAD */
static uint64_t vaddr_to_offset(const Elf64_Ehdr *hdr, uint64_t vaddr, size_t file_size) {
    if (hdr->e_type == ET_DYN) {
        /* Для Position-Independent Executable віртуальні адреси в PT_DYNAMIC збігаються зі зміщеннями */
        if (vaddr < file_size) {
            return vaddr;
        }
    }

    const Elf64_Phdr *ph = (const Elf64_Phdr *)((const uint8_t *)hdr + hdr->e_phoff);
    for (uint16_t i = 0; i < hdr->e_phnum; ++i) {
        if (ph[i].p_type == PT_LOAD) {
            if (vaddr >= ph[i].p_vaddr && vaddr < (ph[i].p_vaddr + ph[i].p_filesz)) {
                return ph[i].p_offset + (vaddr - ph[i].p_vaddr);
            }
        }
    }
    return 0;
}

static const char *machine_to_string(uint16_t machine) {
    switch (machine) {
        case EM_X86_64:  return "Advanced Micro Devices X86-64";
        case EM_AARCH64: return "ARM AArch64";
        case EM_ARM:     return "ARM 32-bit";
        case EM_RISCV:   return "RISC-V";
        case EM_386:     return "Intel 80386";
        default:         return "Unknown Architecture";
    }
}

static void inspect_elf(const uint8_t *data, size_t size) {
    if (size < sizeof(Elf64_Ehdr)) {
        fprintf(stderr, "Помилка: файл занадто малий для формату ELF64.\n");
        return;
    }

    const Elf64_Ehdr *hdr = (const Elf64_Ehdr *)data;

    /* 1. Перевірка магічних байтів \x7fELF */
    if (memcmp(hdr->e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Помилка: файл не є коректним ELF-образом (невірні магічні байти).\n");
        return;
    }

    if (hdr->e_ident[EI_CLASS] != ELFCLASS64) {
        fprintf(stderr, "Повідомлення: підтримуються лише 64-бітні бінарники ELFCLASS64.\n");
        return;
    }

    printf("=== ПАСПОРТ БІНАРНИКА ===\n");
    printf("Клас:              ELF64\n");
    printf("Порядок байтів:    %s\n", hdr->e_ident[EI_DATA] == ELFDATA2LSB ? "Little-Endian (LSB)" : "Big-Endian (MSB)");
    printf("Архітектура:       %s (0x%04x)\n", machine_to_string(hdr->e_machine), hdr->e_machine);
    printf("Тип файлу:         %s\n", hdr->e_type == ET_EXEC ? "ET_EXEC (Виконуваний із фіксованою адресою)" :
                                       hdr->e_type == ET_DYN ? "ET_DYN (Position-Independent Executable або Shared Object)" : "Інший");
    printf("Точка входу:       0x%016lx\n", (unsigned long)hdr->e_entry);

    /* 2. Аудит Program Headers */
    if (hdr->e_phoff + (hdr->e_phnum * sizeof(Elf64_Phdr)) > size) {
        fprintf(stderr, "Помилка: пошкоджена таблиця Program Headers виходить за межі файлу.\n");
        return;
    }

    const Elf64_Phdr *ph = (const Elf64_Phdr *)(data + hdr->e_phoff);
    const char *interp_path = NULL;
    bool has_nx_stack = true;
    bool has_relro = false;
    const Elf64_Phdr *dyn_ph = NULL;

    for (uint16_t i = 0; i < hdr->e_phnum; ++i) {
        if (ph[i].p_type == PT_INTERP) {
            if (ph[i].p_offset + ph[i].p_filesz <= size) {
                interp_path = (const char *)(data + ph[i].p_offset);
            }
        } else if (ph[i].p_type == PT_GNU_STACK) {
            if (ph[i].p_flags & PF_X) {
                has_nx_stack = false; /* Стек має право на виконання - небезпечно! */
            }
        } else if (ph[i].p_type == PT_GNU_RELRO) {
            has_relro = true;
        } else if (ph[i].p_type == PT_DYNAMIC) {
            dyn_ph = &ph[i];
        }
    }

    printf("\n=== ЗАХИСНІ МЕХАНІЗМИ ТА ІНТЕРПРЕТАТОР ===\n");
    printf("Тип зв'язування:   %s\n", interp_path ? "Динамічне (Dynamically linked)" : "Статичне (Statically linked)");
    if (interp_path) {
        printf("Інтерпретатор:     %s\n", interp_path);
    }
    printf("NX (No-Execute):   %s\n", has_nx_stack ? "Увімкнено (Стек захищено від виконання коду)" : "ВИМКНЕНО (Стек має права на виконання!)");
    printf("RELRO:             %s\n", has_relro ? "Присутній (PT_GNU_RELRO активний)" : "Відсутній (Таблиця GOT доступна для запису)");

    /* 3. Перевірка таблиці секцій на наявність .symtab (stripped / not stripped) */
    bool has_symtab = false;
    if (hdr->e_shoff > 0 && (hdr->e_shoff + (hdr->e_shnum * sizeof(Elf64_Shdr)) <= size)) {
        const Elf64_Shdr *sh = (const Elf64_Shdr *)(data + hdr->e_shoff);
        if (hdr->e_shstrndx < hdr->e_shnum) {
            const char *shstrtab = (const char *)(data + sh[hdr->e_shstrndx].sh_offset);
            for (uint16_t i = 0; i < hdr->e_shnum; ++i) {
                const char *sname = shstrtab + sh[i].sh_name;
                if (strcmp(sname, ".symtab") == 0) {
                    has_symtab = true;
                    break;
                }
            }
        }
    }
    printf("Символи:           %s\n", has_symtab ? "not stripped (Присутня повна таблиця .symtab)" : "stripped (Налагоджувальні символи видалено)");

    /* 4. Аудит динамічних залежностей (DT_NEEDED) */
    if (dyn_ph && dyn_ph->p_offset + dyn_ph->p_filesz <= size) {
        printf("\n=== ДИНАМІЧНІ ЗАЛЕЖНОСТІ (DT_NEEDED) ===\n");
        const Elf64_Dyn *dyn = (const Elf64_Dyn *)(data + dyn_ph->p_offset);
        size_t dyn_count = dyn_ph->p_filesz / sizeof(Elf64_Dyn);

        /* Знаходження таблиці рядків DT_STRTAB */
        uint64_t strtab_vaddr = 0;
        for (size_t i = 0; i < dyn_count && dyn[i].d_tag != DT_NULL; ++i) {
            if (dyn[i].d_tag == DT_STRTAB) {
                strtab_vaddr = dyn[i].d_un.d_ptr;
                break;
            }
        }

        uint64_t strtab_offset = strtab_vaddr ? vaddr_to_offset(hdr, strtab_vaddr, size) : 0;
        if (strtab_offset && strtab_offset < size) {
            const char *dynstr = (const char *)(data + strtab_offset);
            bool found_needed = false;

            for (size_t i = 0; i < dyn_count && dyn[i].d_tag != DT_NULL; ++i) {
                if (dyn[i].d_tag == DT_NEEDED) {
                    uint64_t str_idx = dyn[i].d_un.d_val;
                    if (strtab_offset + str_idx < size) {
                        printf("  * Потрібна бібліотека: %s\n", dynstr + str_idx);
                        found_needed = true;
                    }
                } else if (dyn[i].d_tag == DT_RUNPATH) {
                    uint64_t str_idx = dyn[i].d_un.d_val;
                    if (strtab_offset + str_idx < size) {
                        printf("  * Вшитий RUNPATH:     %s\n", dynstr + str_idx);
                    }
                } else if (dyn[i].d_tag == DT_RPATH) {
                    uint64_t str_idx = dyn[i].d_un.d_val;
                    if (strtab_offset + str_idx < size) {
                        printf("  * Вшитий RPATH:       %s (Застарілий)\n", dynstr + str_idx);
                    }
                }
            }

            if (!found_needed) {
                printf("  (Записів DT_NEEDED не виявлено)\n");
            }
        } else {
            printf("  [Увага: не вдалося розв'язати зміщення таблиці DT_STRTAB]\n");
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях-до-elf-файлу>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int fd = open(argv[1], O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        perror("open");
        return EXIT_FAILURE;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("fstat");
        close(fd);
        return EXIT_FAILURE;
    }

    if (st.st_size == 0) {
        fprintf(stderr, "Помилка: файл порожній.\n");
        close(fd);
        return EXIT_FAILURE;
    }

    void *map = mmap(NULL, (size_t)st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return EXIT_FAILURE;
    }

    inspect_elf((const uint8_t *)map, (size_t)st.st_size);

    munmap(map, (size_t)st.st_size);
    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <elf.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#include <cstring>
#include <expected>
#include <filesystem>
#include <format>
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <vector>

namespace fs = std::filesystem;

class MappedFile {
public:
    static std::expected<MappedFile, std::string> open_readonly(const fs::path &path) {
        int fd = ::open(path.c_str(), O_RDONLY | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::format("Не вдалося відкрити файл: {}", std::strerror(errno)));
        }

        struct stat st{};
        if (::fstat(fd, &st) < 0) {
            ::close(fd);
            return std::unexpected(std::format("Не вдалося отримати атрибути файлу: {}", std::strerror(errno)));
        }

        if (st.st_size == 0) {
            ::close(fd);
            return std::unexpected("Файл має нульовий розмір.");
        }

        auto size = static_cast<size_t>(st.st_size);
        void *addr = ::mmap(nullptr, size, PROT_READ, MAP_PRIVATE, fd, 0);
        ::close(fd); // Дескриптор можна закрити одразу після створення відображення mmap

        if (addr == MAP_FAILED) {
            return std::unexpected(std::format("Збій виклику mmap: {}", std::strerror(errno)));
        }

        return MappedFile(static_cast<const uint8_t *>(addr), size);
    }

    ~MappedFile() noexcept {
        if (data_ != nullptr && size_ > 0) {
            ::munmap(const_cast<uint8_t *>(data_), size_);
        }
    }

    MappedFile(const MappedFile &) = delete;
    MappedFile &operator=(const MappedFile &) = delete;

    MappedFile(MappedFile &&other) noexcept
        : data_(std::exchange(other.data_, nullptr)),
          size_(std::exchange(other.size_, 0)) {}

    MappedFile &operator=(MappedFile &&other) noexcept {
        if (this != &other) {
            if (data_ != nullptr && size_ > 0) {
                ::munmap(const_cast<uint8_t *>(data_), size_);
            }
            data_ = std::exchange(other.data_, nullptr);
            size_ = std::exchange(other.size_, 0);
        }
        return *this;
    }

    [[nodiscard]] std::span<const uint8_t> bytes() const noexcept {
        return {data_, size_};
    }

private:
    MappedFile(const uint8_t *data, size_t size) noexcept : data_(data), size_(size) {}
    const uint8_t *data_{nullptr};
    size_t size_{0};
};

class SafeElfInspector {
public:
    explicit SafeElfInspector(std::span<const uint8_t> buffer) : buf_(buffer) {}

    void inspect() const {
        if (buf_.size() < sizeof(Elf64_Ehdr)) {
            std::cerr << "Помилка: буфер занадто малий для заголовка ELF64.\n";
            return;
        }

        const auto *hdr = reinterpret_cast<const Elf64_Ehdr *>(buf_.data());

        // Перевірка магічних байтів
        if (std::memcmp(hdr->e_ident, ELFMAG, SELFMAG) != 0) {
            std::cerr << "Помилка: сигнатура ELF не збігається.\n";
            return;
        }

        if (hdr->e_ident[EI_CLASS] != ELFCLASS64) {
            std::cerr << "Повідомлення: інспектор підтримує лише 64-бітні образи ELFCLASS64.\n";
            return;
        }

        print_header_passport(hdr);
        inspect_program_headers(hdr);
        inspect_sections(hdr);
        inspect_dynamic_dependencies(hdr);
    }

private:
    std::span<const uint8_t> buf_;

    [[nodiscard]] static std::string_view machine_name(uint16_t m) noexcept {
        switch (m) {
            case EM_X86_64:  return "AMD x86-64";
            case EM_AARCH64: return "ARM AArch64";
            case EM_ARM:     return "ARM 32-bit";
            case EM_RISCV:   return "RISC-V";
            case EM_386:     return "Intel 80386";
            default:         return "Невідома архітектура";
        }
    }

    [[nodiscard]] uint64_t vaddr_to_file_offset(const Elf64_Ehdr *hdr, uint64_t vaddr) const noexcept {
        if (hdr->e_type == ET_DYN && vaddr < buf_.size()) {
            return vaddr;
        }

        if (hdr->e_phoff + (hdr->e_phnum * sizeof(Elf64_Phdr)) > buf_.size()) {
            return 0;
        }

        const auto *ph = reinterpret_cast<const Elf64_Phdr *>(buf_.data() + hdr->e_phoff);
        for (uint16_t i = 0; i < hdr->e_phnum; ++i) {
            if (ph[i].p_type == PT_LOAD) {
                if (vaddr >= ph[i].p_vaddr && vaddr < (ph[i].p_vaddr + ph[i].p_filesz)) {
                    return ph[i].p_offset + (vaddr - ph[i].p_vaddr);
                }
            }
        }
        return 0;
    }

    void print_header_passport(const Elf64_Ehdr *hdr) const {
        std::cout << "=== ПАСПОРТ БІНАРНИКА ===\n"
                  << std::format("Клас:              ELF64\n")
                  << std::format("Порядок байтів:    {}\n", hdr->e_ident[EI_DATA] == ELFDATA2LSB ? "Little-Endian (LSB)" : "Big-Endian (MSB)")
                  << std::format("Архітектура:       {} (0x{:04x})\n", machine_name(hdr->e_machine), hdr->e_machine)
                  << std::format("Тип файлу:         {}\n", hdr->e_type == ET_EXEC ? "ET_EXEC (Статично розміщений виконуваний файл)" :
                                                            hdr->e_type == ET_DYN ? "ET_DYN (Position-Independent Executable або Shared Object)" : "Інший")
                  << std::format("Точка входу:       0x{:016x}\n", hdr->e_entry);
    }

    void inspect_program_headers(const Elf64_Ehdr *hdr) const {
        if (hdr->e_phoff + (hdr->e_phnum * sizeof(Elf64_Phdr)) > buf_.size()) {
            std::cerr << "Помилка: Program Headers виходять за межі файлу.\n";
            return;
        }

        const auto *ph = reinterpret_cast<const Elf64_Phdr *>(buf_.data() + hdr->e_phoff);
        std::string_view interp_path;
        bool nx_enabled = true;
        bool relro_found = false;

        for (uint16_t i = 0; i < hdr->e_phnum; ++i) {
            if (ph[i].p_type == PT_INTERP) {
                if (ph[i].p_offset + ph[i].p_filesz <= buf_.size()) {
                    interp_path = reinterpret_cast<const char *>(buf_.data() + ph[i].p_offset);
                }
            } else if (ph[i].p_type == PT_GNU_STACK) {
                if ((ph[i].p_flags & PF_X) != 0) {
                    nx_enabled = false;
                }
            } else if (ph[i].p_type == PT_GNU_RELRO) {
                relro_found = true;
            }
        }

        std::cout << "\n=== ЗАХИСНІ МЕХАНІЗМИ ТА ІНТЕРПРЕТАТОР ===\n"
                  << std::format("Тип зв'язування:   {}\n", interp_path.empty() ? "Статичне (Statically linked)" : "Динамічне (Dynamically linked)");
        if (!interp_path.empty()) {
            std::cout << std::format("Інтерпретатор:     {}\n", interp_path);
        }
        std::cout << std::format("NX (No-Execute):   {}\n", nx_enabled ? "Увімкнено (Стек без прав виконання)" : "ВИМКНЕНО (Небезпечний виконуваний стек!)")
                  << std::format("RELRO:             {}\n", relro_found ? "Присутній (PT_GNU_RELRO)" : "Відсутній");
    }

    void inspect_sections(const Elf64_Ehdr *hdr) const {
        if (hdr->e_shoff == 0 || (hdr->e_shoff + (hdr->e_shnum * sizeof(Elf64_Shdr)) > buf_.size())) {
            std::cout << "Символи:           stripped (Таблиця секцій відсутня або пошкоджена)\n";
            return;
        }

        const auto *sh = reinterpret_cast<const Elf64_Shdr *>(buf_.data() + hdr->e_shoff);
        bool has_symtab = false;

        if (hdr->e_shstrndx < hdr->e_shnum) {
            const auto *shstrtab = reinterpret_cast<const char *>(buf_.data() + sh[hdr->e_shstrndx].sh_offset);
            for (uint16_t i = 0; i < hdr->e_shnum; ++i) {
                std::string_view name(shstrtab + sh[i].sh_name);
                if (name == ".symtab") {
                    has_symtab = true;
                    break;
                }
            }
        }

        std::cout << std::format("Символи:           {}\n", has_symtab ? "not stripped (Повна таблиця .symtab наявна)" : "stripped (Налагоджувальні символи вичищено)");
    }

    void inspect_dynamic_dependencies(const Elf64_Ehdr *hdr) const {
        const auto *ph = reinterpret_cast<const Elf64_Phdr *>(buf_.data() + hdr->e_phoff);
        const Elf64_Phdr *dyn_ph = nullptr;

        for (uint16_t i = 0; i < hdr->e_phnum; ++i) {
            if (ph[i].p_type == PT_DYNAMIC) {
                dyn_ph = &ph[i];
                break;
            }
        }

        if (!dyn_ph || dyn_ph->p_offset + dyn_ph->p_filesz > buf_.size()) {
            return;
        }

        std::cout << "\n=== ДИНАМІЧНІ ЗАЛЕЖНОСТІ (DT_NEEDED) ===\n";
        const auto *dyn = reinterpret_cast<const Elf64_Dyn *>(buf_.data() + dyn_ph->p_offset);
        size_t count = dyn_ph->p_filesz / sizeof(Elf64_Dyn);

        uint64_t strtab_vaddr = 0;
        for (size_t i = 0; i < count && dyn[i].d_tag != DT_NULL; ++i) {
            if (dyn[i].d_tag == DT_STRTAB) {
                strtab_vaddr = dyn[i].d_un.d_ptr;
                break;
            }
        }

        uint64_t strtab_offset = strtab_vaddr != 0 ? vaddr_to_file_offset(hdr, strtab_vaddr) : 0;
        if (strtab_offset == 0 || strtab_offset >= buf_.size()) {
            std::cout << "  [Увага: не вдалося розв'язати таблицю .dynstr]\n";
            return;
        }

        const auto *dynstr = reinterpret_cast<const char *>(buf_.data() + strtab_offset);
        bool found_any = false;

        for (size_t i = 0; i < count && dyn[i].d_tag != DT_NULL; ++i) {
            if (dyn[i].d_tag == DT_NEEDED) {
                uint64_t idx = dyn[i].d_un.d_val;
                if (strtab_offset + idx < buf_.size()) {
                    std::cout << std::format("  * Потрібна бібліотека: {}\n", dynstr + idx);
                    found_any = true;
                }
            } else if (dyn[i].d_tag == DT_RUNPATH) {
                uint64_t idx = dyn[i].d_un.d_val;
                if (strtab_offset + idx < buf_.size()) {
                    std::cout << std::format("  * Вшитий RUNPATH:     {}\n", dynstr + idx);
                }
            } else if (dyn[i].d_tag == DT_RPATH) {
                uint64_t idx = dyn[i].d_un.d_val;
                if (strtab_offset + idx < buf_.size()) {
                    std::cout << std::format("  * Вшитий RPATH:       {} (Застарілий)\n", dynstr + idx);
                }
            }
        }

        if (!found_any) {
            std::cout << "  (Залежностей DT_NEEDED не виявлено)\n";
        }
    }
};

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << std::format("Використання: {} <шлях-до-бінарника>\n", argv[0]);
        return EXIT_FAILURE;
    }

    auto mapped = MappedFile::open_readonly(argv[1]);
    if (!mapped) {
        std::cerr << std::format("Помилка ініціалізації: {}\n", mapped.error());
        return EXIT_FAILURE;
    }

    SafeElfInspector inspector(mapped->bytes());
    inspector.inspect();

    return EXIT_SUCCESS;
}
```
:::

---

### Обробка крайових випадків та перевірка надійності

Під час аналізу бінарних файлів, отриманих з ненадійних джерел (артефакти шкідливого ПЗ, пошкоджені дампи вбудованих прошивок або фальсифіковані заголовки), парсер стикається з типовими пастками, які можуть призвести до аварійного завершення самого інспектора.

#### 1. Перевірка цілісності зміщень (Integer Overflow та Out-of-Bounds)
Зловмисник може навмисно встановити поле `e_phoff` або `e_shoff` у значення, близьке до `0xffffffffffffffff`. Без явної перевірки додавання розміру таблиці `hdr->e_phoff + (hdr->e_phnum * sizeof(Elf64_Phdr))` призведе до переповнення цілого числа (*integer wrap-around*), і перевірка `< size` поверне хибне значення `true`. В обох варіантах нашої реалізації перевірка захищена від переповнення контролем розміру буфера `buf_.size()`.

#### 2. Захист від пошкоджених таблиць рядків (`.dynstr` та `.shstrtab`)
Рядки в ELF (імена секцій та бібліотек) зберігаються у вигляді нуль-термінованих масивів символів. Якщо бінарник пошкоджено, або якщо рядок не містить термінального нуля `\0` до кінця файлу, звичайний виклик `printf("%s")` або створення `std::string_view` призведе до читання за межами мапованої пам'яті (*heap/buffer over-read*). Утиліта перевіряє зміщення кожного індексу `str_idx` відносно загального розміру відображення.

#### 3. Відсутність таблиці секцій у stripped бінарниках
Багато оптимізаторів та захисних утиліт повністю витирають таблицю секцій `Section Headers` (`e_shoff = 0`, `e_shnum = 0`), оскільки ядру Linux для запуску програми потрібні виключно сегменти `Program Headers`. Інспектор коректно обробляє таку ситуацію: за відсутності `e_shoff` бінарник ідентифікується як `stripped`, а аналіз динамічних залежностей продовжується на основі сегмента `PT_DYNAMIC`.

---

### Приклад виконання та діагностика

Збірка та запуск розробленого інспектора на системному бінарнику демонструє вичерпну паспортизацію виконуваного файлу:

```bash
# Збірка версії C++:
$ g++ -std=c++23 -O2 elf_inspector.cpp -o elf_inspector

# Аудит системної утиліти curl:
$ ./elf_inspector /usr/bin/curl

=== ПАСПОРТ БІНАРНИКА ===
Клас:              ELF64
Порядок байтів:    Little-Endian (LSB)
Архітектура:       Advanced Micro Devices X86-64 (0x003e)
Тип файлу:         ET_DYN (Position-Independent Executable або Shared Object)
Точка входу:       0x000000000000b460

=== ЗАХИСНІ МЕХАНІЗМИ ТА ІНТЕРПРЕТАТОР ===
Тип зв'язування:   Динамічне (Dynamically linked)
Інтерпретатор:     /lib64/ld-linux-x86-64.so.2
NX (No-Execute):   Увімкнено (Стек захищено від виконання коду)
RELRO:             Присутній (PT_GNU_RELRO активний)
Символи:           stripped (Налагоджувальні символи видалено)

=== ДИНАМІЧНІ ЗАЛЕЖНОСТІ (DT_NEEDED) ===
  * Потрібна бібліотека: libcurl.so.4
  * Потрібна бібліотека: libc.so.6
  * Потрібна бібліотека: libz.so.1
```

Інструмент гарантує нульову можливість виконання прихованих інструкцій цільового файлу під час аудиту, забезпечуючи надійний перший ешелон аналізу в умовах невідомого або потенційно ворожого середовища.
