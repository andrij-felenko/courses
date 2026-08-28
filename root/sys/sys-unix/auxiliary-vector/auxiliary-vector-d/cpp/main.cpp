#include <iostream>
#include <iomanip>
#include <span>
#include <sys/auxv.h>

class AuxvInspector {
public:
    static void print_info() {
        const unsigned long page_size = ::getauxval(AT_PAGESZ);
        const unsigned long vdso_addr = ::getauxval(AT_SYSINFO_EHDR);
        const auto* random_bytes = reinterpret_cast<const std::uint8_t*>(::getauxval(AT_RANDOM));

        std::cout << "Розмір системної сторінки: " << page_size << " байтів\n"
                  << "Віртуальна адреса vDSO:    0x" << std::hex << vdso_addr << std::dec << "\n";

        if (random_bytes) {
            std::cout << "Випадкові байти (AT_RANDOM): ";
            for (std::size_t i = 0; i < 16; ++i) {
                std::cout << std::hex << std::setw(2) << std::setfill('0') 
                          << static_cast<int>(random_bytes[i]) << " ";
            }
            std::cout << std::dec << "\n";
        }
    }
};

int main() {
    AuxvInspector::print_info();
    return 0;
}
