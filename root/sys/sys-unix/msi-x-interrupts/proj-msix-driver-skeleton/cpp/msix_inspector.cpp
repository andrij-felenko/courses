//
// msix_inspector.cpp — Перевірка векторів MSI-X та конфігурація SMP Affinity (C++20)
//

#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <vector>
#include <system_error>
#include <unistd.h>

namespace fs = std::filesystem;

class IrqManager {
public:
    explicit IrqManager(std::string pci_bdf)
        : bdf_(std::move(pci_bdf)),
          num_cpus_(static_cast<int>(sysconf(_SC_NPROCESSORS_ONLN))) {}

    void inspect_and_balance() {
        const fs::path msi_path = fs::path("/sys/bus/pci/devices") / bdf_ / "msi_irqs";

        std::error_code ec;
        if (!fs::exists(msi_path, ec) || !fs::is_directory(msi_path, ec)) {
            std::cerr << "Каталог " << msi_path << " не знайдено (пристрій не має MSI/MSI-X)\n";
            return;
        }

        std::cout << "Аналіз переривань для пристрою " << bdf_ << ":\n";
        int cpu_index = 0;

        for (const auto &entry : fs::directory_iterator(msi_path)) {
            if (!entry.is_regular_file()) {
                continue;
            }

            const std::string irq_num = entry.path().filename().string();
            std::ifstream type_file(entry.path());
            std::string irq_type;

            if (std::getline(type_file, irq_type)) {
                std::cout << "  • Знайдено вектор Linux IRQ " << irq_num
                          << " (тип: " << irq_type << ")\n";

                int target_cpu = cpu_index % num_cpus_;
                bind_affinity(irq_num, target_cpu);
                cpu_index++;
            }
        }
    }

private:
    void bind_affinity(const std::string &irq, int cpu_id) {
        const fs::path aff_path = fs::path("/proc/irq") / irq / "smp_affinity_list";
        std::ofstream aff_file(aff_path);

        if (!aff_file) {
            std::cerr << "Не вдалося відкрити " << aff_path << " для запису\n";
            return;
        }

        aff_file << cpu_id << "\n";
        if (aff_file.good()) {
            std::cout << "IRQ " << irq << " успішно прив'язано до CPU " << cpu_id << "\n";
        } else {
            std::cerr << "Помилка запису спорідненості для IRQ " << irq << "\n";
        }
    }

    std::string bdf_;
    int num_cpus_;
};

int main(int argc, char *argv[])
{
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <PCI BDF, наприклад 0000:01:00.0>\n";
        return 1;
    }

    IrqManager manager(argv[1]);
    manager.inspect_and_balance();

    return 0;
}
