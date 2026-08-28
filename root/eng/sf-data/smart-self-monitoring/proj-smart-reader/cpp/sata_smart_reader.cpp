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
