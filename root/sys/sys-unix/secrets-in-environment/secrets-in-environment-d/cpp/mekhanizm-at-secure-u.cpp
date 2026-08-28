// Концептуальна логіка верифікації зміни облікових даних процесу
#include <cstdint>
#include <concepts>

struct Credentials {
    std::uint32_t uid{0};
    std::uint32_t gid{0};
    std::uint32_t euid{0};
    std::uint32_t egid{0};
    std::uint64_t capabilities{0};
};

[[nodiscard]] constexpr bool is_privilege_transition(const Credentials& current, const Credentials& target) noexcept {
    return (target.euid != current.euid) ||
           (target.egid != current.egid) ||
           (target.uid  != current.uid)  ||
           (target.gid  != current.gid)  ||
           ((target.capabilities & ~current.capabilities) != 0);
}
