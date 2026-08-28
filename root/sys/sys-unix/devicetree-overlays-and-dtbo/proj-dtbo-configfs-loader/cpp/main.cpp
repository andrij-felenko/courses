#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <system_error>
#include <bit>
#include <cstdint>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/mount.h>

namespace fs = std::filesystem;

/* RAII-обгортка сирого дескриптора: блоб має піти в ядро одним write(),
   а std::ofstream такої гарантії не дає. */
class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    explicit operator bool() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int get() const noexcept { return fd_; }
    void reset() noexcept { if (fd_ >= 0) { ::close(fd_); fd_ = -1; } }

private:
    int fd_;
};

class DtboOverlayManager {
public:
    static constexpr std::string_view configfs_path = "/sys/kernel/config";
    static constexpr std::string_view overlays_path = "/sys/kernel/config/device-tree/overlays";
    static constexpr uint32_t fdt_magic = 0xd00dfeedU;

    struct FdtHeader {
        uint32_t magic;
        uint32_t totalsize;
        uint32_t off_dt_struct;
        uint32_t off_dt_strings;
        uint32_t off_mem_rsvmap;
        uint32_t version;
        uint32_t last_comp_version;
        uint32_t boot_cpuid_phys;
        uint32_t size_dt_strings;
        uint32_t size_dt_struct;
    };

    explicit DtboOverlayManager(std::string overlay_name)
        : name_(std::move(overlay_name)),
          target_path_(fs::path(overlays_path) / name_) {}

    ~DtboOverlayManager() {
        if (applied_) {
            std::error_code ec;
            remove_overlay(ec);
        }
    }

    DtboOverlayManager(const DtboOverlayManager&) = delete;
    DtboOverlayManager& operator=(const DtboOverlayManager&) = delete;

    DtboOverlayManager(DtboOverlayManager&& other) noexcept
        : name_(std::move(other.name_)),
          target_path_(std::move(other.target_path_)),
          applied_(other.applied_) {
        other.applied_ = false;
    }

    DtboOverlayManager& operator=(DtboOverlayManager&& other) noexcept {
        if (this != &other) {
            if (applied_) {
                std::error_code ec;
                remove_overlay(ec);
            }
            name_ = std::move(other.name_);
            target_path_ = std::move(other.target_path_);
            applied_ = other.applied_;
            other.applied_ = false;
        }
        return *this;
    }

    bool apply_overlay(const fs::path& dtbo_filepath, std::error_code& ec) {
        if (!ensure_configfs(ec)) {
            return false;
        }

        auto buffer = read_file(dtbo_filepath, ec);
        if (ec) {
            return false;
        }

        if (!validate_header(buffer, ec)) {
            return false;
        }

        if (!fs::exists(target_path_)) {
            if (!fs::create_directory(target_path_, ec)) {
                return false;
            }
        }

        fs::path dtbo_attr = target_path_ / "dtbo";
        FileDescriptor fd(::open(dtbo_attr.c_str(), O_WRONLY));
        if (!fd) {
            ec = std::error_code(errno, std::generic_category());
            std::error_code rm;
            fs::remove(target_path_, rm);
            return false;
        }

        const ssize_t written = ::write(fd.get(), buffer.data(), buffer.size());
        fd.reset();
        if (written < 0 || static_cast<size_t>(written) != buffer.size()) {
            ec = std::error_code(errno, std::generic_category());
            std::error_code rm;
            fs::remove(target_path_, rm);
            return false;
        }

        if (!check_status(ec)) {
            fs::remove(target_path_, ec);
            return false;
        }

        applied_ = true;
        return true;
    }

    bool remove_overlay(std::error_code& ec) {
        if (!applied_ && !fs::exists(target_path_)) {
            return true;
        }

        if (fs::remove(target_path_, ec)) {
            applied_ = false;
            return true;
        }
        return false;
    }

    [[nodiscard]] bool is_applied() const noexcept { return applied_; }
    [[nodiscard]] const std::string& name() const noexcept { return name_; }

private:
    std::string name_;
    fs::path target_path_;
    bool applied_{false};

    static bool ensure_configfs(std::error_code& ec) {
        if (fs::exists(overlays_path)) {
            return true;
        }

        if (!fs::exists(configfs_path)) {
            ec = std::make_error_code(std::errc::no_such_file_or_directory);
            return false;
        }

        if (::mount("none", configfs_path.data(), "configfs", 0, nullptr) != 0) {
            if (errno != EBUSY) {
                ec = std::error_code(errno, std::generic_category());
                return false;
            }
        }

        if (!fs::exists(overlays_path)) {
            ec = std::make_error_code(std::errc::protocol_not_supported);
            return false;
        }
        return true;
    }

    static std::vector<uint8_t> read_file(const fs::path& path, std::error_code& ec) {
        std::ifstream ifs(path, std::ios::binary | std::ios::ate);
        if (!ifs) {
            ec = std::make_error_code(std::errc::no_such_file_or_directory);
            return {};
        }

        auto size = ifs.tellg();
        ifs.seekg(0, std::ios::beg);

        std::vector<uint8_t> buffer(size);
        if (!ifs.read(reinterpret_cast<char*>(buffer.data()), size)) {
            ec = std::make_error_code(std::errc::io_error);
            return {};
        }

        return buffer;
    }

    static bool validate_header(const std::vector<uint8_t>& buffer, std::error_code& ec) {
        if (buffer.size() < sizeof(FdtHeader)) {
            ec = std::make_error_code(std::errc::executable_format_error);
            return false;
        }

        const auto* hdr = reinterpret_cast<const FdtHeader*>(buffer.data());
        const auto from_be = [](uint32_t v) -> uint32_t {
            if constexpr (std::endian::native == std::endian::little) {
                return std::byteswap(v);
            } else {
                return v;
            }
        };
        uint32_t magic = from_be(hdr->magic);
        uint32_t totalsize = from_be(hdr->totalsize);

        if (magic != fdt_magic || totalsize > buffer.size()) {
            ec = std::make_error_code(std::errc::illegal_byte_sequence);
            return false;
        }

        return true;
    }

    bool check_status(std::error_code& ec) const {
        fs::path status_attr = target_path_ / "status";
        std::ifstream ifs(status_attr);
        if (!ifs) {
            ec = std::make_error_code(std::errc::no_such_file_or_directory);
            return false;
        }

        std::string status;
        std::getline(ifs, status);
        if (!status.empty() && status.back() == '\r') {
            status.pop_back();
        }

        if (status != "applied") {
            ec = std::make_error_code(std::errc::state_not_recoverable);
            return false;
        }

        return true;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cout << "Використання: " << argv[0] << " <apply|remove> <ім'я_оверлею> [файл.dtbo]\n";
        return 1;
    }

    std::string_view cmd = argv[1];
    std::string name = argv[2];
    std::error_code ec;

    if (cmd == "apply") {
        if (argc < 4) {
            std::cerr << "Потрібно вказати шлях до файлу .dtbo\n";
            return 1;
        }

        DtboOverlayManager mgr(name);
        if (!mgr.apply_overlay(argv[3], ec)) {
            std::cerr << "[ERR] Не вдалося застосувати оверлей: " << ec.message() << "\n";
            return 1;
        }

        std::cout << "[OK] Оверлей '" << name << "' застосовано. Натисніть Enter для видалення...\n";
        std::cin.get();
        return 0;
    } else if (cmd == "remove") {
        DtboOverlayManager mgr(name);
        if (!mgr.remove_overlay(ec)) {
            std::cerr << "[ERR] Не вдалося видалити оверлей: " << ec.message() << "\n";
            return 1;
        }
        std::cout << "[OK] Оверлей '" << name << "' видалено.\n";
        return 0;
    }

    std::cerr << "Невідома команда: " << cmd << "\n";
    return 1;
}
