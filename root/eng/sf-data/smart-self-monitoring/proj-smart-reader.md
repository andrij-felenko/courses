# ⚙️ Пряме опитування SMART: реалізація низькорівневого діагностичного клієнта на C та C++

Утиліти моніторингу високого рівня, такі як `smartctl`, приховують низькорівневі деталі спілкування з накопичувачем за сотнями тисяч рядків коду та базами даних виробників. Проте в задачах вбудованих систем, автономних легковагих демонів спостереження або високонавантажених сховищ виклик зовнішнього процесу `smartctl` створює неприйнятні накладні витрати на виділення пам'яті, форки процесів та парсинг текстового виводу.

Пряме опитування здоров'я накопичувача реалізується через надсилання спеціалізованих команд введення-виведення безпосередньо у вузол пристрою за допомогою системного виклику `ioctl`. Нижче наведено детальний розбір механіки прямого спілкування з накопичувачем та дві повноцінні реалізації на C та C++ для дисків SATA (через ATA PASS-THROUGH у підсистемі SCSI) та NVMe (через прямий інтерфейс Admin Queue).

---

## Механізм передачі команд через блоковий шар

Коли програма відкриває файл пристрою `/dev/sda` або `/dev/nvme0`, звичайні операції `read()` та `write()` спрямовуються у блоковий шар ядра, де вони розбиваються на запити `bio` та обробляються планувальником. Для діагностичних команд цей шлях непридатний: у них немає зміщення в просторі LBA.

Тому ядро надає два спеціалізовані наскрізні канали:

1. **Для SATA та SAS (`ioctl(SG_IO)`):** ядро упаковує інструкцію в командний блок SCSI (CDB) та виставляє тип операції `REQ_OP_DRV_IN`. Шар трансляції `libata` розгортає CDB і транслює регістри у фізичний кадр FIS для контролера AHCI. Відповідь контролера записується контролером через прямий доступ до пам'яті (DMA) безпосередньо у буфер процесу.
2. **Для NVMe (`ioctl(NVME_IOCTL_ADMIN_CMD)`):** запит оминає навіть шар SCSI. Драйвер `nvme` створює 64-байтовий командний запис в черзі `Admin Submission Queue` контролера на шині PCIe. Контролер повертає 512-байтову сторінку журналу телеметрії та генерує запис у черзі `Admin Completion Queue`.

---

## 1. Опитування SATA: ATA PASS-THROUGH (16) через SG_IO

Для дисків SATA команда `SMART READ DATA` (`0xB0` / `0xD0`) інкапсулюється в 16-байтовий командний блок SCSI (CDB) з кодом операції `0x85` (ATA PASS-THROUGH 16).

Зверніть увагу на конфігурацію службових байтів у структурі `sg_io_hdr`:
- `dxfer_direction = SG_DXFER_FROM_DEV`: вказує ядру, що напрямок передачі даних іде від накопичувача до хоста;
- `timeout = 5000`: обмежує максимальний час очікування відповіді 5 секундами. Якщо диск заклинило або він завис під час внутрішнього калібрування, драйвер не заблокує процес назавжди, а запустить процедуру скасування команди підсистеми SCSI;
- `sbp = sense_buf`: вказує буфер для прийому звіту про стан пристрою (*SCSI Sense Data*).

:::tabs
```c
/* sata_smart_reader.c — Пряме читання атрибутів SMART для SATA/ATA пристроїв */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <scsi/sg.h>

#define ATA_PASS_THROUGH_16 0x85
#define ATA_SMART_CMD       0xB0
#define ATA_SMART_READ_DATA 0xD0
#define SMART_LBA_MID       0x4F
#define SMART_LBA_HIGH      0xC2

#pragma pack(push, 1)
struct smart_attribute {
    uint8_t  id;
    uint16_t flags;
    uint8_t  current_value;
    uint8_t  worst_value;
    uint8_t  raw_bytes[6];
    uint8_t  reserved;
};

struct smart_data_sector {
    uint16_t               version;
    struct smart_attribute attributes[30];
    uint8_t                offline_data_collection_status;
    uint8_t                self_test_exec_status;
    uint16_t               offline_data_collection_time;
    uint8_t                vendor_specific_366;
    uint8_t                offline_data_collection_capability;
    uint16_t               smart_capability;
    uint8_t                error_logging_capability;
    uint8_t                vendor_specific_371;
    uint8_t                short_test_completion_time;
    uint8_t                extended_test_completion_time;
    uint8_t                conveyance_test_completion_time;
    uint16_t               extended_test_completion_time_ext;
    uint8_t                reserved[134];
    uint8_t                checksum;
};
#pragma pack(pop)

static uint64_t unpack_raw(const uint8_t raw[6]) {
    uint64_t val = 0;
    for (int i = 0; i < 6; ++i) {
        val |= ((uint64_t)raw[i]) << (i * 8);
    }
    return val;
}

static int read_sata_smart(const char *dev_path, struct smart_data_sector *out_data) {
    int fd = open(dev_path, O_RDONLY | O_NONBLOCK);
    if (fd < 0) {
        perror("Не вдалося відкрити пристрій");
        return -1;
    }

    uint8_t cdb[16];
    memset(cdb, 0, sizeof(cdb));
    cdb[0]  = ATA_PASS_THROUGH_16;
    /* [3:1] = 4 (PIO Data-In), [0] = 1 (T_DIR: від пристрою до хоста) */
    cdb[1]  = (4 << 1) | 1;
    /* [2] = 1 (T_LENGTH: довжина передається в Sector Count), [1:0] = 2 (у секторах) */
    cdb[2]  = (1 << 2) | 2;
    cdb[3]  = 0;                         /* Features (high) */
    cdb[4]  = ATA_SMART_READ_DATA;       /* Features (low) = D0h */
    cdb[5]  = 0;                         /* Sector Count (high) */
    cdb[6]  = 1;                         /* Sector Count (low) = 1 сектор (512B) */
    cdb[7]  = 0;                         /* LBA Low (high) */
    cdb[8]  = 0;                         /* LBA Low (low) */
    cdb[9]  = 0;                         /* LBA Mid (high) */
    cdb[10] = SMART_LBA_MID;             /* LBA Mid (low) = 4Fh */
    cdb[11] = 0;                         /* LBA High (high) */
    cdb[12] = SMART_LBA_HIGH;            /* LBA High (low) = C2h */
    cdb[13] = 0;                         /* Device register */
    cdb[14] = ATA_SMART_CMD;             /* Command register = B0h */

    uint8_t sense_buf[32];
    memset(sense_buf, 0, sizeof(sense_buf));

    struct sg_io_hdr io_hdr;
    memset(&io_hdr, 0, sizeof(io_hdr));
    io_hdr.interface_id    = 'S';
    io_hdr.cmd_len         = sizeof(cdb);
    io_hdr.mx_sb_len       = sizeof(sense_buf);
    io_hdr.dxfer_direction = SG_DXFER_FROM_DEV;
    io_hdr.dxfer_len       = sizeof(struct smart_data_sector);
    io_hdr.dxferp          = out_data;
    io_hdr.cmdp            = cdb;
    io_hdr.sbp             = sense_buf;
    io_hdr.timeout         = 5000; /* 5 секунд */

    int ret = ioctl(fd, SG_IO, &io_hdr);
    close(fd);

    if (ret < 0) {
        perror("Помилка виклику ioctl(SG_IO)");
        return -1;
    }

    if ((io_hdr.info & SG_INFO_OK_MASK) != SG_INFO_OK) {
        fprintf(stderr, "Помилка передачі SCSI/ATA: status=0x%02x, host_status=0x%02x\n",
                io_hdr.status, io_hdr.host_status);
        return -1;
    }

    /* Перевірка контрольної суми 512-байтового сектору */
    uint8_t sum = 0;
    const uint8_t *raw_ptr = (const uint8_t *)out_data;
    for (size_t i = 0; i < 512; ++i) {
        sum += raw_ptr[i];
    }
    if (sum != 0) {
        fprintf(stderr, "Попередження: контрольна сума сектору SMART не зійшлася (сума = 0x%02x)\n", sum);
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/sdX\n", argv[0]);
        return EXIT_FAILURE;
    }

    struct smart_data_sector data;
    memset(&data, 0, sizeof(data));

    if (read_sata_smart(argv[1], &data) != 0) {
        return EXIT_FAILURE;
    }

    printf("=== SMART Таблиця накопичувача %s (Версія 0x%04x) ===\n", argv[1], data.version);
    printf("%-4s %-28s %-7s %-7s %-16s %-8s\n",
           "ID", "Назва атрибута", "Value", "Worst", "RAW Value", "Тип");
    printf("----------------------------------------------------------------------------\n");

    for (int i = 0; i < 30; ++i) {
        const struct smart_attribute *attr = &data.attributes[i];
        if (attr->id == 0) continue;

        const char *name = "Unknown Attribute";
        switch (attr->id) {
            case 0x01: name = "Raw Read Error Rate"; break;
            case 0x05: name = "Reallocated Sectors Count"; break;
            case 0x09: name = "Power-On Hours"; break;
            case 0x0A: name = "Spin Retry Count"; break;
            case 0x0C: name = "Power Cycle Count"; break;
            case 0xB8: name = "End-to-End Error"; break;
            case 0xC5: name = "Current Pending Sector"; break;
            case 0xC6: name = "Offline Uncorrectable"; break;
            case 0xC7: name = "UDMA CRC Error Count"; break;
            case 0xE7: name = "SSD Life Left / Wear"; break;
            case 0xE8: name = "Available Reserved Space"; break;
            case 0xF1: name = "Total LBAs Written"; break;
            case 0xF2: name = "Total LBAs Read"; break;
        }

        const char *type_str = (attr->flags & 0x0001) ? "Pre-fail" : "Old-age";
        printf("0x%02X %-28s %-7u %-7u %-16lu %-8s\n",
               attr->id, name, attr->current_value, attr->worst_value,
               (unsigned long)unpack_raw(attr->raw_bytes), type_str);
    }

    return EXIT_SUCCESS;
}
```
```cpp
// sata_smart_reader.cpp — Ідіоматична C++ реалізація наскрізного читання SMART
#include <iostream>
#include <iomanip>
#include <vector>
#include <string_view>
#include <expected>
#include <system_error>
#include <span>
#include <memory>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <scsi/sg.h>

namespace storage::sata {

constexpr uint8_t ATA_PASS_THROUGH_16 = 0x85;
constexpr uint8_t ATA_SMART_CMD       = 0xB0;
constexpr uint8_t ATA_SMART_READ_DATA = 0xD0;
constexpr uint8_t SMART_LBA_MID       = 0x4F;
constexpr uint8_t SMART_LBA_HIGH      = 0xC2;

#pragma pack(push, 1)
struct RawAttribute {
    uint8_t  id;
    uint16_t flags;
    uint8_t  current_value;
    uint8_t  worst_value;
    uint8_t  raw_bytes[6];
    uint8_t  reserved;
};

struct SmartSector {
    uint16_t     version;
    RawAttribute attributes[30];
    uint8_t      reserved_vendor[149];
    uint8_t      checksum;
};
#pragma pack(pop)

struct AttributeInfo {
    uint8_t          id;
    std::string_view name;
    uint8_t          current_value;
    uint8_t          worst_value;
    uint64_t         raw_value;
    bool             is_pre_fail;
};

class FileDescriptor {
    int fd_ = -1;
public:
    explicit FileDescriptor(int fd) noexcept : fd_(fd) {}
    ~FileDescriptor() { if (fd_ >= 0) ::close(fd_); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

class SmartReader {
    static constexpr std::string_view resolve_name(uint8_t id) noexcept {
        switch (id) {
            case 0x01: return "Raw Read Error Rate";
            case 0x05: return "Reallocated Sectors Count";
            case 0x09: return "Power-On Hours";
            case 0x0A: return "Spin Retry Count";
            case 0x0C: return "Power Cycle Count";
            case 0xB8: return "End-to-End Error";
            case 0xC5: return "Current Pending Sector";
            case 0xC6: return "Offline Uncorrectable";
            case 0xC7: return "UDMA CRC Error Count";
            case 0xE7: return "SSD Life Left / Wear";
            case 0xE8: return "Available Reserved Space";
            case 0xF1: return "Total LBAs Written";
            case 0xF2: return "Total LBAs Read";
            default:   return "Vendor Specific Attribute";
        }
    }

    static uint64_t unpack_raw(std::span<const uint8_t, 6> raw) noexcept {
        uint64_t val = 0;
        for (size_t i = 0; i < 6; ++i) {
            val |= static_cast<uint64_t>(raw[i]) << (i * 8);
        }
        return val;
    }

public:
    static std::expected<std::vector<AttributeInfo>, std::error_code>
    read_attributes(std::string_view device_path) {
        int raw_fd = ::open(device_path.data(), O_RDONLY | O_NONBLOCK);
        if (raw_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        FileDescriptor fd(raw_fd);

        SmartSector sector_data{};
        uint8_t cdb[16]{};
        cdb[0]  = ATA_PASS_THROUGH_16;
        cdb[1]  = (4 << 1) | 1;           // PIO Data-In, From Dev
        cdb[2]  = (1 << 2) | 2;           // T_LENGTH in sectors
        cdb[4]  = ATA_SMART_READ_DATA;   // Features = D0h
        cdb[6]  = 1;                     // 1 sector
        cdb[10] = SMART_LBA_MID;         // 4Fh
        cdb[12] = SMART_LBA_HIGH;        // C2h
        cdb[14] = ATA_SMART_CMD;         // B0h

        uint8_t sense_buf[32]{};
        sg_io_hdr io_hdr{};
        io_hdr.interface_id    = 'S';
        io_hdr.cmd_len         = sizeof(cdb);
        io_hdr.mx_sb_len       = sizeof(sense_buf);
        io_hdr.dxfer_direction = SG_DXFER_FROM_DEV;
        io_hdr.dxfer_len       = sizeof(sector_data);
        io_hdr.dxferp          = &sector_data;
        io_hdr.cmdp            = cdb;
        io_hdr.sbp             = sense_buf;
        io_hdr.timeout         = 5000;

        if (::ioctl(fd.get(), SG_IO, &io_hdr) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if ((io_hdr.info & SG_INFO_OK_MASK) != SG_INFO_OK) {
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }

        std::vector<AttributeInfo> result;
        result.reserve(30);

        for (const auto &raw_attr : sector_data.attributes) {
            if (raw_attr.id == 0) continue;

            result.push_back(AttributeInfo{
                .id            = raw_attr.id,
                .name          = resolve_name(raw_attr.id),
                .current_value = raw_attr.current_value,
                .worst_value   = raw_attr.worst_value,
                .raw_value     = unpack_raw(std::span<const uint8_t, 6>(raw_attr.raw_bytes, 6)),
                .is_pre_fail   = (raw_attr.flags & 0x0001) != 0
            });
        }

        return result;
    }
};

} // namespace storage::sata

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " /dev/sdX\n";
        return EXIT_FAILURE;
    }

    auto res = storage::sata::SmartReader::read_attributes(argv[1]);
    if (!res) {
        std::cerr << "Помилка читання SMART: " << res.error().message() << "\n";
        return EXIT_FAILURE;
    }

    std::cout << "=== SMART Таблиця накопичувача " << argv[1] << " ===\n";
    std::cout << std::left << std::setw(6)  << "ID"
              << std::setw(30) << "Назва атрибута"
              << std::setw(8)  << "Value"
              << std::setw(8)  << "Worst"
              << std::setw(18) << "RAW Value"
              << std::setw(10) << "Тип" << "\n";
    std::cout << std::string(80, '-') << "\n";

    for (const auto &attr : *res) {
        std::cout << "0x" << std::hex << std::uppercase << std::setw(2) << std::setfill('0')
                  << static_cast<int>(attr.id) << std::dec << std::setfill(' ') << "  "
                  << std::setw(28) << attr.name
                  << std::setw(8)  << static_cast<int>(attr.current_value)
                  << std::setw(8)  << static_cast<int>(attr.worst_value)
                  << std::setw(18) << attr.raw_value
                  << (attr.is_pre_fail ? "Pre-fail" : "Old-age") << "\n";
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 2. Опитування NVMe: Команда Get Log Page через NVME_IOCTL_ADMIN_CMD

Для накопичувачів NVMe зв'язок реалізується через пряме надсилання команди в чергу адміністрування контролера за допомогою `ioctl(fd, NVME_IOCTL_ADMIN_CMD)`. Тут не використовується трансляція SCSI/ATA: запит одразу формує нативний командний запис NVMe.

Командне слово `cdw10` конструюється об'єднанням номера журналу (`0x02`) у молодших 8 бітах та кількості 32-бітних слів мінус одне (`127` для 512-байтової сторінки) у бітах `[27:16]`:

```
cdw10 = Log_ID | (Num_Dwords_Minus_One << 16)
      = 0x02   | (127 << 16)
      = 0x007F0002
```

:::tabs
```c
/* nvme_health_reader.c — Пряме читання NVMe Health Information Log */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

#pragma pack(push, 1)
struct nvme_smart_log {
    uint8_t  critical_warning;
    uint16_t temperature;                  /* у Кельвінах */
    uint8_t  avail_spare;                  /* відсотки */
    uint8_t  spare_thresh;
    uint8_t  percent_used;
    uint8_t  endu_grp_crit_warn_sumry;
    uint8_t  rsvd6[25];
    uint8_t  data_units_read[16];          /* 128-біт */
    uint8_t  data_units_written[16];       /* 128-біт */
    uint8_t  host_reads[16];
    uint8_t  host_writes[16];
    uint8_t  ctrl_busy_time[16];
    uint8_t  power_cycles[16];
    uint8_t  power_on_hours[16];
    uint8_t  unsafe_shutdowns[16];
    uint8_t  media_errors[16];
    uint8_t  num_err_log_entries[16];
    uint32_t warning_temp_time;
    uint32_t critical_comp_time;
    uint16_t temp_sensor[8];
    uint32_t thm_temp1_trans_count;
    uint32_t thm_temp2_trans_count;
    uint32_t thm_temp1_total_time;
    uint32_t thm_temp2_total_time;
    uint8_t  rsvd232[280];
};
#pragma pack(pop)

static uint64_t unpack_u128_low(const uint8_t buf[16]) {
    uint64_t val = 0;
    for (int i = 0; i < 8; ++i) {
        val |= ((uint64_t)buf[i]) << (i * 8);
    }
    return val;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s /dev/nvme0\n", argv[0]);
        return EXIT_FAILURE;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити NVMe контролер");
        return EXIT_FAILURE;
    }

    struct nvme_smart_log log_data;
    memset(&log_data, 0, sizeof(log_data));

    struct nvme_admin_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));
    cmd.opcode    = 0x02;        /* Get Log Page */
    cmd.nsid      = 0xFFFFFFFF;  /* Global Controller Log */
    cmd.addr      = (uint64_t)(uintptr_t)&log_data;
    cmd.data_len  = sizeof(log_data);
    /* cdw10: [7:0] = Log ID (0x02), [27:16] = Number of Dwords Lower (127 for 512 bytes) */
    cmd.cdw10     = 0x02 | (127 << 16);

    if (ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
        perror("Помилка виклику ioctl(NVME_IOCTL_ADMIN_CMD)");
        close(fd);
        return EXIT_FAILURE;
    }
    close(fd);

    double temp_c = (double)log_data.temperature - 273.15;
    printf("=== Звіт здоров'я NVMe (%s) ===\n", argv[1]);
    printf("Критичні попередження (Critical Warning): 0x%02X\n", log_data.critical_warning);
    if (log_data.critical_warning & (1 << 0)) printf("  [!] Запасні блоки (Available Spare) нижче порогу!\n");
    if (log_data.critical_warning & (1 << 1)) printf("  [!] Перевищено температурний поріг!\n");
    if (log_data.critical_warning & (1 << 2)) printf("  [!] Надійність підсистеми NVM катастрофічно деградувала!\n");
    if (log_data.critical_warning & (1 << 3)) printf("  [!] Носій переведено в режим ТІЛЬКИ ДЛЯ ЧИТАННЯ (Read Only)!\n");
    if (log_data.critical_warning & (1 << 4)) printf("  [!] Збій пристрою резервного живлення кешу!\n");

    printf("Температура: %.1f °C (%u K)\n", temp_c, log_data.temperature);
    printf("Залишок резерву (Available Spare): %u%% (Поріг: %u%%)\n",
           log_data.avail_spare, log_data.spare_thresh);
    printf("Використано ресурсу (Percentage Used): %u%%\n", log_data.percent_used);

    /* 1 data unit = 1000 секторів по 512 байтів = 500 КБ */
    uint64_t units_written = unpack_u128_low(log_data.data_units_written);
    uint64_t units_read = unpack_u128_low(log_data.data_units_read);
    printf("Записано даних: %lu ГБ\n", (unsigned long)(units_written * 512000 / (1024 * 1024 * 1024)));
    printf("Прочитано даних: %lu ГБ\n", (unsigned long)(units_read * 512000 / (1024 * 1024 * 1024)));
    printf("Помилки носія (Media Errors): %lu\n", (unsigned long)unpack_u128_low(log_data.media_errors));
    printf("Аварійні вимкнення (Unsafe Shutdowns): %lu\n", (unsigned long)unpack_u128_low(log_data.unsafe_shutdowns));
    printf("Години роботи під напругою: %lu год\n", (unsigned long)unpack_u128_low(log_data.power_on_hours));

    return EXIT_SUCCESS;
}
```
```cpp
// nvme_health_reader.cpp — Ідіоматична C++ реалізація зчитування NVMe Health Log
#include <iostream>
#include <iomanip>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

namespace storage::nvme {

#pragma pack(push, 1)
struct SmartLogPage {
    uint8_t  critical_warning;
    uint16_t temperature;
    uint8_t  avail_spare;
    uint8_t  spare_thresh;
    uint8_t  percent_used;
    uint8_t  endu_grp_crit_warn_sumry;
    uint8_t  rsvd6[25];
    uint8_t  data_units_read[16];
    uint8_t  data_units_written[16];
    uint8_t  host_reads[16];
    uint8_t  host_writes[16];
    uint8_t  ctrl_busy_time[16];
    uint8_t  power_cycles[16];
    uint8_t  power_on_hours[16];
    uint8_t  unsafe_shutdowns[16];
    uint8_t  media_errors[16];
    uint8_t  num_err_log_entries[16];
    uint32_t warning_temp_time;
    uint32_t critical_comp_time;
    uint16_t temp_sensor[8];
    uint8_t  rsvd232[280];
};
#pragma pack(pop)

struct HealthReport {
    uint8_t  critical_warning_raw;
    bool     spare_below_threshold;
    bool     temperature_exceeded;
    bool     reliability_degraded;
    bool     read_only_mode;
    bool     backup_device_failed;
    double   temperature_celsius;
    uint8_t  available_spare_pct;
    uint8_t  spare_threshold_pct;
    uint8_t  percentage_used_pct;
    uint64_t data_units_written_gb;
    uint64_t data_units_read_gb;
    uint64_t media_integrity_errors;
    uint64_t unsafe_shutdowns;
    uint64_t power_on_hours;
};

class NvmeHealthScanner {
    static uint64_t unpack_u128_low(const uint8_t buf[16]) noexcept {
        uint64_t val = 0;
        for (int i = 0; i < 8; ++i) {
            val |= static_cast<uint64_t>(buf[i]) << (i * 8);
        }
        return val;
    }

public:
    static std::expected<HealthReport, std::error_code>
    query_controller(std::string_view controller_path) {
        int fd = ::open(controller_path.data(), O_RDONLY);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        SmartLogPage log{};
        nvme_admin_cmd cmd{};
        cmd.opcode   = 0x02;        // Get Log Page
        cmd.nsid     = 0xFFFFFFFF;  // Global Controller
        cmd.addr     = reinterpret_cast<uint64_t>(&log);
        cmd.data_len = sizeof(log);
        cmd.cdw10    = 0x02 | (127 << 16); // Log ID 0x02, 127 dwords

        int ioctl_res = ::ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd);
        ::close(fd);

        if (ioctl_res < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        uint64_t wr_units = unpack_u128_low(log.data_units_written);
        uint64_t rd_units = unpack_u128_low(log.data_units_read);

        return HealthReport{
            .critical_warning_raw   = log.critical_warning,
            .spare_below_threshold  = (log.critical_warning & (1 << 0)) != 0,
            .temperature_exceeded   = (log.critical_warning & (1 << 1)) != 0,
            .reliability_degraded   = (log.critical_warning & (1 << 2)) != 0,
            .read_only_mode         = (log.critical_warning & (1 << 3)) != 0,
            .backup_device_failed   = (log.critical_warning & (1 << 4)) != 0,
            .temperature_celsius    = static_cast<double>(log.temperature) - 273.15,
            .available_spare_pct    = log.avail_spare,
            .spare_threshold_pct    = log.spare_thresh,
            .percentage_used_pct    = log.percent_used,
            .data_units_written_gb  = (wr_units * 512000) / (1024 * 1024 * 1024),
            .data_units_read_gb     = (rd_units * 512000) / (1024 * 1024 * 1024),
            .media_integrity_errors = unpack_u128_low(log.media_errors),
            .unsafe_shutdowns       = unpack_u128_low(log.unsafe_shutdowns),
            .power_on_hours         = unpack_u128_low(log.power_on_hours)
        };
    }
};

} // namespace storage::nvme

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " /dev/nvme0\n";
        return EXIT_FAILURE;
    }

    auto report = storage::nvme::NvmeHealthScanner::query_controller(argv[1]);
    if (!report) {
        std::cerr << "Помилка опитування контролера: " << report.error().message() << "\n";
        return EXIT_FAILURE;
    }

    std::cout << "=== Стан здоров'я NVMe пристрою " << argv[1] << " ===\n";
    std::cout << "Температура:             " << std::fixed << std::setprecision(1)
              << report->temperature_celsius << " °C\n";
    std::cout << "Залишок резерву (Spare): " << static_cast<int>(report->available_spare_pct)
              << "% (Поріг: " << static_cast<int>(report->spare_threshold_pct) << "%)\n";
    std::cout << "Знос ресурсу (Used):     " << static_cast<int>(report->percentage_used_pct) << "%\n";
    std::cout << "Записано даних:          " << report->data_units_written_gb << " ГБ\n";
    std::cout << "Прочитано даних:         " << report->data_units_read_gb << " ГБ\n";
    std::cout << "Помилки медіа/ECC:       " << report->media_integrity_errors << "\n";
    std::cout << "Аварійні вимкнення:      " << report->unsafe_shutdowns << "\n";
    std::cout << "Години роботи:           " << report->power_on_hours << " год\n";

    if (report->critical_warning_raw != 0) {
        std::cout << "\n[!] КРИТИЧНІ ПОПЕРЕДЖЕННЯ:\n";
        if (report->spare_below_threshold) std::cout << "  - Резервні блоки вичерпано!\n";
        if (report->temperature_exceeded)  std::cout << "  - Критичний перегрів пристрою!\n";
        if (report->reliability_degraded)  std::cout << "  - Надійність масиву деградувала!\n";
        if (report->read_only_mode)        std::cout << "  - Диск заблоковано в режимі Read-Only!\n";
        if (report->backup_device_failed)  std::cout << "  - Відмовила батарея/конденсатор кешу!\n";
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Трасування та перевірка наскрізних запитів у ядрі

Під час розробки або налагодження низькорівневих діагностичних клієнтів важливо переконатися, що надіслані кадри коректно досягають апаратного контролера, а повернені байти не спотворюються проміжними рівнями трансляції.

Для перевірки проходження наскрізних команд у Linux використовуються точки трасування ядра (*tracepoints*):

```bash
# Трасування наскрізних команд підсистеми SCSI / libata
trace-cmd record -e scsi:scsi_dispatch_cmd_start -e scsi:scsi_dispatch_cmd_done
trace-cmd report

# Трасування команд черги адміністрування NVMe
trace-cmd record -e nvme:nvme_setup_admin_cmd -e nvme:nvme_complete_rq
trace-cmd report
```

У звіті трасування SCSI чітко видно відправку 16-байтового CDB з опкодом `0x85` та повернення статусу `SAM_STAT_GOOD` (`0x00`). Для NVMe утиліта покаже виставлення команди `Opcode 0x02` у чергу `admin-sq` та отримання результату через апаратне переривання.

---

## 4. Підводні камені та пастки при прямому опитуванні

1. **Привілеї доступу (Capabilities):** Обидва системні виклики вимагають привілею `CAP_SYS_RAWIO` або `CAP_SYS_ADMIN`. Без відповідних прав виклик завершується з помилкою `EPERM` (*Operation not permitted*).
2. **Диски в режимі сну (Standby spin-down):** Надіслана команда `SMART READ DATA` змушує шпиндель магнітного диска розкрутитися, що збільшує лічильник стартів і додає затримку до 5–10 секунд. Якщо мета — лише перевірити статус без пробудження, слід надсилати перевірку стану живлення через `CHECK POWER MODE` (`0xE5`) перед діагностикою.
3. **Вирівнювання буфера пам'яті (Memory Alignment):** Під час прямих DMA-передач від контролера деякі шинні адаптери повертають помилку `EINVAL`, якщо адреса буфера в пам'яті процесу не вирівняна на межу апаратного сектора (512 або 4096 байтів). У промисловому коді пам'ять під структури телеметрії виділяють через `posix_memalign()` або C++17 `std::aligned_alloc()`.
4. **Порядок байтів (Endianness):** Усі структури протоколів ATA та NVMe використовують порядок байтів Little-Endian. На архітектурах із порядком Big-Endian (наприклад, IBM s390x, PowerPC) усі зчитані 16-, 32- та 64-бітні цілі числа необхідно явно конвертувати макросами `le16toh()`, `le32toh()`, `le64toh()` із заголовного файлу `<endian.h>`.
5. **Апаратні RAID-контролери:** Якщо диски підключені до апаратного масиву (наприклад, LSI MegaRAID, HP Smart Array), надсилання `SG_IO` у вузол `/dev/sda` опитає віртуальний логічний том (LUN), який поверне фіктивні дані. Для доступу до реальних фізичних дисків запит необхідно направляти у керівний символьний файл контролера (наприклад, `/dev/megaraid_sas_ioctl_node`), обгортаючи команду в фірмовий заголовок Pass-Through відповідного драйвера.
