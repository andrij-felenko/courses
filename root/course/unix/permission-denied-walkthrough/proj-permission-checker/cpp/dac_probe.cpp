// dac_probe.cpp — Покроковий симулятор перевірки прав VFS ядра Linux на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <algorithm>
#include <format>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/statvfs.h>

namespace fs = std::filesystem;

struct ProcessIdentity {
    uid_t fsuid{};
    gid_t fsgid{};
    std::vector<gid_t> groups;

    static ProcessIdentity current() {
        ProcessIdentity pid;
        uid_t ruid, suid;
        gid_t rgid, sgid;
        if (getresuid(&ruid, &pid.fsuid, &suid) != 0 ||
            getresgid(&rgid, &pid.fsgid, &sgid) != 0) {
            throw std::system_error(errno, std::generic_category(), "getresuid/getresgid");
        }

        int count = getgroups(0, nullptr);
        if (count > 0) {
            pid.groups.resize(count);
            if (getgroups(count, pid.groups.data()) < 0) {
                pid.groups.clear();
            }
        }
        return pid;
    }

    [[nodiscard]] bool in_group(gid_t gid) const noexcept {
        if (fsgid == gid) return true;
        return std::ranges::find(groups, gid) != groups.end();
    }
};

struct AccessRequest {
    bool read{false};
    bool write{false};
    bool exec{false};
};

struct DACResult {
    bool allowed{false};
    std::string_view matched_class;
};

DACResult evaluate_dac(const ProcessIdentity& cred, const struct stat& st, AccessRequest req) {
    const mode_t m = st.st_mode;

    if (cred.fsuid == st.st_uid) {
        const bool ok = (!req.read || (m & S_IRUSR)) &&
                        (!req.write || (m & S_IWUSR)) &&
                        (!req.exec || (m & S_IXUSR));
        return {ok, "ВЛАСНИК (Owner)"};
    }

    if (cred.in_group(st.st_gid)) {
        const bool ok = (!req.read || (m & S_IRGRP)) &&
                        (!req.write || (m & S_IWGRP)) &&
                        (!req.exec || (m & S_IXGRP));
        return {ok, "ГРУПА (Group)"};
    }

    const bool ok = (!req.read || (m & S_IROTH)) &&
                    (!req.write || (m & S_IWOTH)) &&
                    (!req.exec || (m & S_IXOTH));
    return {ok, "РЕШТА (Others)"};
}

void run_diagnostics(const fs::path& target, AccessRequest req) {
    const auto cred = ProcessIdentity::current();

    std::cout << "========================================================\n"
              << "ДІАГНОСТИКА ДОСТУПУ ДО: " << target << "\n"
              << "Ідентичність: fsuid=" << cred.fsuid << ", fsgid=" << cred.fsgid
              << ", додаткових груп=" << cred.groups.size() << "\n"
              << "Запит: Read=" << req.read << ", Write=" << req.write << ", Exec/Search=" << req.exec << "\n"
              << "========================================================\n\n";

    struct statvfs vfs{};
    if (statvfs(target.c_str(), &vfs) == 0 && (vfs.f_flag & ST_RDONLY) && req.write) {
        std::cout << "[ПОПЕРЕДЖЕННЯ] Точка монтування перебуває в режимі READ-ONLY (EROFS)!\n\n";
    }

    fs::path absolute_path = fs::absolute(target);
    std::cout << "ФАЗА 1: Покомпонентний обхід шляху (link_path_walk):\n";

    fs::path current_acc;
    int step = 0;
    bool traversal_ok = true;

    auto parent_path = absolute_path.parent_path();
    for (const auto& part : parent_path) {
        current_acc /= part;
        if (current_acc.empty()) current_acc = "/";

        struct stat st{};
        if (stat(current_acc.c_str(), &st) != 0) {
            std::cout << "  [" << step << "] Каталог '" << current_acc.string() << "' -> НЕ ЗНАЙДЕНО\n";
            traversal_ok = false;
            break;
        }

        auto [can_search, mclass] = evaluate_dac(cred, st, {.exec = true});
        std::cout << "  [" << step << "] Каталог '" << current_acc.string()
                  << "' (mode=" << std::oct << (st.st_mode & 07777) << std::dec
                  << ", uid=" << st.st_uid << ", gid=" << st.st_gid << ")\n"
                  << "      Клас: " << mclass << " -> Пошук (+x): "
                  << (can_search ? "ДОЗВОЛЕНО" : "ВІДМОВА [EACCES]") << "\n";

        if (!can_search) {
            std::cout << "\n>>> КРИТИЧНА ПОМИЛКА: Ядро перериває обхід на каталозі '"
                      << current_acc.string() << "'!\n"
                      << ">>> Причина: брак біта +x у класі '" << mclass << "'.\n";
            traversal_ok = false;
            break;
        }
        step++;
    }

    if (!traversal_ok) return;

    std::cout << "\nФАЗА 2: Перевірка прав цільового об'єкта:\n";
    struct stat target_st{};
    if (stat(absolute_path.c_str(), &target_st) != 0) {
        if (errno == ENOENT) {
            std::cout << "  Файл '" << absolute_path.string() << "' ще не існує.\n";
            if (req.write) {
                std::cout << "  Для створення потрібні права на запис (+w) у батьківському каталозі.\n";
            }
        } else {
            std::cout << "  Помилка stat: " << std::generic_category().message(errno) << "\n";
        }
        return;
    }

    auto [allowed, target_class] = evaluate_dac(cred, target_st, req);
    std::cout << "  Цільовий об'єкт: '" << absolute_path.string() << "'\n"
              << "  Режим: " << std::oct << (target_st.st_mode & 07777) << std::dec
              << ", Власник: " << target_st.st_uid << ":" << target_st.st_gid << "\n"
              << "  Збіг класу: " << target_class << "\n"
              << "  Результат DAC: " << (allowed ? "ДОСТУП ДОЗВОЛЕНО" : "ВІДМОВА [EACCES]") << "\n\n";

    if (!allowed) {
        std::cout << ">>> ПРИЧИНА ВІДМОВИ:\n"
                  << ">>> Запит не задовольняється правами у класі '" << target_class << "'.\n"
                  << ">>> Зверніть увагу: клас обирається один раз і остаточно!\n";
    }
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях> [r] [w] [x]\n";
        return 1;
    }

    AccessRequest req{.read = true};
    if (argc > 2) {
        req.read = req.write = req.exec = false;
        for (int i = 2; i < argc; ++i) {
            std::string_view arg = argv[i];
            if (arg.find('r') != std::string_view::npos) req.read = true;
            if (arg.find('w') != std::string_view::npos) req.write = true;
            if (arg.find('x') != std::string_view::npos) req.exec = true;
        }
    }

    try {
        run_diagnostics(argv[1], req);
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
