#include <unwind.h>
#include <cxxabi.h>
#include <cstdio>

static _Unwind_Reason_Code on_frame(_Unwind_Context* ctx, void* arg) {
    int* left = static_cast<int*>(arg);
    int before = 0;
    _Unwind_Ptr ip   = _Unwind_GetIPInfo(ctx, &before);
    _Unwind_Ptr fn   = _Unwind_GetRegionStart(ctx);
    void*       lsda = _Unwind_GetLanguageSpecificData(ctx);

    std::printf("ip=%p  функція=%p  зсув=%#lx  LSDA=%s  %s\n",
                (void*)ip, (void*)fn, (unsigned long)(ip - fn),
                lsda ? "є" : "немає",
                before ? "ip на самій команді" : "ip уже за call");

    return (--*left == 0) ? _URC_END_OF_STACK : _URC_NO_REASON;
}

void dump_frames() {
    int left = 16;
    _Unwind_Backtrace(&on_frame, &left);
}

// у власному обробнику аварії стане в пригоді й тип того, що зараз летить:
void my_terminate() {
    if (const std::type_info* t = abi::__cxa_current_exception_type())
        std::printf("невиловлений виняток типу %s\n", t->name());  // ім'я понівечене,
    std::abort();                        // людське дає abi::__cxa_demangle з того ж заголовка
}
