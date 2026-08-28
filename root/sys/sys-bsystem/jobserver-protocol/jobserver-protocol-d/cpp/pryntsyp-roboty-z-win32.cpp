// Modern C++20 Win32 RAII обгортка семафора Jobserver
#include <windows.h>
#include <string_view>
#include <memory>

struct HandleDeleter {
    void operator()(HANDLE h) const noexcept {
        if (h && h != INVALID_HANDLE_VALUE) {
            ::CloseHandle(h);
        }
    }
};
using UniqueHandle = std::unique_ptr<void, HandleDeleter>;

class Win32SemaphoreJobserver {
public:
    static UniqueHandle create(std::string_view name, int max_jobs) noexcept {
        HANDLE h = ::CreateSemaphoreA(nullptr, max_jobs - 1, max_jobs - 1, name.data());
        return UniqueHandle(h);
    }

    static UniqueHandle open(std::string_view name) noexcept {
        HANDLE h = ::OpenSemaphoreA(SYNCHRONIZE | SEMAPHORE_MODIFY_STATE, FALSE, name.data());
        return UniqueHandle(h);
    }

    static bool try_acquire(HANDLE h, DWORD timeout_ms = 0) noexcept {
        return ::WaitForSingleObject(h, timeout_ms) == WAIT_OBJECT_0;
    }

    static void release(HANDLE h) noexcept {
        ::ReleaseSemaphore(h, 1, nullptr);
    }
};
