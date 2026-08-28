#include <linux/filter.h>
#include <vector>
#include <span>

namespace sys {

// C++ контейнерний тип для безпечного керування пам'яттю BPF програм
class BpfProgram {
    std::vector<::sock_filter> instructions_;
public:
    explicit BpfProgram(std::vector<::sock_filter> instrs) 
        : instructions_(std::move(instrs)) {}

    [[nodiscard]] ::sock_fprog get_fprog() const noexcept {
        return ::sock_fprog{
            .len = static_cast<unsigned short>(instructions_.size()),
            .filter = const_cast<::sock_filter*>(instructions_.data())
        };
    }
};

} // namespace sys
