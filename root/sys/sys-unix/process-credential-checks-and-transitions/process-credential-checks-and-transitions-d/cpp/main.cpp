#include <iostream>
#include <system_error>
#include <expected>
#include <unistd.h>
#include <sys/types.h>

struct ProcessUIDs {
    uid_t ruid;
    uid_t euid;
    uid_t suid;
};

// Отримання поточних UID через std::expected
[[nodiscard]] std::expected<ProcessUIDs, std::error_code> get_uids() noexcept {
    ProcessUIDs uids{};
    if (::getresuid(&uids.ruid, &uids.euid, &uids.suid) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return uids;
}

int main() {
    auto uids_res = get_uids();
    if (!uids_res) {
        std::cerr << "Помилка читання UID: " << uids_res.error().message() << '\n';
        return 1;
    }

    const auto& [ruid, euid, suid] = *uids_res;
    std::cout << "RUID: " << ruid << ", EUID: " << euid << ", SUID: " << suid << '\n';

    // Ідіоматична обробка привілеїв у C++
    if (euid == 0) {
        if (::seteuid(ruid) != 0) {
            std::cerr << "Скидання привілеїв не вдалося\n";
            return 1;
        }
        std::cout << "Привілеї тимчасово скинуто до RUID " << ruid << '\n';
    }

    return 0;
}
