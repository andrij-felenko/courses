// У C++ заголовок <tss2/tss2_tctildr.h> підключається у просторі extern "C"
#include <memory>
#include <tss2/tss2_tctildr.h>

struct TctiDeleter {
    void operator()(TSS2_TCTI_CONTEXT* ctx) const noexcept {
        if (ctx) Tss2_TctiLdr_Finalize(&ctx);
    }
};
using TctiContextPtr = std::unique_ptr<TSS2_TCTI_CONTEXT, TctiDeleter>;
