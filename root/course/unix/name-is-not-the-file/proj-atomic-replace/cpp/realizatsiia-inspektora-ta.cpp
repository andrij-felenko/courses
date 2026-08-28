#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

struct GhostFileEntry {
    pid_t pid;
    int fd;
    std::string original_path;
    size_t file_size;
};

class ProcRescueManager {
public:
    static std::vector<GhostFileEntry> scan_process(pid_t pid) {
        std::vector<GhostFileEntry> results;
        const fs::path fd_path = fs::path("/proc") / std::to_string(pid) / "fd";

        std::error_code ec;
        if (!fs::exists(fd_path, ec)) {
            return results;
        }

        for (const auto& entry : fs::directory_iterator(fd_path, ec)) {
            if (ec) break;

            std::string link_target = fs::read_symlink(entry.path(), ec).string();
            if (ec) { ec.clear(); continue; }

            if (link_target.find("(deleted)") != std::string::npos) {
                int fd_num = -1;
                try {
                    fd_num = std::stoi(entry.path().filename().string());
                } catch (...) {
                    continue;
                }

                struct stat st{};
                size_t size_bytes = 0;
                if (::stat(entry.path().c_str(), &st) == 0) {
                    size_bytes = static_cast<size_t>(st.st_size);
                }

                results.push_back(GhostFileEntry{
                    .pid = pid,
                    .fd = fd_num,
                    .original_path = link_target,
                    .file_size = size_bytes
                });
            }
        }
        return results;
    }

    static std::expected<fs::path, std::error_code> 
    rescue_file(const GhostFileEntry& item, const fs::path& dest_dir) {
        std::error_code ec;
        fs::create_directories(dest_dir, ec);
        if (ec) return std::unexpected(ec);

        std::string clean_name = item.original_path;
        auto pos = clean_name.find(" (deleted)");
        if (pos != std::string::npos) {
            clean_name.erase(pos);
        }

        fs::path orig_p(clean_name);
        std::string fname = orig_p.filename().empty() ? "unnamed_ghost" : orig_p.filename().string();
        fs::path out_file = dest_dir / ("rescued_pid" + std::to_string(item.pid) + "_fd" + std::to_string(item.fd) + "_" + fname);

        fs::path magic_link = fs::path("/proc") / std::to_string(item.pid) / "fd" / std::to_string(item.fd);

        int in_fd = ::open(magic_link.c_str(), O_RDONLY | O_CLOEXEC);
        if (in_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        int out_fd = ::open(out_file.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0640);
        if (out_fd < 0) {
            int err = errno;
            ::close(in_fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        std::vector<char> buffer(65536);
        ssize_t bytes_read = 0;
        while ((bytes_read = ::read(in_fd, buffer.data(), buffer.size())) > 0) {
            char* ptr = buffer.data();
            ssize_t to_write = bytes_read;
            while (to_write > 0) {
                ssize_t written = ::write(out_fd, ptr, to_write);
                if (written < 0) {
                    if (errno == EINTR) continue;
                    int err = errno;
                    ::close(in_fd);
                    ::close(out_fd);
                    return std::unexpected(std::error_code(err, std::generic_category()));
                }
                ptr += written;
                to_write -= written;
            }
        }

        ::close(in_fd);
        ::close(out_fd);
        return out_file;
    }
};
