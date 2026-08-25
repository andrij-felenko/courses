# ⚙️ Складання та аналіз UKI: інструментарій і розбір PE-секцій

Автоматизація збірки Unified Kernel Image (UKI) вимагає розуміння двох рівнів: високорівневого інструментарію генерації образів (`ukify` та `objcopy`) і низькорівневого аналізу таблиці PE-секцій. Розбір заголовків PE/COFF безпосередньо в коді дозволяє перевірити цілісність секцій `.linux`, `.initrd`, `.cmdline` та `.sbat` перед відправкою образу на завантаження або підпис.

Практичне формування Unified Kernel Image охоплює два взаємодоповнюючі підходи: автоматичне агрегування ядерного образу, initrd та параметрів через `ukify` і пряме компонування секцій за допомогою `objcopy`. Обидва інструменти розраховують віртуальні адреси та вирівнювання у заголовках PE/COFF для точного зв'язування ELF-ядра та додаткових даних із бінарною заглушкою systemd-stub. Програмний розбір таблиці секцій у C та C++ забезпечує строгий контроль структури завантажувального бінарника до моменту підписання ключами Secure Boot.

---

## Інструментарій збірки образів UKI у консолі

Сучасний дистрибутив Linux пропонує два основні шляхи компонування секцій у кінцевий виконуваний бінарник `.efi`. Перший шлях — використання спеціалізованого скрипта `systemd-ukify`, який розраховує вирівнювання секцій автоматично. Другий шлях — низькорівнева компоновка через `objcopy` з пакету GNU Binutils.

### Використання утиліти systemd-ukify

Офіційний інструмент `ukify` (або `systemd-ukify`) автоматично аналізує вхідні файли, формує потрібні заголовки PE, розраховує віртуальні адреси секцій та може одразу викликати утиліти підписання Secure Boot:

```bash
# Збірка атомарного UKI з вбудованим initramfs та параметрами ядра
systemd-ukify build \
    --linux=/boot/vmlinuz-6.10.3-200.fc40.x86_64 \
    --initrd=/boot/initramfs-6.10.3-200.fc40.x86_64.img \
    --cmdline="root=UUID=8f3c1a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b ro quiet" \
    --os-release=@/etc/os-release \
    --sbat=@/usr/share/sbat/sbat.csv \
    --uname="6.10.3-200.fc40.x86_64" \
    --stub=/usr/lib/systemd/boot/efi/linuxx64.efi.stub \
    --output=/boot/efi/EFI/Linux/fedora-6.10.3.efi
```

Ключові аргументи команди:
- `--linux`: шлях до бінарного образу ядра `vmlinuz`.
- `--initrd`: шлях до стисненого архіву початкової файлової системи. Якщо системі потрібен мікрокод CPU (Intel/AMD), утиліті можна передати кілька прапорців `--initrd`, і вона склеїть їх у єдину секцію `.initrd`.
- `--cmdline`: рядок параметрів завантаження або шлях до файлу із текстом командного рядка (через префікс `@`).
- `--stub`: шлях до бінарної заглушки `systemd-stub`, яка береться з пакету `systemd-boot` або `systemd-udev`.
- `--output`: підсумковий шлях збереження готовго бінарника `.efi` у розділі ESP.

### Низькорівневе компонування через objcopy та підписання

Якщо спеціалізована утиліта `ukify` відсутня у мінімалістичному середовищі збірки, той самий результат досягається за допомогою `objcopy` з пакету GNU Binutils.

Процес ручного компонування складається з трьох послідовних кроків:
1. Підготовка текстового файла з командним рядком ядра.
2. Послідовне додавання нових секцій у бінарний файл заглушки `linuxx64.efi.stub` із вказуванням віртуальних адрес завантаження (`--change-section-vma`).
3. Підписання готового бінарника за допомогою утиліти `sb-sign` або `sbctl`.

```bash
# Крок 1: Створення тимчасового файла командного рядка
echo -n "root=UUID=8f3c1a2b-3c4d-5e6f-7a8b-9c0d1e2f3a4b ro quiet splash" > /tmp/cmdline.txt

# Крок 2: Ручна додамп секцій у заглушку systemd-stub
objcopy \
    --add-section .osrel=/etc/os-release --change-section-vma .osrel=0x20000 \
    --add-section .cmdline=/tmp/cmdline.txt --change-section-vma .cmdline=0x30000 \
    --add-section .linux=/boot/vmlinuz --change-section-vma .linux=0x40000 \
    --add-section .initrd=/boot/initramfs.img --change-section-vma .initrd=0x3000000 \
    /usr/lib/systemd/boot/efi/linuxx64.efi.stub /tmp/uki-unsigned.efi

# Крок 3: Підпис готового бінарника ключем Secure Boot
sb-sign --key /etc/secureboot/db.key --cert /etc/secureboot/db.crt \
        --output /boot/efi/EFI/Linux/fedora-custom.efi /tmp/uki-unsigned.efi
```

У цій послідовності прапорець `--change-section-vma` задає зміщення віртуальної пам'яті (Virtual Memory Address), за якими секції розміщуватимуться в оперативній пам'яті під час виконання заглушки.

---

## Архітектура програмного аналізатора PE/COFF секцій UKI

Для здійснення автоматичної перевірки цілісності секцій UKI у сервісах моніторингу або інсталяторах корисно мати власний парсер заголовка PE/COFF, який працює без зовнішніх бібліотечних залежностей.

### Механізм розбору заголовка PE/COFF

Програма відкриває файл `.efi` через системний виклик відображення пам'яті `mmap`. Це дозволяє обходити байтовий масив файлу без постійного виклику опитувань `read()` і без копіювання буферів у пам'ять користувача.

Алгоритм обходу заголовків працює за такими кроками:

1. **Перевірка DOS-заголовка (`IMAGE_DOS_HEADER`):**
   Перші 64 байти файлу мапуються на структуру DOS. Програма перевіряє двобайтове магічне число `e_magic`. Воно має дорівнювати `0x5A4D` (символи `MZ` — ініціали Марка Збіковскі, розробника MS-DOS).
2. **Перехід до PE-заголовка (`e_lfanew`):**
   Поле `e_lfanew` містить байтове зміщення від початку файла до головного заголовка PE (`IMAGE_NT_HEADERS64`). Програма перевіряє чотирибайтову сигнатуру `Signature`, яка має дорівнювати `0x00004550` (символи `PE\0\0`).
3. **Обчислення адреси таблиці секцій (`IMAGE_SECTION_HEADER`):**
   Адреса першої секції розраховується від початкового зміщення PE-заголовка плюс розмір сигнатури, розмір заголовка `FileHeader` та розмір опціонального заголовка `SizeOfOptionalHeader`.
4. **Ітерація по секціях:**
   Програма виконує цикл за кількістю секцій `NumberOfSections`. Для кожної секції читається 8-байтове ім'я `Name`, файлове зміщення `PointerToRawData` та фактичний розмір `SizeOfRawData`. 

Якщо ім'я секції збігається з `.cmdline` або `.osrel`, програма виводить її текстовий вміст безпосередньо з відображеної пам'яті.

---

## Повний вихідний код розбору PE-секцій UKI

Нижче наведено робочу реалізацію парсера двох мов — C та C++.

:::tabs
```c
/* uki_parser.c — Низькорівневий аналіз PE/COFF секцій UKI мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>

#define DOS_MAGIC 0x5A4D     /* "MZ" */
#define NT_MAGIC  0x00004550 /* "PE\0\0" */

#pragma pack(push, 1)
typedef struct {
    uint16_t e_magic;
    uint8_t  e_res[58];
    uint32_t e_lfanew;
} DosHeader;

typedef struct {
    uint16_t Machine;
    uint16_t NumberOfSections;
    uint32_t TimeDateStamp;
    uint32_t PointerToSymbolTable;
    uint32_t NumberOfSymbols;
    uint16_t SizeOfOptionalHeader;
    uint16_t Characteristics;
} FileHeader;

typedef struct {
    uint32_t Signature;
    FileHeader FileHeader;
} NtHeaders64;

typedef struct {
    uint8_t  Name[8];
    uint32_t VirtualSize;
    uint32_t VirtualAddress;
    uint32_t SizeOfRawData;
    uint32_t PointerToRawData;
    uint32_t PointerToRelocations;
    uint32_t PointerToLinenumbers;
    uint16_t NumberOfRelocations;
    uint16_t NumberOfLinenumbers;
    uint32_t Characteristics;
} SectionHeader;
#pragma pack(pop)

static void parse_uki_sections(const uint8_t *map, size_t size) {
    if (size < sizeof(DosHeader)) {
        fprintf(stderr, "Помилка: файл занадто малий для DOS-заголовка\n");
        return;
    }

    const DosHeader *dos = (const DosHeader *)map;
    if (dos->e_magic != DOS_MAGIC) {
        fprintf(stderr, "Помилка: відсутній сигнатура MZ\n");
        return;
    }

    if (dos->e_lfanew + sizeof(NtHeaders64) > size) {
        fprintf(stderr, "Помилка: некоректне зміщення PE-заголовка\n");
        return;
    }

    const NtHeaders64 *nt = (const NtHeaders64 *)(map + dos->e_lfanew);
    if (nt->Signature != NT_MAGIC) {
        fprintf(stderr, "Помилка: відсутня сигнатура PE\\0\\0\n");
        return;
    }

    uint16_t num_sections = nt->FileHeader.NumberOfSections;
    uint32_t sec_offset = dos->e_lfanew + sizeof(uint32_t) + sizeof(FileHeader) + 
                         nt->FileHeader.SizeOfOptionalHeader;

    printf("Знайдено PE-секцій: %u\n", num_sections);
    printf("-----------------------------------------------------\n");

    for (uint16_t i = 0; i < num_sections; i++) {
        if (sec_offset + sizeof(SectionHeader) > size) break;
        const SectionHeader *sec = (const SectionHeader *)(map + sec_offset);
        
        char name[9] = {0};
        memcpy(name, sec->Name, 8);

        printf("[%02u] Секція: %-8s | Файлове зміщення: 0x%08X | Розмір: %u B\n",
               i + 1, name, sec->PointerToRawData, sec->SizeOfRawData);

        /* Друк вмісту текстових секцій .cmdline та .osrel */
        if (strcmp(name, ".cmdline") == 0 || strcmp(name, ".osrel") == 0) {
            if (sec->PointerToRawData + sec->SizeOfRawData <= size) {
                printf("     Вміст (%s):\n     \"%.*s\"\n", 
                       name, (int)sec->SizeOfRawData, (const char *)(map + sec->PointerToRawData));
            }
        }

        sec_offset += sizeof(SectionHeader);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <path-to-uki.efi>\n", argv[0]);
        return 1;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити файл");
        return 1;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("Помилка отримання розміру");
        close(fd);
        return 1;
    }

    uint8_t *map = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) {
        perror("Помилка mmap");
        close(fd);
        return 1;
    }

    parse_uki_sections(map, st.st_size);

    munmap(map, st.st_size);
    close(fd);
    return 0;
}
```
```cpp
// uki_parser.cpp — Ідіоматичний парсер PE/COFF секцій UKI мовою C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <span >
#include <memory>
#include <optional>
#include <cstdint>
#include <cstring>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

namespace uki {

constexpr uint16_t DOS_MAGIC = 0x5A4D;
constexpr uint32_t NT_MAGIC  = 0x00004550;

#pragma pack(push, 1)
struct DosHeader {
    uint16_t e_magic;
    uint8_t  e_res[58];
    uint32_t e_lfanew;
};

struct FileHeader {
    uint16_t Machine;
    uint16_t NumberOfSections;
    uint32_t TimeDateStamp;
    uint32_t PointerToSymbolTable;
    uint32_t NumberOfSymbols;
    uint16_t SizeOfOptionalHeader;
    uint16_t Characteristics;
};

struct NtHeaders64 {
    uint32_t Signature;
    FileHeader FileHeader;
};

struct SectionHeader {
    uint8_t  Name[8];
    uint32_t VirtualSize;
    uint32_t VirtualAddress;
    uint32_t SizeOfRawData;
    uint32_t PointerToRawData;
    uint32_t PointerToRelocations;
    uint32_t PointerToLinenumbers;
    uint16_t NumberOfRelocations;
    uint16_t NumberOfLinenumbers;
    uint32_t Characteristics;
};
#pragma pack(pop)

// RAII обгортка для безпечного керування пам'яттю mmap
class MappedFile {
public:
    explicit MappedFile(const std::string& path) {
        int fd = ::open(path.c_str(), O_RDONLY);
        if (fd < 0) return;

        struct stat st{};
        if (::fstat(fd, &st) == 0 && st.st_size > 0) {
            size_ = static_cast<size_t>(st.st_size);
            void* addr = ::mmap(nullptr, size_, PROT_READ, MAP_PRIVATE, fd, 0);
            if (addr != MAP_FAILED) {
                data_ = static_cast<const std::byte*>(addr);
            }
        }
        ::close(fd);
    }

    ~MappedFile() {
        if (data_ && size_ > 0) {
            ::munmap(const_cast<void*>(static_cast<const void*>(data_)), size_);
        }
    }

    MappedFile(const MappedFile&) = delete;
    MappedFile& operator=(const MappedFile&) = delete;

    [[nodiscard]] std::span<const std::byte> bytes() const noexcept {
        return {data_, size_};
    }

    [[nodiscard]] bool valid() const noexcept { return data_ != nullptr; }

private:
    const std::byte* data_{nullptr};
    size_t size_{0};
};

class UkiInspector {
public:
    explicit UkiInspector(std::span<const std::byte> buffer) : buffer_(buffer) {}

    void print_report() const {
        if (buffer_.size() < sizeof(DosHeader)) {
            std::cerr << "Буфер занадто малий для DOS заголовка\n";
            return;
        }

        const auto* dos = reinterpret_cast<const DosHeader*>(buffer_.data());
        if (dos->e_magic != DOS_MAGIC) {
            std::cerr << "Файл не містить сигнатури MZ\n";
            return;
        }

        if (dos->e_lfanew + sizeof(NtHeaders64) > buffer_.size()) {
            std::cerr << "Некоректний зсув PE заголовка\n";
            return;
        }

        const auto* nt = reinterpret_cast<const NtHeaders64*>(buffer_.data() + dos->e_lfanew);
        if (nt->Signature != NT_MAGIC) {
            std::cerr << "Файл не містить сигнатури PE\\0\\0\n";
            return;
        }

        const uint16_t count = nt->FileHeader.NumberOfSections;
        size_t sec_offset = dos->e_lfanew + sizeof(uint32_t) + sizeof(FileHeader) + 
                            nt->FileHeader.SizeOfOptionalHeader;

        std::cout << "Знайдено PE-секцій: " << count << "\n";
        std::cout << "-----------------------------------------------------\n";

        for (uint16_t i = 0; i < count; ++i) {
            if (sec_offset + sizeof(SectionHeader) > buffer_.size()) break;
            const auto* sec = reinterpret_cast<const SectionHeader*>(buffer_.data() + sec_offset);

            char name_buf[9] = {0};
            std::memcpy(name_buf, sec->Name, 8);
            std::string_view name(name_buf);

            std::cout << "[" << (i + 1) << "] Секція: " << name 
                      << " | Зміщення: 0x" << std::hex << sec->PointerToRawData 
                      << std::dec << " | Розмір: " << sec->SizeOfRawData << " B\n";

            if (name == ".cmdline" || name == ".osrel") {
                if (sec->PointerToRawData + sec->SizeOfRawData <= buffer_.size()) {
                    std::string_view text_val(
                        reinterpret_cast<const char*>(buffer_.data() + sec->PointerToRawData),
                        sec->SizeOfRawData
                    );
                    std::cout << "     Вміст (" << name << "):\n     \"" << text_val << "\"\n";
                }
            }

            sec_offset += sizeof(SectionHeader);
        }
    }

private:
    std::span<const std::byte> buffer_;
};

} // namespace uki

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Використання: " << argv[0] << " <path-to-uki.efi>\n";
        return 1;
    }

    uki::MappedFile file(argv[1]);
    if (!file.valid()) {
        std::cerr << "Не вдалося відкрити або відобразити файл\n";
        return 1;
    }

    uki::UkiInspector inspector(file.bytes());
    inspector.print_report();

    return 0;
}
```
:::

---

## Особливості порівняння реалізацій C та C++20

Аналіз двох версій коду демонструє принципову різницю в підходах до управління ресурсами та безпеки роботи з пам'яттю:

1. **Безпека меж буфера (`std::span`):**
   У версії C перевірка меж `sec_offset + sizeof(SectionHeader) > size` виконується через ручне порівняння сирих вказівників. У версії C++20 клас `std::span<const std::byte>` обгортає неперервний фрагмент пам'яті й надає точний метод `.size()`, що виключає ризик виходу за межі відображеного буфера.
2. **Автоматичне управління ресурсами (RAII):**
   У програмі на мові C закриття файлового дескриптора `close(fd)` та виклик `munmap()` виконуються вручну у кількох гілках повернення з помилкою. У C++20 клас `MappedFile` застосовує паттерн RAII: деструктор автоматично викликає `munmap` та `close` при виході об'єкта зі зони видимості, навіть якщо під час обробки виникне виняток.
3. **Робота зі рядками без копіювання (`std::string_view`):**
   Замість виділення пам'яті під тимчасові масиви через `malloc` або використання схильних до переповнення `strcpy`, версія C++20 створює об'єкти `std::string_view`. Вони посилаються безпосередньо на байти у мапованому файлі без жодного копіювання пам'яті.

---

## Простеження активного UKI в працюючій системі

Коли операційна система завантажена через UKI, прошивка UEFI та `systemd-stub` залишають у системній файловій системі `efivarfs` службові змінні.

Перевірити стан активного завантаження та витягнути значення виміряних секцій можна за допомогою інструменту `bootctl`:

```bash
# Перевірка статусу завантажувача та виявлення активного UKI
bootctl status

# Виведення виміряних значень TPM2 PCR 11 для активного образу
systemd-measure status
```

Діректорія `/sys/firmware/efi/efivars/` містить змінні `LoaderImageIdentifier-4a67b082-...`, які зберігають шлях до бінарника `.efi`, з якого було здійснено завантаження. Це дозволяє скриптам оновлення точно визначати, який UKI зараз виконується у системі.
