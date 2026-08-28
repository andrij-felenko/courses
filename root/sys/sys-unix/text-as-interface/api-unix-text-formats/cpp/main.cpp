#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <pwd.h>
#include <mntent.h>

// Ідіоматична обгортка RAII для дескриптора mntent
class MountTableReader {
public:
    explicit MountTableReader(const char* path) 
        : fp_(setmntent(path, "r")) {}

    ~MountTableReader() {
        if (fp_) {
            endmntent(fp_);
        }
    }

    bool is_open() const noexcept { return fp_ != nullptr; }

    void print_fs_type(std::string_view target_type) {
        if (!fp_) return;
        struct mntent ent{};
        char buffer[4096];
        while (getmntent_r(fp_, &ent, buffer, sizeof(buffer)) != nullptr) {
            if (target_type == ent.mnt_type) {
                std::cout << "Пристрій: " << ent.mnt_fsname
                          << " -> Точка монтування: " << ent.mnt_dir << '\n';
            }
        }
    }

private:
    FILE* fp_{nullptr};
};

void print_regular_users_cpp() {
    setpwent();
    while (const auto* pw = getpwent()) {
        if (pw->pw_uid >= 1000) {
            std::cout << "Користувач: " << pw->pw_name 
                      << ", UID: " << pw->pw_uid 
                      << ", Оболонка: " << pw->pw_shell << '\n';
        }
    }
    endpwent();
}
