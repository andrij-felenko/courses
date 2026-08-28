#include <sys/capsicum.h>
#include <system_error>
#include <cerrno>

namespace capsicum {

class Rights {
public:
    template <typename... Args>
    explicit Rights(Args... args) noexcept {
        ::cap_rights_init(&raw_, args..., 0);
    }

    [[nodiscard]] const cap_rights_t* get() const noexcept { return &raw_; }
    [[nodiscard]] cap_rights_t* get() noexcept { return &raw_; }

    [[nodiscard]] bool contains(const Rights& sub) const noexcept {
        return ::cap_rights_contains(&raw_, sub.get());
    }

    void apply_to(int fd) const {
        if (::cap_rights_limit(fd, &raw_) < 0) {
            throw std::system_error(errno, std::generic_category(), "cap_rights_limit failed");
        }
    }

    [[nodiscard]] static Rights from_fd(int fd) {
        Rights r;
        if (::cap_rights_get(fd, r.get()) < 0) {
            throw std::system_error(errno, std::generic_category(), "cap_rights_get failed");
        }
        return r;
    }

private:
    cap_rights_t raw_{};
};

} // namespace capsicum
