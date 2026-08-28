#include <iostream>
#include <string>
#include <vector>
#include <span>
#include <filesystem>
#include <system_error>
#include <expected>
#include <cstring>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <libgen.h>
#endif

namespace fs = std::filesystem;

class ScopedDescriptor {
public:
#if defined(_WIN32)
    explicit ScopedDescriptor(HANDLE h = INVALID_HANDLE_VALUE) : handle_(h) {}
    ~ScopedDescriptor() { reset(); }

    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;

    ScopedDescriptor(ScopedDescriptor&& other) noexcept : handle_(other.handle_) {
        other.handle_ = INVALID_HANDLE_VALUE;
    }

    ScopedDescriptor& operator=(ScopedDescriptor&& other) noexcept {
        if (this != &other) {
            reset();
            handle_ = other.handle_;
            other.handle_ = INVALID_HANDLE_VALUE;
        }
        return *this;
    }

    [[nodiscard]] HANDLE get() const noexcept { return handle_; }
    [[nodiscard]] bool isValid() const noexcept { return handle_ != INVALID_HANDLE_VALUE; }

    void reset(HANDLE h = INVALID_HANDLE_VALUE) noexcept {
        if (handle_ != INVALID_HANDLE_VALUE) {
            CloseHandle(handle_);
            handle_ = h;
        }
    }

    HANDLE release() noexcept {
        HANDLE tmp = handle_;
        handle_ = INVALID_HANDLE_VALUE;
        return tmp;
    }
private:
    HANDLE handle_;
#else
    explicit ScopedDescriptor(int fd = -1) : fd_(fd) {}
    ~ScopedDescriptor() { reset(); }

    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;

    ScopedDescriptor(ScopedDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    ScopedDescriptor& operator=(ScopedDescriptor&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = new_fd;
        }
    }

    int release() noexcept {
        int tmp = fd_;
        fd_ = -1;
        return tmp;
    }
private:
    int fd_;
#endif
};

class AtomicFileEngine {
public:
    static std::expected<void, std::error_code> write(
        const fs::path& target_path,
        std::span<const std::byte> payload) noexcept 
    {
        std::error_code ec;
        fs::path parent_dir = target_path.parent_path();
        if (parent_dir.empty()) {
            parent_dir = ".";
        }

#if defined(_WIN32)
        std::wstring w_dir = parent_dir.wstring();
        std::wstring w_target = target_path.wstring();
        wchar_t w_temp[MAX_PATH];

        if (GetTempFileNameW(w_dir.c_str(), L"atm", 0, w_temp) == 0) {
            return std::unexpected(std::error_code((int)GetLastError(), std::system_category()));
        }

        fs::path temp_path(w_temp);
        ScopedDescriptor file_guard(CreateFileW(
            w_temp, GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr));

        if (!file_guard.isValid()) {
            DWORD err = GetLastError();
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code((int)err, std::system_category()));
        }

        DWORD written = 0;
        BOOL ok = WriteFile(file_guard.get(), payload.data(), static_cast<DWORD>(payload.size()), &written, nullptr);
        if (!ok || written != payload.size()) {
            DWORD err = GetLastError();
            file_guard.reset();
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code((int)(err ? err : ERROR_WRITE_FAULT), std::system_category()));
        }

        if (!FlushFileBuffers(file_guard.get())) {
            DWORD err = GetLastError();
            file_guard.reset();
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code((int)err, std::system_category()));
        }
        file_guard.reset(); // Закриваємо дескриптор перед заміною

        if (!ReplaceFileW(w_target.c_str(), w_temp, nullptr, REPLACEFILE_IGNORE_MERGE_ERRORS, nullptr, nullptr)) {
            DWORD err = GetLastError();
            if (err == ERROR_FILE_NOT_FOUND) {
                if (!MoveFileExW(w_temp, w_target.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
                    err = GetLastError();
                    fs::remove(temp_path, ec);
                    return std::unexpected(std::error_code((int)err, std::system_category()));
                }
            } else {
                fs::remove(temp_path, ec);
                return std::unexpected(std::error_code((int)err, std::system_category()));
            }
        }
        return {};

#else
        mode_t target_mode = 0644;
        struct stat st{};
        if (::stat(target_path.c_str(), &st) == 0) {
            target_mode = st.st_mode & 0777;
        }

        std::string temp_tmpl = (target_path.string() + ".tmp_XXXXXX");
        std::vector<char> tmpl_buf(temp_tmpl.begin(), temp_tmpl.end());
        tmpl_buf.push_back('\0');

        int raw_fd = ::mkstemp(tmpl_buf.data());
        if (raw_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        ScopedDescriptor file_guard(raw_fd);
        fs::path temp_path(tmpl_buf.data());

        if (::fchmod(file_guard.get(), target_mode) != 0) {
            int err = errno;
            file_guard.reset();
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        const auto* src = reinterpret_cast<const uint8_t*>(payload.data());
        size_t remaining = payload.size();
        while (remaining > 0) {
            ssize_t n = ::write(file_guard.get(), src, remaining);
            if (n < 0) {
                if (errno == EINTR) continue;
                int err = errno;
                file_guard.reset();
                fs::remove(temp_path, ec);
                return std::unexpected(std::error_code(err, std::generic_category()));
            }
            src += n;
            remaining -= static_cast<size_t>(n);
        }

        if (::fsync(file_guard.get()) != 0) {
            int err = errno;
            file_guard.reset();
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }
        file_guard.reset(); // Закриваємо файл перед rename

        if (::rename(temp_path.c_str(), target_path.c_str()) != 0) {
            int err = errno;
            fs::remove(temp_path, ec);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        // Синхронізація батьківського каталогу
        ScopedDescriptor dir_guard(::open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY));
        if (dir_guard.isValid()) {
            ::fsync(dir_guard.get());
        }

        return {};
#endif
    }
};
