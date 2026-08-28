// ana_dump.cpp — ідіоматичний парсер NVMe ANA мовою C++20
#include <iostream>
#include <vector>
#include <string_view>
#include <memory>
#include <span>
#include <format>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

namespace nvme {

inline constexpr uint8_t LOG_ANA_LID = 0x0c;
inline constexpr size_t DEFAULT_BUFFER_SIZE = 4096;

struct [[gnu::packed]] AnaGroupDesc {
    uint32_t grpid;
    uint32_t nnsids;
    uint64_t chgcnt;
    uint8_t  state;
    uint8_t  rsvd17[15];
    uint32_t nsids[];
};

struct [[gnu::packed]] AnaLogHeader {
    uint64_t chgcnt;
    uint16_t ngrps;
    uint8_t  rsvd10[6];
};

constexpr std::string_view stateToString(uint8_t state) noexcept {
    switch (state & 0x0f) {
        case 0x01: return "OPTIMIZED (AO)";
        case 0x02: return "NON-OPTIMIZED (ANO)";
        case 0x03: return "INACCESSIBLE (AI)";
        case 0x04: return "PERSISTENT LOSS (PL)";
        case 0x0f: return "CHANGE STATE (TRANSITION)";
        default:   return "UNKNOWN";
    }
}

class Device {
    int fd_{-1};
public:
    explicit Device(std::string_view path) {
        fd_ = ::open(path.data(), O_RDONLY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити пристрій");
        }
    }

    ~Device() noexcept {
        if (fd_ >= 0) ::close(fd_);
    }

    Device(const Device&) = delete;
    Device& operator=(const Device&) = delete;

    [[nodiscard]] std::vector<uint8_t> fetchAnaLog(size_t bufferSize = DEFAULT_BUFFER_SIZE) const {
        std::vector<uint8_t> buffer(bufferSize, 0);
        const auto numd = static_cast<uint32_t>((buffer.size() / 4) - 1);

        nvme_passthru_cmd cmd{};
        cmd.opcode     = 0x02; // Get Log Page
        cmd.nsid       = 0xFFFFFFFF;
        cmd.addr       = reinterpret_cast<uintptr_t>(buffer.data());
        cmd.data_len   = static_cast<uint32_t>(buffer.size());
        cmd.cdw10      = ((numd & 0xFFFF) << 16) | LOG_ANA_LID;
        cmd.cdw11      = (numd >> 16) & 0xFFFF;
        cmd.timeout_ms = 5000;

        if (::ioctl(fd_, NVME_IOCTL_ADMIN_CMD, &cmd) < 0) {
            throw std::system_error(errno, std::generic_category(), "ioctl(NVME_IOCTL_ADMIN_CMD) зазнав невдачі");
        }

        return buffer;
    }
};

void parseAndPrint(std::span<const uint8_t> buffer, std::string_view devPath) {
    if (buffer.size() < sizeof(AnaLogHeader)) {
        std::cerr << "Буфер замалий для заголовка ANA\n";
        return;
    }

    const auto* header = reinterpret_cast<const AnaLogHeader*>(buffer.data());
    std::cout << std::format("=== ЖУРНАЛ СТАНІВ NVMe ANA ({}) ===\n", devPath);
    std::cout << std::format("Глобальний лічильник змін (Change Counter): {}\n", header->chgcnt);
    std::cout << std::format("Кількість груп ANA (Number of Groups):     {}\n\n", header->ngrps);

    size_t offset = sizeof(AnaLogHeader);
    for (uint16_t i = 0; i < header->ngrps; ++i) {
        if (offset + sizeof(AnaGroupDesc) > buffer.size()) {
            std::cerr << "Попередження: неочікуваний кінець буфера дескрипторів.\n";
            break;
        }

        const auto* desc = reinterpret_cast<const AnaGroupDesc*>(buffer.data() + offset);
        const size_t descSize = sizeof(AnaGroupDesc) + (desc->nnsids * sizeof(uint32_t));

        if (offset + descSize > buffer.size()) {
            std::cerr << std::format("Попередження: обрізаний дескриптор для групи {}.\n", desc->grpid);
            break;
        }

        std::cout << std::format("Група ANA ID: {}\n", desc->grpid);
        std::cout << std::format("  Стан маршруту:       {} (0x{:02X})\n", stateToString(desc->state), desc->state);
        std::cout << std::format("  Лічильник змін:      {}\n", desc->chgcnt);
        std::cout << std::format("  Кількість томів:     {}\n", desc->nnsids);
        std::cout << "  Прив'язані томи NSID: ";

        std::span<const uint32_t> nsids(desc->nsids, desc->nnsids);
        for (size_t n = 0; n < nsids.size(); ++n) {
            std::cout << nsids[n] << (n + 1 < nsids.size() ? ", " : "");
        }
        std::cout << "\n\n";

        offset += descSize;
    }
}

} // namespace nvme

int main(int argc, char* argv[]) {
    const std::string_view devPath = (argc > 1) ? argv[1] : "/dev/nvme0";
    try {
        const nvme::Device device(devPath);
        const auto buffer = device.fetchAnaLog();
        nvme::parseAndPrint(buffer, devPath);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
