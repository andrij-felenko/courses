// C++: Управління ресурсом через std::unique_ptr та custom deleter
#include <memory>
#include <stdexcept>
#include <xf86drm.h>
#include <xf86drmMode.h>

struct AtomicReqDeleter {
    void operator()(drmModeAtomicReqPtr req) const noexcept {
        if (req) ::drmModeAtomicFree(req);
    }
};

using AtomicReqPtr = std::unique_ptr<drmModeAtomicReq, AtomicReqDeleter>;

AtomicReqPtr create_atomic_request() {
    AtomicReqPtr req(::drmModeAtomicAlloc());
    if (!req) throw std::bad_alloc();
    return req;
}
