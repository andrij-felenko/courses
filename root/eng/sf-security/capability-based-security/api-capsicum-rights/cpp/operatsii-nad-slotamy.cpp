#include <sel4/sel4.h>
#include <expected>
#include <cstdint>

namespace sel4 {

enum class Error : int {
    NoError = seL4_NoError,
    InvalidArgument = seL4_InvalidArgument,
    InvalidCapability = seL4_InvalidCapability,
    IllegalOperation = seL4_IllegalOperation,
    RangeError = seL4_RangeError,
    DeleteFirst = seL4_DeleteFirst,
    RevokeFirst = seL4_RevokeFirst,
    NotEnoughMemory = seL4_NotEnoughMemory
};

struct SlotRef {
    seL4_CNode root;
    seL4_Word index;
    seL4_Uint8 depth;
};

class CNodeManager {
public:
    explicit CNodeManager(seL4_CNode service_cnode) noexcept : service_{service_cnode} {}

    [[nodiscard]] std::expected<void, Error> mint(
        const SlotRef& dest, const SlotRef& src,
        seL4_CapRights_t rights, seL4_CapData_t badge) const noexcept
    {
        int res = ::seL4_CNode_Mint(
            service_, dest.index, dest.depth,
            src.root, src.index, src.depth,
            rights, badge);
        if (res != seL4_NoError) {
            return std::unexpected(static_cast<Error>(res));
        }
        return {};
    }

    [[nodiscard]] std::expected<void, Error> revoke(const SlotRef& target) const noexcept {
        int res = ::seL4_CNode_Revoke(service_, target.index, target.depth);
        if (res != seL4_NoError) {
            return std::unexpected(static_cast<Error>(res));
        }
        return {};
    }

    [[nodiscard]] std::expected<void, Error> remove(const SlotRef& target) const noexcept {
        int res = ::seL4_CNode_Delete(service_, target.index, target.depth);
        if (res != seL4_NoError) {
            return std::unexpected(static_cast<Error>(res));
        }
        return {};
    }

private:
    seL4_CNode service_;
};

} // namespace sel4
