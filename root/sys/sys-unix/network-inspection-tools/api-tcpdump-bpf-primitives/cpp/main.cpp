#include <cstdint>
#include <span>
#include <vector>
#include <linux/types.h>
#include <linux/filter.h>

namespace bpf {

// Ідіоматична C++ обгортка над програмою фільтрації cBPF
class BpfProgram {
public:
    explicit BpfProgram(std::vector<sock_filter> instructions)
        : instructions_{std::move(instructions)} {}

    [[nodiscard]] sock_fprog get_fprog() noexcept {
        return sock_fprog{
            .len = static_cast<unsigned short>(instructions_.size()),
            .filter = instructions_.data()
        };
    }

    [[nodiscard]] std::span<const sock_filter> instructions() const noexcept {
        return instructions_;
    }

private:
    std::vector<sock_filter> instructions_;
};

} // namespace bpf
