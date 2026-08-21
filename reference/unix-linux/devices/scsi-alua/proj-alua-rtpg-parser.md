# ⚙️ Зчитування та розбір дескрипторів ALUA через SCSI Generic SG_IO

Утиліти автоматичного керування багатошляховістю в Linux (зокрема демон `multipathd` та модуль ядра `scsi_dh_alua`) самостійно зчитують стани портів цілі через внутрішні інтерфейси ядра та відображають їх у віртуальній файловій системі `sysfs`. Проте під час введення в експлуатацію нових систем збереження даних, низькорівневої діагностики каналів Fibre Channel/iSCSI або створення спеціалізованих агентів моніторингу виникає потреба звернутися до контролера сховища безпосередньо.

Пряме опитування через інтерфейс драйвера **SCSI Generic (`/dev/sg*`)** або безпосередньо через блоковий пристрій (`/dev/sd*`) за допомогою керуючого виклику `ioctl(..., SG_IO, ...)` дозволяє отримати сирі двійкові дескриптори безпосередньо з мікропрограми дискового масиву в обхід кешування операційної системи. Це усуває затримки оновлення інформації в `sysfs` та дає змогу верифікувати коректність поведінки цільових портів під час аварійного перемикання (*failover*).

У цьому проекті реалізовано низькорівневу консольну утиліту двома мовами — класичним C та сучасним ідіоматичним C++23. Програма формує 16-байтовий блок дескриптора команди (CDB) **REPORT TARGET PORT GROUPS (RTPG)**, надсилає його до пристрою через інтерфейс `SG_IO`, перевіряє статус виконання та байти Sense-даних, після чого виконує побайтовий розбір отриманого двійкового потоку стандарту SPC-4.

---

## Архітектура та принцип роботи утиліти

Взаємодія з накопичувачем на рівні команд SCSI через інтерфейс `SG_IO` вимагає суворого дотримання протокольного контракту та складається з таких послідовних етапів:

1. **Відкриття дескриптора файлу пристрою:** Програма відкриває символьний або блоковий пристрій (`/dev/sg1` або `/dev/sdb`) у режимі читання та запису (`O_RDWR | O_NONBLOCK`). Для надсилання сирих команд SCSI процес обов'язково повинен мати права суперкористувача `root` або володіти системною можливістю `CAP_SYS_RAWIO`.
2. **Формування CDB команди RTPG:** Створюється 16-байтовий буфер, де байт 0 містить код операції `0xA3` (*MAINTENANCE IN*), байт 1 містить код дії обслуговування `0x0A` (*REPORT TARGET PORT GROUPS*), а в байтах 6..9 записується розмір виділеного буфера прийому даних (1024 байти) у порядку байтів мережі (*big-endian*).
3. **Підготовка структури `struct sg_io_hdr`:** Заповнюються параметри напрямку передачі даних (`SG_DXFER_FROM_DEV`), вказівники на буфер відповіді та буфер сенс-даних, а також тайм-аут очікування відповіді від масиву (5000 мс).
4. **Виконання керуючого виклику `ioctl`:** Ядро транслює запит у відповідний драйвер HBA (Fibre Channel, SAS або iSCSI) і надсилає кадр по фабриці SAN.
5. **Розбір бінарної структури відповіді:** Перші 4 байти відповіді інтерпретуються як довжина списку параметрів. Далі у циклі зчитуються 8-байтові заголовки дескрипторів цільових груп портів (TPG), витягується біт `PREF` (бажаний порт), 4-бітовий код стану доступу ALUA (AO, ANO, SB, UN, TO), маска дозволених переходів, номер групи `TPG ID` та список 4-байтових ідентифікаторів портів цілі (*Relative Target Port ID*).

```
+──────────────────────────────────────────────────────────────────────────+
|                    ЖИТТЄВИЙ ЦИКЛ ВИКЛИКУ SG_IO В УТИЛІТІ                 |
+──────────────────────────────────────────────────────────────────────────+
| 1. open("/dev/sg1", O_RDWR) ──► Отримання файлового дескриптора fd      |
| 2. Заповнення CDB 0xA3 0x0A  ──► Формування 16-байтового кадру команди   |
| 3. Заповнення sg_io_hdr      ──► Реєстрація буферів і тайм-ауту 5000 мс  |
| 4. ioctl(fd, SG_IO, &hdr)    ──► Надсилання через підсистему SCSI ядра  |
| 5. Перевірка status == 0     ──► Якщо CHECK CONDITION: аналіз Sense-буфера|
| 6. Двійковий розбір потоку   ──► Декодування TPG, станів ALUA та портів  |
+──────────────────────────────────────────────────────────────────────────+
```

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <scsi/sg.h>
#include <scsi/scsi.h>

#define RTPG_CDB_LEN       16
#define RTPG_BUF_SIZE      1024
#define SENSE_BUF_SIZE     64
#define DEFAULT_TIMEOUT_MS 5000

/* Текстове представлення асиметричного стану доступу за стандартом SPC-4 */
static const char *alua_state_str(uint8_t state) {
    switch (state & 0x0F) {
        case 0x00: return "Active/Optimized (AO)";
        case 0x01: return "Active/Non-Optimized (ANO)";
        case 0x02: return "Standby (SB)";
        case 0x03: return "Unavailable (UN)";
        case 0x0E: return "Standby Offline";
        case 0x0F: return "Transitioning (TO)";
        default:   return "Reserved / Unknown";
    }
}

/* Текстовий опис коду статусу TPG */
static const char *alua_status_str(uint8_t status) {
    switch (status) {
        case 0x00: return "No status / Normal";
        case 0x01: return "Altered by SET TARGET PORT GROUPS";
        case 0x02: return "Altered by Target controller (Implicit)";
        default:   return "Vendor specific";
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_пристрою_scsi> (наприклад /dev/sg1 або /dev/sdb)\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *dev_path = argv[1];
    int fd = open(dev_path, O_RDWR | O_NONBLOCK);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій");
        return EXIT_FAILURE;
    }

    uint8_t cdb[RTPG_CDB_LEN];
    memset(cdb, 0, sizeof(cdb));
    cdb[0] = 0xA3; /* MAINTENANCE IN */
    cdb[1] = 0x0A; /* Service Action: REPORT TARGET PORT GROUPS */
    /* Allocation Length: 1024 байти (big-endian uint32 у байтах 6..9) */
    uint32_t alloc_len = htonl(RTPG_BUF_SIZE);
    memcpy(&cdb[6], &alloc_len, sizeof(alloc_len));

    uint8_t resp_buf[RTPG_BUF_SIZE];
    uint8_t sense_buf[SENSE_BUF_SIZE];
    memset(resp_buf, 0, sizeof(resp_buf));
    memset(sense_buf, 0, sizeof(sense_buf));

    struct sg_io_hdr io_hdr;
    memset(&io_hdr, 0, sizeof(io_hdr));
    io_hdr.interface_id = 'S';
    io_hdr.cmdp = cdb;
    io_hdr.cmd_len = sizeof(cdb);
    io_hdr.dxfer_direction = SG_DXFER_FROM_DEV;
    io_hdr.dxfer_len = sizeof(resp_buf);
    io_hdr.dxferp = resp_buf;
    io_hdr.sbp = sense_buf;
    io_hdr.mx_sb_len = sizeof(sense_buf);
    io_hdr.timeout = DEFAULT_TIMEOUT_MS;

    printf("Надсилання команди REPORT TARGET PORT GROUPS до %s...\n", dev_path);
    if (ioctl(fd, SG_IO, &io_hdr) < 0) {
        perror("Помилка виклику ioctl SG_IO");
        close(fd);
        return EXIT_FAILURE;
    }

    if (io_hdr.status != 0) {
        fprintf(stderr, "Пристрій повернув статус SCSI: 0x%02X (CHECK CONDITION)\n", io_hdr.status);
        if (io_hdr.sb_len_wr > 0) {
            uint8_t sense_key = sense_buf[2] & 0x0F;
            uint8_t asc = sense_buf[12];
            uint8_t ascq = sense_buf[13];
            fprintf(stderr, "Sense Key: 0x%02X, ASC: 0x%02X, ASCQ: 0x%02X\n", sense_key, asc, ascq);
        }
        close(fd);
        return EXIT_FAILURE;
    }

    /* Перші 4 байти — загальна довжина наступних даних дескрипторів (big-endian) */
    uint32_t data_len = (resp_buf[0] << 24) | (resp_buf[1] << 16) | (resp_buf[2] << 8) | resp_buf[3];
    printf("Отримано успішну відповідь. Довжина даних параметра: %u байтів\n\n", data_len);

    uint32_t offset = 4;
    uint32_t total_limit = 4 + data_len;
    if (total_limit > RTPG_BUF_SIZE) {
        total_limit = RTPG_BUF_SIZE;
    }

    int tpg_index = 1;
    while (offset + 8 <= total_limit) {
        uint8_t pref_state = resp_buf[offset];
        uint8_t is_pref = (pref_state & 0x80) ? 1 : 0;
        uint8_t state = pref_state & 0x0F;
        uint8_t sup_mask = resp_buf[offset + 1];
        uint16_t tpg_id = (resp_buf[offset + 2] << 8) | resp_buf[offset + 3];
        uint8_t status_code = resp_buf[offset + 4];
        uint16_t port_count = (resp_buf[offset + 6] << 8) | resp_buf[offset + 7];

        printf("=== [Цільова група портів #%d (TPG ID: %u / 0x%04X)] ===\n", tpg_index, tpg_id, tpg_id);
        printf("  Стан доступу ALUA:    %s\n", alua_state_str(state));
        printf("  Бажана група (PREF):  %s\n", is_pref ? "ТАК (Preferred)" : "НІ");
        printf("  Маска підтримки:      0x%02X (AO:%d, ANO:%d, SB:%d, UN:%d, TO:%d)\n",
               sup_mask,
               (sup_mask & 0x01) ? 1 : 0,
               (sup_mask & 0x02) ? 1 : 0,
               (sup_mask & 0x04) ? 1 : 0,
               (sup_mask & 0x08) ? 1 : 0,
               (sup_mask & 0x80) ? 1 : 0);
        printf("  Статус зміни:         %s\n", alua_status_str(status_code));
        printf("  Кількість портів:     %u\n", port_count);

        offset += 8;
        printf("  Список портів цілі:\n");
        for (uint16_t p = 0; p < port_count; ++p) {
            if (offset + 4 > total_limit) {
                fprintf(stderr, "  [Попередження: буфер обірвався передчасно]\n");
                break;
            }
            uint16_t port_id = (resp_buf[offset + 2] << 8) | resp_buf[offset + 3];
            printf("    - Порт #%u (Relative Target Port ID: %u / 0x%04X)\n", p + 1, port_id, port_id);
            offset += 4;
        }
        printf("\n");
        tpg_index++;
    }

    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <expected>
#include <format>
#include <cstring>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <scsi/sg.h>
#include <scsi/scsi.h>

// RAII-обгортка над файловим дескриптором системного пристрою
class ScsiDevice {
public:
    explicit ScsiDevice(const std::string_view path) {
        fd_ = ::open(path.data(), O_RDWR | O_NONBLOCK);
    }

    ~ScsiDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    ScsiDevice(const ScsiDevice&) = delete;
    ScsiDevice& operator=(const ScsiDevice&) = delete;

    ScsiDevice(ScsiDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    ScsiDevice& operator=(ScsiDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int get_fd() const noexcept { return fd_; }

private:
    int fd_{-1};
};

// Доменна структура цільової групи портів ALUA
struct TargetPortGroup {
    uint16_t tpg_id{0};
    uint8_t access_state{0};
    bool is_preferred{false};
    uint8_t supported_mask{0};
    uint8_t status_code{0};
    std::vector<uint16_t> relative_port_ids;

    [[nodiscard]] std::string_view state_name() const noexcept {
        switch (access_state & 0x0F) {
            case 0x00: return "Active/Optimized (AO)";
            case 0x01: return "Active/Non-Optimized (ANO)";
            case 0x02: return "Standby (SB)";
            case 0x03: return "Unavailable (UN)";
            case 0x0E: return "Standby Offline";
            case 0x0F: return "Transitioning (TO)";
            default:   return "Reserved / Unknown";
        }
    }

    [[nodiscard]] std::string_view status_name() const noexcept {
        switch (status_code) {
            case 0x00: return "No status / Normal";
            case 0x01: return "Altered by SET TARGET PORT GROUPS";
            case 0x02: return "Altered by Target controller (Implicit)";
            default:   return "Vendor specific";
        }
    }
};

// Функція надсилання запиту RTPG та безпечного розбору дескрипторів
std::expected<std::vector<TargetPortGroup>, std::string> query_rtpg(const ScsiDevice& dev) {
    if (!dev.is_valid()) {
        return std::unexpected("Недійсний дескриптор пристрою");
    }

    constexpr size_t cdb_len = 16;
    constexpr size_t buf_size = 1024;
    constexpr size_t sense_size = 64;

    uint8_t cdb[cdb_len]{};
    cdb[0] = 0xA3; // MAINTENANCE IN
    cdb[1] = 0x0A; // Service Action: REPORT TARGET PORT GROUPS
    uint32_t alloc_len = htonl(static_cast<uint32_t>(buf_size));
    std::memcpy(&cdb[6], &alloc_len, sizeof(alloc_len));

    std::vector<uint8_t> resp_buf(buf_size, 0);
    uint8_t sense_buf[sense_size]{};

    sg_io_hdr io_hdr{};
    io_hdr.interface_id = 'S';
    io_hdr.cmdp = cdb;
    io_hdr.cmd_len = static_cast<unsigned char>(cdb_len);
    io_hdr.dxfer_direction = SG_DXFER_FROM_DEV;
    io_hdr.dxfer_len = static_cast<unsigned int>(resp_buf.size());
    io_hdr.dxferp = resp_buf.data();
    io_hdr.sbp = sense_buf;
    io_hdr.mx_sb_len = static_cast<unsigned char>(sense_size);
    io_hdr.timeout = 5000;

    if (::ioctl(dev.get_fd(), SG_IO, &io_hdr) < 0) {
        return std::unexpected(std::strerror(errno));
    }

    if (io_hdr.status != 0) {
        return std::unexpected(std::format("SCSI Check Condition: 0x{:02X}", io_hdr.status));
    }

    uint32_t data_len = (resp_buf[0] << 24) | (resp_buf[1] << 16) | (resp_buf[2] << 8) | resp_buf[3];
    std::span<const uint8_t> data(resp_buf.data(), std::min(static_cast<size_t>(4 + data_len), buf_size));

    std::vector<TargetPortGroup> groups;
    size_t offset = 4;

    while (offset + 8 <= data.size()) {
        TargetPortGroup group;
        uint8_t pref_state = data[offset];
        group.is_preferred = (pref_state & 0x80) != 0;
        group.access_state = pref_state & 0x0F;
        group.supported_mask = data[offset + 1];
        group.tpg_id = static_cast<uint16_t>((data[offset + 2] << 8) | data[offset + 3]);
        group.status_code = data[offset + 4];
        uint16_t port_count = static_cast<uint16_t>((data[offset + 6] << 8) | data[offset + 7]);

        offset += 8;
        for (uint16_t p = 0; p < port_count; ++p) {
            if (offset + 4 > data.size()) break;
            uint16_t port_id = static_cast<uint16_t>((data[offset + 2] << 8) | data[offset + 3]);
            group.relative_port_ids.push_back(port_id);
            offset += 4;
        }
        groups.push_back(std::move(group));
    }

    return groups;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << std::format("Використання: {} <шлях_до_пристрою_scsi>\n", argv[0]);
        return 1;
    }

    ScsiDevice dev(argv[1]);
    if (!dev.is_valid()) {
        std::cerr << std::format("Помилка відкриття {}: {}\n", argv[1], std::strerror(errno));
        return 1;
    }

    std::cout << std::format("Опитування дескрипторів ALUA для {}...\n\n", argv[1]);
    auto result = query_rtpg(dev);
    if (!result) {
        std::cerr << std::format("Помилка виконання RTPG: {}\n", result.error());
        return 1;
    }

    for (size_t i = 0; const auto& grp : *result) {
        std::cout << std::format("=== [Цільова група портів #{} (TPG ID: {} / 0x{:04X})] ===\n",
                                 i + 1, grp.tpg_id, grp.tpg_id);
        std::cout << std::format("  Стан доступу ALUA:    {}\n", grp.state_name());
        std::cout << std::format("  Бажана група (PREF):  {}\n", grp.is_preferred ? "ТАК (Preferred)" : "НІ");
        std::cout << std::format("  Маска підтримки:      0x{:02X}\n", grp.supported_mask);
        std::cout << std::format("  Статус зміни:         {}\n", grp.status_name());
        std::cout << std::format("  Кількість портів:     {}\n", grp.relative_port_ids.size());
        std::cout << "  Список портів цілі:\n";
        for (size_t p = 0; p < grp.relative_port_ids.size(); ++p) {
            std::cout << std::format("    - Порт #{} (Relative Target Port ID: {} / 0x{:04X})\n",
                                     p + 1, grp.relative_port_ids[p], grp.relative_port_ids[p]);
        }
        std::cout << "\n";
        ++i;
    }

    return 0;
}
```
:::

---

## Особливості реалізації мовами C та C++

Порівняння двох варіантів реалізації наочно демонструє переваги та відмінності між процедурним підходом C і сучасним об'єктно-орієнтованим C++23:

- **Керування ресурсами (RAII):** У варіанті C дескриптор файлу пристрою закривається вручну викликом `close(fd)` у кожній гілці завершення та при помилках. У C++ клас `ScsiDevice` інкапсулює дескриптор у деструкторі, унеможливлюючи витік ресурсів навіть при передчасному виході.
- **Безпека меж пам'яті:** У C побайтовий розбір здійснюється через явну арифметику вказівників і зміщень `offset += 4` з ручною перевіркою `offset + 8 <= total_limit`. У C++ застосовується обгортка `std::span<const uint8_t>`, яка створює безпечний інтерфейс перегляду виділеного буфера без додаткових копіювань пам'яті.
- **Обробка помилок без винятків:** Замість повернення негативних кодів помилок C++ використовує монадичний тип `std::expected<std::vector<TargetPortGroup>, std::string>`, що змушує викликача явно обробити як успішний вектор дескрипторів, так і деталізоване повідомлення про статус SCSI `CHECK CONDITION`.
- **Форматування виводу:** Замість застарілого `printf()` у C++ задіяно бібліотеку `std::format`, яка забезпечує строгу типізацію аргументів під час компіляції.

---

## Інструкція зі збирання та запуску

Для компіляції вихідних кодів у середовищі Linux скористайтеся компіляторами `gcc` або `g++`:

```sh
# Збирання версії мовою C
gcc -O2 -Wall -Wextra alua_rtpg.c -o alua_rtpg_c

# Збирання версії мовою C++ (потрібна підтримка стандарту C++23)
g++ -O2 -std=c++23 -Wall -Wextra alua_rtpg.cpp -o alua_rtpg_cpp
```

### Запуск програми та приклад виводу

Запустіть утиліту з правами `sudo`, вказавши шлях до одного з портів масиву:

```sh
$ sudo ./alua_rtpg_c /dev/sdb
Надсилання команди REPORT TARGET PORT GROUPS до /dev/sdb...
Отримано успішну відповідь. Довжина даних параметра: 36 байтів

=== [Цільова група портів #1 (TPG ID: 1 / 0x0001)] ===
  Стан доступу ALUA:    Active/Optimized (AO)
  Бажана група (PREF):  ТАК (Preferred)
  Маска підтримки:      0x8F (AO:1, ANO:1, SB:1, UN:1, TO:1)
  Статус зміни:         No status / Normal
  Кількість портів:     2
  Список портів цілі:
    - Порт #1 (Relative Target Port ID: 1 / 0x0001)
    - Порт #2 (Relative Target Port ID: 2 / 0x0002)

=== [Цільова група портів #2 (TPG ID: 2 / 0x0002)] ===
  Стан доступу ALUA:    Active/Non-Optimized (ANO)
  Бажана група (PREF):  НІ
  Маска підтримки:      0x8F (AO:1, ANO:1, SB:1, UN:1, TO:1)
  Статус зміни:         No status / Normal
  Кількість портів:     2
  Список портів цілі:
    - Порт #1 (Relative Target Port ID: 3 / 0x0003)
    - Порт #2 (Relative Target Port ID: 4 / 0x0004)
```

---

## Крайові випадки та обробка помилок

Під час практичного використання утиліти в реальних дата-центрах слід враховувати такі граничні стани дискових масивів:

1. **Опрацювання стану Transitioning:** Якщо утиліту запущено в момент аварійного перемикання або планової міграції контролера, команда поверне статус `CHECK CONDITION` із сенс-ключем `0x02` (*NOT READY*) та ASC/ASCQ `0x04/0x0A` (*Target Port in Rapid Transition*). Надійна програма моніторингу не повинна завершуватися з фатальною помилкою: вона фіксує сенс-код і робить експоненційну паузу (*exponential backoff* 200–500 мс) перед повторним викликом.
2. **Динамічне виділення буфера:** Якщо корпоративний дисковий масив має велику кількість портів (наприклад, 16 або 32 порти в одній групі), статичний буфер розміром 1024 байти може виявитися замалим. Реальне значення `data_len` у перших 4 байтах відповіді показує точний необхідний обсяг пам'яті. Якщо `data_len + 4 > RTPG_BUF_SIZE`, утиліта може перерозподілити буфер динамічно та надіслати повторний запит із точним значенням `ALLOCATION LENGTH`.
3. **Права доступу:** Якщо програму запущено з-під звичайного користувача, виклик `open()` поверне помилку `EACCES` (*Permission denied*), а виклик `ioctl()` завершиться кодом `EPERM`. Робота з сирими SCSI-командами завжди вимагає привілеїв суперкористувача.
