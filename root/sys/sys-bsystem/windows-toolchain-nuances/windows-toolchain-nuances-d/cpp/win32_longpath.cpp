// win32_longpath.cpp — безпечне відкриття файлу в C++ з std::filesystem
#include <windows.h>
#include <filesystem>
#include <iostream>
#include <string>

class UniqueHandle {
public:
    explicit UniqueHandle(HANDLE h = INVALID_HANDLE_VALUE) noexcept : handle_(h) {}
    ~UniqueHandle() noexcept {
        if (handle_ != INVALID_HANDLE_VALUE && handle_ != nullptr) {
            CloseHandle(handle_);
        }
    }

    UniqueHandle(const UniqueHandle&) = delete;
    UniqueHandle& operator=(const UniqueHandle&) = delete;

    UniqueHandle(UniqueHandle&& other) noexcept : handle_(other.handle_) {
        other.handle_ = INVALID_HANDLE_VALUE;
    }

    UniqueHandle& operator=(UniqueHandle&& other) noexcept {
        if (this != &other) {
            if (handle_ != INVALID_HANDLE_VALUE && handle_ != nullptr) {
                CloseHandle(handle_);
            }
            handle_ = other.handle_;
            other.handle_ = INVALID_HANDLE_VALUE;
        }
        return *this;
    }

    [[nodiscard]] HANDLE get() const noexcept { return handle_; }
    [[nodiscard]] bool is_valid() const noexcept { return handle_ != INVALID_HANDLE_VALUE; }

private:
    HANDLE handle_;
};

UniqueHandle open_file_modern(const std::filesystem::path& file_path, DWORD access_mode) {
    // std::filesystem під MSVC самостійно нормалізує та додає префікс \\?\ 
    // для абсолютних шляхів, якщо це необхідно
    const std::wstring native_path = file_path.wstring();

    HANDLE h = CreateFileW(
        native_path.c_str(),
        access_mode,
        FILE_SHARE_READ,
        nullptr,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );

    return UniqueHandle(h);
}
