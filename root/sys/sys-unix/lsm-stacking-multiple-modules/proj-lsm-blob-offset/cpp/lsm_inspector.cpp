// lsm_inspector.cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <string_view>
#include <cstdint>
#include <cerrno>
#include <cstring>
#include <unistd.h>
#include <sys/syscall.h>
#include <expected>

#ifndef __NR_lsm_list_modules
#define __NR_lsm_list_modules 461
#endif

namespace lsm {

// Безпечне зчитування конфігурації sysfs за допомогою C++ iostreams та RAII
std::expected<std::string, std::string> read_sysfs_active_lsms() {
    std::ifstream file("/sys/kernel/security/lsm");
    if (!file.is_open()) {
        return std::unexpected("Не вдалося відкрити /sys/kernel/security/lsm (перевірте наявність securityfs)");
    }
    std::string line;
    if (std::getline(file, line)) {
        return line;
    }
    return std::unexpected("Файл /sys/kernel/security/lsm порожній");
}

// Прямий виклик lsm_list_modules із поверненням типу std::expected (C++23)
std::expected<std::vector<std::uint64_t>, std::string> query_lsm_ids_syscall() {
    std::vector<std::uint64_t> ids(16);
    std::uint32_t size = static_cast<std::uint32_t>(ids.size() * sizeof(std::uint64_t));

    const long ret = ::syscall(__NR_lsm_list_modules, ids.data(), &size, 0);
    if (ret < 0) {
        if (errno == ENOSYS) {
            return std::unexpected("Системний виклик lsm_list_modules відсутній (потрібне ядро Linux >= 6.8)");
        }
        return std::unexpected(std::string("Помилка виконання lsm_list_modules: ") + std::strerror(errno));
    }

    ids.resize(static_cast<std::size_t>(ret));
    return ids;
}

} // namespace lsm

int main() {
    std::cout << "=== Інспектор стеку Linux Security Modules (C++23 UAPI) ===\n";

    // 1. Перевірка sysfs
    if (auto sysfs_res = lsm::read_sysfs_active_lsms(); sysfs_res.has_value()) {
        std::cout << "[sysfs] Активні модулі LSM (порядок виконання): " << *sysfs_res << "\n";
    } else {
        std::cerr << "[sysfs помилка] " << sysfs_res.error() << "\n";
    }

    // 2. Перевірка системного виклику
    if (auto ids_res = lsm::query_lsm_ids_syscall(); ids_res.has_value()) {
        std::cout << "[syscall] Виявлено " << ids_res->size() << " активних модулів у стеку (ID):\n";
        std::size_t idx = 0;
        for (const auto id : *ids_res) {
            std::cout << "  - Module [" << idx++ << "]: ID 0x" << std::hex << id << std::dec << "\n";
        }
    } else {
        std::cerr << "[syscall помилка] " << ids_res.error() << "\n";
    }

    return 0;
}
