#include <sys/random.h>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <span>
#include <system_error>

namespace crypto {

[[nodiscard]] bool get_random_key(std::span<std::byte> out) noexcept {
    ssize_t ret = ::getrandom(out.data(), out.size(), 0);
    return ret == static_cast<ssize_t>(out.size());
}

} // namespace crypto

int main() {
    std::array<std::byte, 32> key{};
    if (!crypto::get_random_key(key)) {
        std::cerr << "Помилка виклику getrandom\n";
        return 1;
    }

    std::cout << "Криптографічний ключ згенеровано безпечно.\n";
    return 0;
}
