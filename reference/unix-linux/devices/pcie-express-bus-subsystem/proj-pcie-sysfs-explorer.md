# ⚙️ Практика: Дослідження пристроїв PCIe через sysfs та дамп конфігураційного простору

У цій практичній вставці ми розробимо автономну консольну утиліту для користувацького простору (Userspace), яка взаємодіє з підсистемою PCI ядра Linux через віртуальну файлову систему `sysfs` без необхідності написання та завантаження власного модуля ядра. Утиліта сканує каталог `/sys/bus/pci/devices/`, відкриває бінарний файл конфігураційного простору `/sys/bus/pci/devices/<BDF>/config`, парсить його структуру та виводить ключові апаратні характеристики: Vendor ID, Device ID, Class Code, типи й адреси регістрів BAR, а також розшифровує однозв'язаний список можливостей пристрою (Capabilities List).

> 🔧 **Навіщо це.** Замість використання сторонніх інструментів (таких як утиліта `lspci` із пакета `pciutils`) розробники низькорівневого ПЗ, діагностичних комплексів, драйверів користувацького простору на базі `VFIO` (Virtual Function I/O) або високопродуктивних фреймворків обробки мережевого трафіку (типу DPDK) мусять безпосередньо зчитувати конфігураційні ресурси пристроїв та здійснювати відображення фізичних регістрів MMIO у віртуальну пам'ять процесу за допомогою `mmap()`.

---

## 1. Архітектурний задум та улаштування `sysfs`

Файлова система `sysfs` створює у просторі користувача прозору ієрархію об'єктів ядра. Для шини PCI кожен виявлений пристрій отримує свій каталог за шляхом `/sys/bus/pci/devices/0000:BB:DD.F/`, де `0000:BB:DD.F` — це адреса пристрою у форматі BDF (Domain:Bus:Device.Function).

Усередині каталогу пристрою ядро експонує наступні псевдофайли:
* **`config`:** Бінарний файл, що відображає 256 байтів (для PCI) або 4096 байтів (для PCIe) конфігураційного простору пристрою. Читання перших 64 байтів віддає заголовок Header Type 0 або Type 1.
* **`vendor` / `device` / `class`:** Текстові файли, що містять шістнадцяткові значення відповідних полів для швидкої фільтрації.
* **`resource`:** Текстовий список початкових, кінцевих фізичних адрес та прапорців для всіх BARs пристрою.
* **`resource0` .. `resource5`:** Бінарні файли, що відповідають фізичним регіонам BAR. Відкриття файла `resource0` та виконання виклику `mmap()` дозволяє процесу у просторі користувача напряму читати й писати в регістри пристрою в обхід ядра (за наявності привілеїв `CAP_SYS_RAWIO` або прав `root`).

Послідовність дій нашої утиліти:
1. **Сканування каталогу:** Утиліта відкриває каталог `/sys/bus/pci/devices/` та перераховує всі наявні підкаталоги BDF.
2. **Читання конфігураційного простору:** Для кожного пристрою відкривається бінарний файл `config` у режимі читання, і з нього зчитуються перші 64 байти у бінарну структуру `ConfigHeader`.
3. **Парсинг ідентифікаторів:** Зчитуються 16-бітні поля `vendor_id` та `device_id`, а також 24-бітне поле `class_code`.
4. **Декодування BARs:** Утиліта послідовно аналізує 6 елементів масиву `bar[6]`. Якщо молодший біт `bar[i]` дорівнює `1`, ресурс ідентифікується як I/O Port. Якщо біт `0`, це Memory BAR. Якщо біти 1–2 дорівнюють `0b10`, ресурс ідентифікується як 64-бітний MMIO, після чого старші 32 біти беруться з наступного елемента `bar[i+1]`, а індекс `i` інкрементується.
5. **Обхід списку Capabilities:** Перевіряється біт 4 регістра `status`. Якщо біт встановлено у `1`, утиліта зчитує 8-бітне поле `cap_pointer` (зсув `0x34`) і починає обхід однозв'язаного списку. Кожен елемент списку складається з 8-бітного `cap_id` та 8-бітного `next_pointer`. Обхід продовжується, доки `next_pointer` не поверне `0` або значення вийде за межі конфігураційного простору.

---

## 2. Прямий доступ до регістрів MMIO з користувацького простору через `mmap()`

Після розшифровки базової фізичної адреси BAR за допомогою конфігураційного простору або файла `resource`, користувацький застосунок може отримати безпосередній доступ до апаратних регістрів пристрою без залучення системних викликів на кожну операцію.

Для цього використовується системний виклик `mmap()` над файлом `resourceN` (де `N` — номер BAR):

:::tabs
```c
int fd = open("/sys/bus/pci/devices/0000:01:00.0/resource0", O_RDWR | O_SYNC);
if (fd >= 0) {
    void *bar0_mmio = mmap(NULL, bar0_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    /* Доступ до регістрів за адресою bar0_mmio */
    munmap(bar0_mmio, bar0_size);
    close(fd);
}
```
```cpp
// RAII-обгортка для відображення MMIO пам'яті в C++20
class MmappedResource {
public:
    MmappedResource(const std::filesystem::path& path, std::size_t size) : size_(size) {
        int fd = ::open(path.c_str(), O_RDWR | O_SYNC);
        if (fd >= 0) {
            addr_ = ::mmap(nullptr, size_, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            ::close(fd);
        }
    }
    ~MmappedResource() {
        if (addr_ && addr_ != MAP_FAILED) ::munmap(addr_, size_);
    }
    [[nodiscard]] std::span<std::byte> bytes() const {
        return {static_cast<std::byte*>(addr_), size_};
    }
private:
    void* addr_{MAP_FAILED};
    std::size_t size_{0};
};
```
:::

Прапор `O_SYNC` є критично важливим: він гарантує, що ядро відкриває сторінки фізичної пам'яті у режимі Uncached або Write-Combining, вимикаючи процесорне кешування. Після цього будь-яке читання або запис за вказівником `bar0_mmio + offset` породжує миттєву транзакцію TLP на шині PCIe.

Цей механізм слугує основою для драйверів користувацького простору (Userspace Drivers). Проте слід пам'ятати про ризики: помилка у зсуві регістра під час запису через `mmap()` може спричинити апаратне блокування пристрою або згенерувати фатальну помилку шини AER Uncorrectable Fatal.

---

## 3. Реалізація утиліти (`pcie_explorer`)

Нижче наведено робочу реалізацію утиліти двома мовами: класичною мовою C (із використанням низькорівневих POSIX викликів `open`, `read`, `pread`, `readdir`) та сучасний ідіоматичний C++20 (із використанням `std::filesystem`, RAII-обгортанням потоків `std::ifstream`, об'єктно-орієнтованим парсингом та форматованим виводом `std::cout`).

:::tabs
```c
/* pcie_explorer.c — сканер PCIe пристроїв мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>

#define SYSFS_PCI_PATH "/sys/bus/pci/devices"

/* Структура стандартного заголовка PCI Header Type 0 (64 байти) */
typedef struct {
    uint16_t vendor_id;
    uint16_t device_id;
    uint16_t command;
    uint16_t status;
    uint8_t  revision_id;
    uint8_t  prog_if;
    uint8_t  subclass;
    uint8_t  class_code;
    uint8_t  cache_line_size;
    uint8_t  latency_timer;
    uint8_t  header_type;
    uint8_t  bist;
    uint32_t bar[6];
    uint32_t cardbus_cis;
    uint16_t sub_vendor_id;
    uint16_t sub_device_id;
    uint32_t rom_address;
    uint8_t  cap_pointer;
    uint8_t  reserved[7];
    uint8_t  interrupt_line;
    uint8_t  interrupt_pin;
    uint8_t  min_gnt;
    uint8_t  max_lat;
} __attribute__((packed)) pci_header_t;

/* Розшифровка Capabilities */
static void parse_capabilities(int fd, uint8_t cap_ptr) {
    uint8_t pos = cap_ptr;
    printf("    Capabilities list:");
    
    while (pos >= 0x40 && pos < 0xFF) {
        uint8_t cap_hdr[2];
        if (pread(fd, cap_hdr, 2, pos) != 2) break;
        
        uint8_t cap_id = cap_hdr[0];
        uint8_t next_ptr = cap_hdr[1];
        
        switch (cap_id) {
            case 0x01: printf(" [Power Management]"); break;
            case 0x05: printf(" [MSI]"); break;
            case 0x10: printf(" [PCI Express]"); break;
            case 0x11: printf(" [MSI-X]"); break;
            default:   printf(" [Cap ID 0x%02X]", cap_id); break;
        }
        pos = next_ptr;
    }
    printf("\n");
}

/* Обробка одного пристрою BDF */
static void inspect_device(const char *bdf) {
    char path[512];
    snprintf(path, sizeof(path), "%s/%s/config", SYSFS_PCI_PATH, bdf);
    
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        return;
    }
    
    pci_header_t hdr;
    if (read(fd, &hdr, sizeof(hdr)) != sizeof(hdr)) {
        close(fd);
        return;
    }
    
    printf("Пристрій [%s] — Vendor: 0x%04X, Device: 0x%04X (Class 0x%02X%02X)\n",
           bdf, hdr.vendor_id, hdr.device_id, hdr.class_code, hdr.subclass);
    
    /* Парсинг BARs */
    for (int i = 0; i < 6; i++) {
        uint32_t bar = hdr.bar[i];
        if (bar == 0) continue;
        
        if (bar & 0x01) {
            /* I/O BAR */
            printf("    BAR%d: Port I/O на 0x%04X\n", i, bar & ~0x03);
        } else {
            /* Memory BAR */
            int is_64bit = (bar & 0x06) == 0x04;
            int is_prefetchable = (bar & 0x08) != 0;
            uint64_t addr = bar & ~0x0F;
            
            if (is_64bit && i < 5) {
                uint64_t high = hdr.bar[i + 1];
                addr |= (high << 32);
                printf("    BAR%d (64-bit MMIO%s): 0x%016LX\n",
                       i, is_prefetchable ? ", Prefetchable" : "", (unsigned long long)addr);
                i++; /* Пропускаємо наступний BAR, бо він є старшою частиною */
            } else {
                printf("    BAR%d (32-bit MMIO%s): 0x%08X\n",
                       i, is_prefetchable ? ", Prefetchable" : "", bar & ~0x0F);
            }
        }
    }
    
    /* Перевірка прапора Status: Capabilities List */
    if (hdr.status & (1 << 4)) {
        parse_capabilities(fd, hdr.cap_pointer);
    }
    
    close(fd);
}

int main(void) {
    DIR *dir = opendir(SYSFS_PCI_PATH);
    if (!dir) {
        perror("Не вдалося відкрити sysfs pci path");
        return 1;
    }
    
    printf("=== PCI Express sysfs explorer (C implementation) ===\n");
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;
        inspect_device(entry->d_name);
    }
    
    closedir(dir);
    return 0;
}
```
```cpp
// pcie_explorer.cpp — сучасний сканер PCIe пристроїв на C++20
#include <iostream>
#include <fstream>
#include <filesystem>
#include <vector>
#include <string>
#include <iomanip>
#include <cstdint>
#include <memory>

namespace fs = std::filesystem;

namespace pcie {

// Структура конфігураційного простору згідно зі специфікацією PCI-SIG
struct alignas(1) ConfigHeader {
    uint16_t vendor_id;
    uint16_t device_id;
    uint16_t command;
    uint16_t status;
    uint8_t  revision_id;
    uint8_t  prog_if;
    uint8_t  subclass;
    uint8_t  class_code;
    uint8_t  cache_line_size;
    uint8_t  latency_timer;
    uint8_t  header_type;
    uint8_t  bist;
    uint32_t bar[6];
    uint32_t cardbus_cis;
    uint16_t sub_vendor_id;
    uint16_t sub_device_id;
    uint16_t rom_address_low;
    uint16_t rom_address_high;
    uint8_t  cap_pointer;
    uint8_t  reserved[7];
    uint8_t  interrupt_line;
    uint8_t  interrupt_pin;
    uint8_t  min_gnt;
    uint8_t  max_lat;
};

class DeviceInspector {
public:
    explicit DeviceInspector(fs::path bdf_path) 
        : bdf_name_(bdf_path.filename().string()),
          config_path_(bdf_path / "config") {}

    bool inspect() {
        std::ifstream file(config_path_, std::ios::binary);
        if (!file.is_open()) return false;

        ConfigHeader hdr{};
        file.read(reinterpret_cast<char*>(&hdr), sizeof(hdr));
        if (file.gcount() < static_cast<std::streamsize>(sizeof(hdr))) return false;

        print_header_info(hdr);
        print_bars(hdr);

        if (hdr.status & (1 << 4)) { // Capabilities List Present
            print_capabilities(file, hdr.cap_pointer);
        }
        return true;
    }

private:
    void print_header_info(const ConfigHeader& hdr) const {
        std::cout << "Пристрій [" << bdf_name_ << "] — Vendor: 0x" 
                  << std::hex << std::setw(4) << std::setfill('0') << hdr.vendor_id
                  << ", Device: 0x" << std::setw(4) << hdr.device_id
                  << std::dec << " (Class 0x" << std::hex << (int)hdr.class_code << ")\n";
    }

    void print_bars(const ConfigHeader& hdr) const {
        for (std::size_t i = 0; i < 6; ++i) {
            uint32_t bar = hdr.bar[i];
            if (bar == 0) continue;

            if (bar & 0x01) {
                std::cout << "    BAR" << i << ": Port I/O at 0x" 
                          << std::hex << (bar & ~0x03) << std::dec << "\n";
            } else {
                bool is_64bit = (bar & 0x06) == 0x04;
                bool is_prefetchable = (bar & 0x08) != 0;
                uint64_t addr = bar & ~0x0F;

                if (is_64bit && i < 5) {
                    uint64_t high = hdr.bar[i + 1];
                    addr |= (high << 32);
                    std::cout << "    BAR" << i << " (64-bit MMIO" 
                              << (is_prefetchable ? ", Prefetchable" : "") 
                              << "): 0x" << std::hex << addr << std::dec << "\n";
                    ++i; // Пропускаємо старшу частину 64-бітного BAR
                } else {
                    std::cout << "    BAR" << i << " (32-bit MMIO" 
                              << (is_prefetchable ? ", Prefetchable" : "") 
                              << "): 0x" << std::hex << (bar & ~0x0F) << std::dec << "\n";
                }
            }
        }
    }

    void print_capabilities(std::ifstream& file, uint8_t cap_ptr) const {
        uint8_t pos = cap_ptr;
        std::cout << "    Capabilities list:";

        while (pos >= 0x40 && pos < 0xFF) {
            file.seekg(pos, std::ios::beg);
            uint8_t cap_hdr[2]{0, 0};
            file.read(reinterpret_cast<char*>(cap_hdr), 2);
            if (file.gcount() < 2) break;

            uint8_t cap_id = cap_hdr[0];
            uint8_t next_ptr = cap_hdr[1];

            switch (cap_id) {
                case 0x01: std::cout << " [Power Management]"; break;
                case 0x05: std::cout << " [MSI]"; break;
                case 0x10: std::cout << " [PCI Express]"; break;
                case 0x11: std::cout << " [MSI-X]"; break;
                default:   std::cout << " [Cap ID 0x" << std::hex << (int)cap_id << std::dec << "]"; break;
            }
            pos = next_ptr;
        }
        std::cout << "\n";
    }

    std::string bdf_name_;
    fs::path config_path_;
};

} // namespace pcie

int main() {
    const fs::path sysfs_pci_dir{"/sys/bus/pci/devices"};
    if (!fs::exists(sysfs_pci_dir)) {
        std::cerr << "Помилка: sysfs PCI шлях не існує!\n";
        return 1;
    }

    std::cout << "=== PCI Express sysfs explorer (C++20 implementation) ===\n";

    for (const auto& entry : fs::directory_iterator(sysfs_pci_dir)) {
        if (entry.is_directory() || entry.is_symlink()) {
            pcie::DeviceInspector inspector(entry.path());
            inspector.inspect();
        }
    }

    return 0;
}
```
:::

---

## 4. Особливості реалізації, збірка та запуск

Під час роботи з бінарним файлом `config` через `sysfs` слід враховувати два крайових випадки:

1. **Права доступу (Permissions):** Звичайний користувач у Linux має права на прочитання перших 64 байтів файлу `config` (стандартного заголовка PCI). Проте прочитання розширеного простору PCIe (байти `0x0100`..`0x0FFF`) або запис у конфігураційний простір вимагають прав суперкористувача `root` або наявності POSIX-капабіліті `CAP_SYS_RAWIO`.
2. **Порядок байтів (Endianness):** Усі числові поля у специфікації PCI/PCIe зберігаються у форматі Little-Endian. Архітектури x86-64 та ARM64 (у стандартному режимі) є Little-Endian, тому бінарне зчитування байтів безпосередньо у поля `uint16_t` та `uint32_t` є безпечним. На Big-Endian архітектурах (наприклад, PowerPC чи s390x) вимагається явне перетворення за допомогою функцій `le16_to_cpu()` або `le32_to_cpu()`.

Збірка обох версій утиліти здійснюється стандартними компіляторами `gcc` та `g++`:

```bash
# Збірка версії мовою C
gcc -O2 -Wall pcie_explorer.c -o pcie_explorer_c

# Збірка версії мовою C++20
g++ -O2 -Wall -std=c++20 pcie_explorer.cpp -o pcie_explorer_cpp

# Запуск сканування
./pcie_explorer_cpp
```

Приклад виводу утиліти при скануванні NVMe-накопичувача та дискретного графічного адаптера:

```text
Пристрій [0000:01:00.0] — Vendor: 0x10de, Device: 0x2484 (Class 0x03)
    BAR0 (32-bit MMIO): 0xFB000000
    BAR1 (64-bit MMIO, Prefetchable): 0x0000000C00000000
    BAR3 (64-bit MMIO, Prefetchable): 0x0000000C10000000
    BAR5: Port I/O at 0xE000
    Capabilities list: [Power Management] [MSI] [PCI Express] [MSI-X]
Пристрій [0000:04:00.0] — Vendor: 0x144d, Device: 0xa808 (Class 0x01)
    BAR0 (64-bit MMIO): 0x00000000FBD00000
    Capabilities list: [Power Management] [MSI] [MSI-X] [PCI Express]
```
