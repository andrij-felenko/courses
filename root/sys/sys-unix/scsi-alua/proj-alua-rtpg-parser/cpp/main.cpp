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
