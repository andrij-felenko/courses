#include <iostream>
#include <fstream>
#include <cstdint>
#include <string>
#include <iomanip>
#include <system_error>

class PagemapReader {
public:
    explicit PagemapReader(pid_t pid) {
        path_ = "/proc/" + std::to_string(pid) + "/pagemap";
    }

    [[nodiscard]] uint64_t read_entry(uintptr_t virtual_address, size_t page_size = 4096) const {
        std::ifstream file(path_, std::ios::binary);
        if (!file.is_open()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити " + path_);
        }

        const auto offset = static_cast<std::streamoff>((virtual_address / page_size) * sizeof(uint64_t));
        file.seekg(offset);
        if (!file.good()) {
            throw std::runtime_error("Помилка позиціонування lseek у pagemap");
        }

        uint64_t entry{0};
        file.read(reinterpret_cast<char*>(&entry), sizeof(entry));
        if (file.gcount() != sizeof(entry)) {
            throw std::runtime_error("Не вдалося зчитати повний 64-бітний запис pagemap");
        }
        return entry;
    }

private:
    std::string path_;
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <pid> <hex_vaddr>\n";
        return 1;
    }

    try {
        const pid_t pid = std::stoi(argv[1]);
        const uintptr_t vaddr = std::stoull(argv[2], nullptr, 16);

        PagemapReader reader(pid);
        const uint64_t entry = reader.read_entry(vaddr);

        const bool present = ((entry >> 63) & 1) != 0;
        const bool swapped = ((entry >> 62) & 1) != 0;
        const uint64_t pfn = entry & ((1ULL << 55) - 1);

        std::cout << "=== Pagemap інспекція PID=" << pid << " Адреса=0x"
                  << std::hex << vaddr << std::dec << " ===\n";
        std::cout << "Присутня у RAM: " << (present ? "ТАК" : "НІ") << "\n";
        std::cout << "У свопі:        " << (swapped ? "ТАК" : "НІ") << "\n";
        if (present) {
            std::cout << "Фізичний PFN:   0x" << std::hex << pfn
                      << " (Фізична адреса: 0x" << (pfn * 4096) << ")" << std::dec << "\n";
        }

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
