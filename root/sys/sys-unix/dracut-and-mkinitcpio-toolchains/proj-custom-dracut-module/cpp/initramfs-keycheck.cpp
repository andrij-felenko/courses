// initramfs-keycheck.cpp — Ідіоматична C++ реалізація (RAII, string_view, filesystem, expected)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <expected>
#include <system_error>

namespace fs = std::filesystem;

constexpr std::string_view EXPECTED_MAGIC = "SECUREKEY2026";
constexpr std::string_view CMDLINE_PATH = "/proc/cmdline";

enum class CheckError {
    MissingArgument,
    FileNotFound,
    NotARegularFile,
    FileTooSmall,
    OpenFailed,
    ReadFailed,
    InvalidMagic
};

std::string_view to_string(CheckError err) noexcept {
    switch (err) {
        case CheckError::MissingArgument: return "No keypath provided via CLI or cmdline";
        case CheckError::FileNotFound:    return "Keyfile path does not exist";
        case CheckError::NotARegularFile: return "Target path is not a regular file";
        case CheckError::FileTooSmall:    return "Keyfile size is smaller than expected header";
        case CheckError::OpenFailed:      return "Failed to open keyfile for reading";
        case CheckError::ReadFailed:      return "Failed to read header bytes";
        case CheckError::InvalidMagic:    return "Magic token mismatch in keyfile header";
    }
    return "Unknown error";
}

class FileHandle {
    int fd_ = -1;
public:
    explicit FileHandle(int fd) noexcept : fd_(fd) {}
    ~FileHandle() { if (fd_ >= 0) ::close(fd_); }
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
    FileHandle(FileHandle&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

std::expected<void, CheckError> verify_keyfile(const fs::path& keypath) {
    std::error_code ec;

    if (!fs::exists(keypath, ec) || ec) {
        return std::unexpected(CheckError::FileNotFound);
    }

    if (!fs::is_regular_file(keypath, ec) || ec) {
        return std::unexpected(CheckError::NotARegularFile);
    }

    if (fs::file_size(keypath, ec) < EXPECTED_MAGIC.size() || ec) {
        return std::unexpected(CheckError::FileTooSmall);
    }

    std::ifstream file(keypath, std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected(CheckError::OpenFailed);
    }

    std::string header(EXPECTED_MAGIC.size(), '\0');
    if (!file.read(header.data(), static_cast<std::streamsize>(header.size()))) {
        return std::unexpected(CheckError::ReadFailed);
    }

    if (header != EXPECTED_MAGIC) {
        return std::unexpected(CheckError::InvalidMagic);
    }

    return {};
}

std::string parse_cmdline_keypath() {
    std::ifstream cmdfile(std::string{CMDLINE_PATH});
    if (!cmdfile.is_open()) return "";

    std::string line;
    if (std::getline(cmdfile, line)) {
        constexpr std::string_view key_prefix = "keycheck.path=";
        auto pos = line.find(key_prefix);
        if (pos != std::string::npos) {
            auto start = pos + key_prefix.size();
            auto end = line.find_first_of(" \n\r", start);
            return line.substr(start, (end == std::string::npos) ? std::string::npos : (end - start));
        }
    }
    return "";
}

int main(int argc, char* argv[]) {
    std::string keypath_str;

    if (argc >= 2) {
        keypath_str = argv[1];
    } else {
        keypath_str = parse_cmdline_keypath();
    }

    if (keypath_str.empty()) {
        std::cerr << "[keycheck:ERR] " << to_string(CheckError::MissingArgument) << "\n";
        return 1;
    }

    const fs::path keypath{keypath_str};
    auto result = verify_keyfile(keypath);

    if (!result) {
        std::cerr << "[keycheck:FAIL] Error verifying " << keypath << ": "
                  << to_string(result.error()) << "\n";
        return static_cast<int>(result.error());
    }

    std::cout << "[keycheck:OK] SUCCESS: Valid token verified at " << keypath << "\n";
    return 0;
}
