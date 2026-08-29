#pragma once
#include <cstdint>
#include <optional>
#include <sys/ioctl.h>
#include <linux/kvm.h>

namespace kvm {

struct TranslationResult {
    uint64_t physical_address{0};
    bool valid{false};
    bool writeable{false};
    bool usermode{false};
};

class AddressTranslator {
public:
    [[nodiscard]] static std::optional<TranslationResult> translate(int vcpu_fd, uint64_t gva) noexcept {
        struct kvm_translation tr{};
        tr.linear_address = gva;
        if (ioctl(vcpu_fd, KVM_TRANSLATE, &tr) != 0 || !tr.valid) return std::nullopt;
        return TranslationResult{
            .physical_address = tr.physical_address,
            .valid = (tr.valid != 0),
            .writeable = (tr.writeable != 0),
            .usermode = (tr.usermode != 0)
        };
    }
};

}
