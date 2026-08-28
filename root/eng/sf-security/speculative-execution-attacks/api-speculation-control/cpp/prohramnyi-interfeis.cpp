#include <iostream>
#include <system_error>
#include <cerrno>
#include <sys/prctl.h>

namespace security {

enum class SpeculationTarget : unsigned long {
    IndirectBranch = PR_SPEC_INDIRECT_BRANCH,
    StoreBypass    = PR_SPEC_STORE_BYPASS,
    L1dFlush       = PR_SPEC_L1D_FLUSH
};

class ProcessSpeculationController {
public:
    static void force_disable(SpeculationTarget target) {
        const auto resource = static_cast<unsigned long>(target);
        if (::prctl(PR_SET_SPECULATION_CTRL, resource, PR_SPEC_FORCE_DISABLE, 0, 0) != 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "Не вдалося встановити PR_SPEC_FORCE_DISABLE");
        }
    }

    [[nodiscard]] static bool is_force_disabled(SpeculationTarget target) noexcept {
        const auto resource = static_cast<unsigned long>(target);
        const int status = ::prctl(PR_GET_SPECULATION_CTRL, resource, 0, 0, 0);
        if (status < 0) {
            return false;
        }
        return (status & PR_SPEC_PRCTL) && (status & PR_SPEC_FORCE_DISABLE);
    }
};

} // namespace security
