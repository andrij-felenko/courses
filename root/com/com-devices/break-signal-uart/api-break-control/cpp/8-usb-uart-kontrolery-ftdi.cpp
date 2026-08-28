// Керування Break через обгортку FTDI D2XX на C++
#include <ftd2xx.h>
#include <stdexcept>

class FtdiBreakGuard {
public:
    explicit FtdiBreakGuard(FT_HANDLE handle) : handle_{handle} {
        if (::FT_SetBreakOn(handle_) != FT_OK) {
            throw std::runtime_error("FT_SetBreakOn failed");
        }
    }

    ~FtdiBreakGuard() noexcept {
        ::FT_SetBreakOff(handle_);
    }

    FtdiBreakGuard(const FtdiBreakGuard&) = delete;
    FtdiBreakGuard& operator=(const FtdiBreakGuard&) = delete;

private:
    FT_HANDLE handle_;
};
