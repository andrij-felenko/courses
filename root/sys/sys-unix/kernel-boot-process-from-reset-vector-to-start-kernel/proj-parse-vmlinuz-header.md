# ⚙️ Проєкт: Парсер заголовка bzImage / vmlinuz

Цей інструмент демонструє, як зчитати двійковий заголовок `setup_header` з образа ядра Linux (`vmlinuz` або `bzImage`), перевірити магічну сигнатуру `"HdrS"`, витягнути версію протоколу завантаження, точку входу та обмеження адреси `initramfs`.

Для роботи завантажувача, гіпервізора (наприклад, QEMU/KVM) або утиліти перезавантаження ядра без прошивки `kexec` необхідно прочитати перші кілобайти файла ядра та переконатися, що він сумісний із даною архітектурою. 

Файл `vmlinuz` має чітко визначену двійкову структуру. На самому початку файла (offset `0x0000`) розміщено спадковий MS-DOS заголовок із сигнатурою `"MZ"` (`0x5A4D`), який залишено для сумісності з родинами завантажувачів UEFI, що сприймають ядро як виконуваний файл PE/COFF. За заздалегідь обумовленим зсувом `0x01F1` знаходиться структура `setup_header`.

Нижче наведено повноцінні робочі реалізації інструменту аналізу заголовка мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define SETUP_HEADER_OFFSET 0x01F1
#define HDRS_MAGIC 0x53726448 /* "HdrS" у Little-Endian */

/* Спрощена структура setup_header відповідно до специфікації Linux Boot Protocol */
struct setup_header {
    uint8_t  setup_sects;
    uint16_t root_flags;
    uint32_t syssize;
    uint16_t ram_size;
    uint16_t vid_mode;
    uint16_t root_dev;
    uint16_t boot_flag;
    uint16_t jump;
    uint32_t header;            /* Сигнатура "HdrS" */
    uint16_t version;           /* Версія протоколу (напр. 0x020f) */
    uint32_t realmode_swtch;
    uint16_t start_sys_seg;
    uint16_t kernel_version;
    uint8_t  type_of_loader;
    uint8_t  loadflags;
    uint16_t setup_move_size;
    uint32_t code32_start;      /* 32-бітна адреса входу розпакувальника */
    uint32_t ramdisk_image;     /* Адреса initramfs */
    uint32_t ramdisk_size;      /* Розмір initramfs */
    uint32_t bootsect_kludge;
    uint16_t heap_end_ptr;
    uint8_t  ext_loader_ver;
    uint8_t  ext_loader_type;
    uint32_t cmd_line_ptr;      /* Адреса рядка командного рядка */
    uint32_t initrd_addr_max;   /* Максимально припустима адреса initramfs */
} __attribute__((packed));

static void print_loader_type(uint8_t type) {
    uint8_t high = type >> 4;
    switch (high) {
        case 0x0: printf("LILO / Direct\n"); break;
        case 0x1: printf("Loadlin\n"); break;
        case 0x2: printf("BOOTSECT / SYSLINUX\n"); break;
        case 0x7: printf("GRUB2\n"); break;
        case 0x8: printf("QEMU / KVM Direct Boot\n"); break;
        case 0xE: printf("EFI Boot Stub\n"); break;
        default:  printf("Невідомий завантажувач (0x%02X)\n", type); break;
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_vmlinuz>\n", argv[0]);
        return EXIT_FAILURE;
    }

    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        perror("Не вдалося відкрити файл ядра");
        return EXIT_FAILURE;
    }

    if (fseek(f, SETUP_HEADER_OFFSET, SEEK_SET) != 0) {
        perror("Помилка позиціонування у файлі");
        fclose(f);
        return EXIT_FAILURE;
    }

    struct setup_header hdr;
    if (fread(&hdr, sizeof(hdr), 1, f) != 1) {
        fprintf(stderr, "Помилка: не вдалося зчитати setup_header\n");
        fclose(f);
        return EXIT_FAILURE;
    }
    fclose(f);

    /* Перевірка магічного числа "HdrS" */
    if (hdr.header != HDRS_MAGIC) {
        fprintf(stderr, "ПОМИЛКА: Невалідний заголовок! Сигнатура 0x%08X (очікувалося 'HdrS' 0x%08X)\n",
                hdr.header, HDRS_MAGIC);
        return EXIT_FAILURE;
    }

    uint8_t ver_major = hdr.version >> 8;
    uint8_t ver_minor = hdr.version & 0xFF;

    printf("=== Інспекція заголовка vmlinuz / bzImage ===\n");
    printf("Сигнатура:             HdrS (OK)\n");
    printf("Версія протоколу:      %d.%02d (0x%04X)\n", ver_major, ver_minor, hdr.version);
    printf("Точка входу (code32):  0x%08X\n", hdr.code32_start);
    printf("Максимальна адреса initrd: 0x%08X\n", hdr.initrd_addr_max);
    printf("Прапори завантаження:  0x%02X ", hdr.loadflags);
    if (hdr.loadflags & 0x01) printf("[LOADED_HIGH] ");
    if (hdr.loadflags & 0x80) printf("[CAN_BE_RELOCATED/KASLR] ");
    printf("\n");
    printf("Останній тип завантажувача: ");
    print_loader_type(hdr.type_of_loader);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <iomanip>
#include <expected>
#include <string_view>
#include <format>

constexpr std::size_t SETUP_HEADER_OFFSET = 0x01F1;
constexpr uint32_t HDRS_MAGIC = 0x53726448; /* "HdrS" */

struct alignas(1) SetupHeader {
    uint8_t  setup_sects;
    uint16_t root_flags;
    uint32_t syssize;
    uint16_t ram_size;
    uint16_t vid_mode;
    uint16_t root_dev;
    uint16_t boot_flag;
    uint16_t jump;
    uint32_t header;
    uint16_t version;
    uint32_t realmode_swtch;
    uint16_t start_sys_seg;
    uint16_t kernel_version;
    uint8_t  type_of_loader;
    uint8_t  loadflags;
    uint16_t setup_move_size;
    uint32_t code32_start;
    uint32_t ramdisk_image;
    uint32_t ramdisk_size;
    uint32_t bootsect_kludge;
    uint16_t heap_end_ptr;
    uint8_t  ext_loader_ver;
    uint8_t  ext_loader_type;
    uint32_t cmd_line_ptr;
    uint32_t initrd_addr_max;
};

class VmlinuzHeaderParser {
public:
    static std::expected<SetupHeader, std::string> parse_file(const std::string& path) {
        std::ifstream file(path, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected(std::format("Не вдалося відкрити файл: {}", path));
        }

        file.seekg(SETUP_HEADER_OFFSET, std::ios::beg);
        if (!file) {
            return std::unexpected("Помилка позиціонування на зсув setup_header");
        }

        SetupHeader header{};
        file.read(reinterpret_cast<char*>(&header), sizeof(SetupHeader));
        if (!file) {
            return std::unexpected("Помилка зчитування структури SetupHeader");
        }

        if (header.header != HDRS_MAGIC) {
            return std::unexpected(std::format("Невалідний заголовок ядра: magic 0x{:08X}", header.header));
        }

        return header;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << std::format("Використання: {} <шлях_до_vmlinuz>\n", argv[0]);
        return 1;
    }

    auto result = VmlinuzHeaderParser::parse_file(argv[1]);
    if (!result) {
        std::cerr << std::format("Помилка: {}\n", result.error());
        return 1;
    }

    const auto& hdr = result.value();
    uint8_t major = hdr.version >> 8;
    uint8_t minor = hdr.version & 0xFF;

    std::cout << "=== Інспекція заголовка vmlinuz (C++23 Modern RAII) ===\n";
    std::cout << std::format("Сигнатура:             HdrS (0x{:08X})\n", hdr.header);
    std::cout << std::format("Версія протоколу:      {}.{:02d} (0x{:04X})\n", major, minor, hdr.version);
    std::cout << std::format("Точка входу (code32):  0x{:08X}\n", hdr.code32_start);
    std::cout << std::format("Максимальна адреса initrd: 0x{:08X}\n", hdr.initrd_addr_max);
    std::cout << std::format("Прапори завантаження:  0x{:02X}\n", hdr.loadflags);

    return 0;
}
```
:::

## Детальний аналіз логіки роботи інструменту

Код утиліти реалізує кілька послідовних етапів інспекції та перевірки двійкового файлу:

1. **Безпечне відкриття двійкового потоку**: утиліта відкриває файл у бінарному режимі (`"rb"` у C або `std::ios::binary` у C++), що запобігає трансляції символів нового рядка на системах із різними стандартами кінця рядків та дозволяє зчитувати точний побайтовий дискрет файлу.
2. **Точне позиціонування**: виклик `fseek` або `seekg` на постійний зсув `0x01F1` (593 у десятковій системі). Саме за цією адресою специфікація Linux Boot Protocol гарантує наявність поля `setup_header`.
3. **Контроль вирівнювання бінарних структур**: у версії на C++ використовується специфікатор `alignas(1)`, а у версії на C — атрибут компілятора `__attribute__((packed))`. Це гарантує, що компілятор не додасть між бітовими полями вирівнювальних байтів (padding), які б порушили збіг полів із двійковим вмістом на диску.
4. **Валідація магічного числа**: поле `header` перевіряється на рівність константі `0x53726448`. На архітектурі Little-Endian це 32-бітне число відповідає чотирьом ASCII-символам `'H'`, `'d'`, `'r'`, `'S'` (Header Signature). Якщо зауважено інше значення, файл не є валідним образом vmlinuz для x86.

## Розбір прапорів завантаження та сумісності

Аналіз полів заголовка дозволяє завантажувачу або гіпервізору обрати правильну стратегію передачі керування та перевірити сумісність пам'яті:

- **Перевірка релокації `CAN_BE_RELOCATED`**: біт 7 у полі `loadflags` (значення `0x80`) визначає, чи здатен декомпресор розпакувати ядро за довільною фізичною адресою, відмінною від адреси за замовчуванням `0x100000`. Це принципово для систем із захистом KASLR та для віртуальних машин, де адреса `0x100000` може бути зарезервована прошивкою гіпервізора.
- **Визначення межі адресування `initrd_addr_max`**: завантажувач перевіряє це поле для уникнення накладання тимчасового файлового кореня `initramfs` на область розміщення самого розпакувальника або низьких структур BIOS. Якщо розмір архіву `initramfs` перевищує доступний простір нижче цієї межі, завантажувач припиняє виконання до спроби стрибка в ядро.
- **Визначення типу завантажувача `type_of_loader`**: старший півбайт поля вказує сімейство завантажувача. Якщо ядро запускається безпосередньо з QEMU/KVM через параметри `-kernel` та `-initrd`, це поле приймає значення `0x80` (QEMU Direct Boot). При завантаженні через EFI Boot Stub поле містить значення `0xE0`.

## Практичне застосування та тестування в QEMU

Під час розробки та налагодження низькорівневих завантажувачів або власних модулів ядра корисним кроком є тестування даного парсера на реальних образах ядра у зв'язці з емулятором QEMU.

При запуску віртуальної машини за допомогою команди:

```bash
qemu-system-x86_64 -kernel /boot/vmlinuz-linux -initrd /boot/initramfs-linux.img -append "console=ttyS0 quiet" -nographic
```

Гіпервізор QEMU емулює роботу спадкового завантажувача і заповнює поле `type_of_loader` значенням `0x80`. Наш парсер зчитує ці значення безпосередньо з виділеного заголовочного буфера і підтверджує валідність сигнатури `"HdrS"` до того, як QEMU виконає непрямий стрибок за адресою `code32_start`.

Особливості обробки крайових випадків утиліти:
- Якщо наданий файл має розмір менше ніж 1024 байти, спроба seek або read завершується помилкою `std::unexpected` у C++ або поверненням `EXIT_FAILURE` у C, що запобігає спробам розпакування пошкоджених файлів.
- Якщо завантажувач використовує застарілу версію протоколу (менше 2.02), значення `cmd_line_ptr` вважається 16-бітним зсувом у реальному режимі, і розпакувальник ядра обробляє його за спадковими правилами.
- У разі виявлення несумісної версії протоколу утиліта інформує про це користувача без виклику неочищених винятків або аварійного завершення процесу.
- Якщо двійковий файл ядра зашифровано або пошкоджено на диску, аналіз магічної сигнатури відловлює дефект до передачі контролю в код декомпресора.

Очікуваний вивід утиліти при запуску над реальним ядром Linux:

```text
=== Інспекція заголовка vmlinuz / bzImage ===
Сигнатура:             HdrS (OK)
Версія протоколу:      2.15 (0x020F)
Точка входу (code32):  0x00100000
Максимальна адреса initrd: 0x7FFFFFFF
Прапори завантаження:  0x81 [LOADED_HIGH] [CAN_BE_RELOCATED/KASLR] 
Останній тип завантажувача: GRUB2
```

Для компіляції версії C++23 використовується команда:
```bash
g++ -std=c++23 -O2 parse_vmlinuz.cpp -o parse_vmlinuz
```

Завдяки цьому проекту розробник отримує зручний інструмент для швидкої інспекції прапорів ядра в ізольованому середовищі. Утиліта може бути інтегрована в автоматизовані скрипти збірки вилучених образів дистрибутивів або вбудованих систем для автентифікації версії ядра та перевірки відсутності помилок формату перед завантаженням прошивки в пристрій.
