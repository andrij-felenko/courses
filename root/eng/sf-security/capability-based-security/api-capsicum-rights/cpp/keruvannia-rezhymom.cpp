#include <sys/capsicum.h>
#include <system_error>
#include <cerrno>

namespace capsicum {

inline void enter() {
    if (::cap_enter() < 0) {
        throw std::system_error(errno, std::generic_category(), "cap_enter failed");
    }
}

[[nodiscard]] inline bool is_capability_mode() {
    u_int mode = 0;
    if (::cap_getmode(&mode) < 0) {
        throw std::system_error(errno, std::generic_category(), "cap_getmode failed");
    }
    return mode != 0;
}

} // namespace capsicum
