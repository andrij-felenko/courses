#include <windows.h>
#include <string>
#include <system_error>
#include <filesystem>

namespace fs = std::filesystem;

class Win32Handle {
public:
    explicit Win32Handle(HANDLE handle = INVALID_HANDLE_VALUE) : handle_(handle) {}
    ~Win32Handle() {
        if (handle_ != INVALID_HANDLE_VALUE) {
            CloseHandle(handle_);
        }
    }

    Win32Handle(const Win32Handle&) = delete;
    Win32Handle& operator=(const Win32Handle&) = delete;

    Win32Handle(Win32Handle&& other) noexcept : handle_(other.handle_) {
        other.handle_ = INVALID_HANDLE_VALUE;
    }

    Win32Handle& operator=(Win32Handle&& other) noexcept {
        if (this != &other) {
            if (handle_ != INVALID_HANDLE_VALUE) CloseHandle(handle_);
            handle_ = other.handle_;
            other.handle_ = INVALID_HANDLE_VALUE;
        }
        return *this;
    }

    [[nodiscard]] HANDLE get() const noexcept { return handle_; }
    [[nodiscard]] bool is_valid() const noexcept { return handle_ != INVALID_HANDLE_VALUE; }

    void flush() {
        if (handle_ != INVALID_HANDLE_VALUE && !FlushFileBuffers(handle_)) {
            throw std::system_error(GetLastError(), std::system_category(), "FlushFileBuffers failed");
        }
    }

private:
    HANDLE handle_{INVALID_HANDLE_VALUE};
};

class Win32AtomicStorage {
public:
    static Win32Handle open_exclusive_writer(const fs::path& path) {
        HANDLE h = CreateFileW(
            path.c_str(),
            GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ,
            nullptr,
            CREATE_ALWAYS,
            FILE_ATTRIBUTE_NORMAL,
            nullptr
        );
        if (h == INVALID_HANDLE_VALUE) {
            throw std::system_error(GetLastError(), std::system_category(), "CreateFileW failed");
        }
        return Win32Handle(h);
    }

    static void commit_replace(const fs::path& temp_path, const fs::path& target_path) {
        if (!ReplaceFileW(
                target_path.c_str(),
                temp_path.c_str(),
                nullptr,
                REPLACEFILE_IGNORE_MERGE_ERRORS,
                nullptr,
                nullptr)) {
            // Якщо цільовий файл ще не існував, використовуємо MoveFileExW
            DWORD err = GetLastError();
            if (err == ERROR_FILE_NOT_FOUND) {
                if (!MoveFileExW(temp_path.c_str(), target_path.c_str(), MOVEFILE_REPLACE_EXISTING)) {
                    throw std::system_error(GetLastError(), std::system_category(), "MoveFileExW failed");
                }
                return;
            }
            throw std::system_error(err, std::system_category(), "ReplaceFileW failed");
        }
    }
};
