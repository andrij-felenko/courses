#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <string_view>
#include <system_error>
#include <format>

namespace fs = std::filesystem;

class SriovManager {
public:
    explicit SriovManager(std::string_view pf_bdf)
        : pf_path_(fs::path("/sys/bus/pci/devices") / pf_bdf) {
        if (!fs::exists(pf_path_)) {
            throw std::invalid_argument(
                std::format("PCI пристрій {} не знайдено у sysfs", pf_bdf)
            );
        }
    }

    // RAII-безпечний запис у файли sysfs
    void write_sysfs(const fs::path& rel_path, std::string_view value) const {
        fs::path full_path = pf_path_ / rel_path;
        std::ofstream ofs(full_path);
        if (!ofs.is_open()) {
            throw std::system_error(
                make_error_code(std::errc::no_such_file_or_directory),
                std::format("Не вдалося відкрити sysfs файл: {}", full_path.string())
            );
        }
        ofs << value;
        if (!ofs.good()) {
            throw std::system_error(
                make_error_code(std::errc::io_error),
                std::format("Помилка запису '{}' у {}", value, full_path.string())
            );
        }
    }

    void configure_vfs(size_t num_vfs) const {
        std::cout << std::format("[+] Конфігурація {} VF для PF: {}\n", num_vfs, pf_path_.filename().string());

        // 1. Вимикаємо autoprobe хоста, щоб нові VF не захоплювалися мережевим стеком
        try {
            write_sysfs("sriov_drivers_autoprobe", "0");
        } catch (const std::exception& e) {
            std::cerr << std::format("[!] Попередження: {}\n", e.what());
        }

        // 2. Скидаємо поточний стан VF
        write_sysfs("sriov_numvfs", "0");

        // 3. Записуємо бажану кількість віртуальних функцій
        write_sysfs("sriov_numvfs", std::to_string(num_vfs));

        std::cout << std::format("[+] Успішно згенеровано {} VF у системі.\n", num_vfs);
    }

    void inspect_vf_iommu_groups() const {
        for (const auto& entry : fs::directory_iterator(pf_path_)) {
            std::string filename = entry.path().filename().string();
            if (filename.starts_with("virtfn")) {
                fs::path vf_target = fs::read_symlink(entry.path());
                fs::path vf_bdf = vf_target.filename();
                fs::path iommu_group_path = entry.path() / "iommu_group";

                if (fs::exists(iommu_group_path)) {
                    fs::path group_target = fs::read_symlink(iommu_group_path);
                    std::cout << std::format("  └─ VF [{}] ({}) → IOMMU Group: {} (/dev/vfio/{})\n", 
                                             filename, vf_bdf.string(), 
                                             group_target.filename().string(),
                                             group_target.filename().string());
                }
            }
        }
    }

private:
    fs::path pf_path_;
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << std::format("Використання: {} <PF_BDF> <NUM_VFS>\n", argv[0]);
        return EXIT_FAILURE;
    }

    try {
        std::string_view pf_bdf = argv[1];
        size_t num_vfs = std::stoul(argv[2]);

        SriovManager manager(pf_bdf);
        manager.configure_vfs(num_vfs);
        manager.inspect_vf_iommu_groups();

    } catch (const std::exception& ex) {
        std::cerr << std::format("[-] Фатальна помилка: {}\n", ex.what());
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
