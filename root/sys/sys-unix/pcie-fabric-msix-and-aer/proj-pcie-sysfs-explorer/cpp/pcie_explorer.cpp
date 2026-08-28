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
struct ConfigHeader {
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
static_assert(sizeof(ConfigHeader) == 64, "Заголовок PCI Header Type 0 має бути рівно 64 байти");

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
        uint8_t pos = cap_ptr & 0xFC;
        int guard = 48;   // запобіжник від зациклення списку можливостей
        std::cout << "    Capabilities list:";

        while (pos >= 0x40 && pos < 0xFF && guard-- > 0) {
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
