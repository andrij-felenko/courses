// inspect_lsm.cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <cerrno>
#include <cstring>
#include <unistd.h>
#include <sys/syscall.h>
#include <expected>

#ifndef __NR_lsm_list_modules
#define __NR_lsm_list_modules 461
#endif

namespace sys::lsm {

// Запит активних модулів безпеки через новий системний виклик Linux 6.8+
std::expected<std::vector<std::uint64_t>, std::string> get_active_lsm_ids() {
    std::vector<std::uint64_t> ids(16);
    std::uint32_t size = static_cast<std::uint32_t>(ids.size() * sizeof(std::uint64_t));

    const long count = ::syscall(__NR_lsm_list_modules, ids.data(), &size, 0);
    if (count < 0) {
        if (errno == ENOSYS) {
            return std::unexpected("Системний виклик lsm_list_modules не підтримується цим ядром (< 6.8)");
        }
        return std::unexpected(std::string("Помилка lsm_list_modules: ") + std::strerror(errno));
    }

    ids.resize(static_cast<std::size_t>(count));
    return ids;
}

} // namespace sys::lsm

int main() {
    auto lsm_ids = sys::lsm::get_active_lsm_ids();
    if (!lsm_ids) {
        std::cerr << "Помилка: " << lsm_ids.error() << "\n";
        return 1;
    }

    std::cout << "Кількість активних модулів LSM у стеку: " << lsm_ids->size() << "\n";
    std::size_t idx = 0;
    for (const auto id : *lsm_ids) {
        std::cout << "  [" << idx++ << "] Module LSM ID: 0x" << std::hex << id << std::dec << "\n";
    }

    return 0;
}
