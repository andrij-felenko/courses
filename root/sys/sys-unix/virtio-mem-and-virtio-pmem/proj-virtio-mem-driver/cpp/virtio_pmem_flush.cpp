// virtio_pmem_flush.cpp — Обробник флаш-запитів мовою C++ (std::expected замість кодів помилок)
#include <iostream>
#include <cstdint>
#include <expected>
#include <system_error>
#include <cerrno>
#include <unistd.h>

enum class PmemReqType : uint32_t {
    Flush = 0
};

struct PmemReq {
    PmemReqType type;
};

struct PmemResp {
    int32_t status{0};
};

class HostBackendFile {
public:
    explicit HostBackendFile(int fd) noexcept : fd_(fd) {}

    [[nodiscard]] std::expected<void, std::error_code> sync_data() const noexcept {
        if (fd_ < 0) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }
        if (::fdatasync(fd_) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

private:
    int fd_{-1};
};

PmemResp process_pmem_request(const HostBackendFile& backend, const PmemReq& req) {
    PmemResp resp;
    if (req.type == PmemReqType::Flush) {
        auto result = backend.sync_data();
        if (result) {
            resp.status = 0;
            std::cout << "[virtio-pmem C++ host] DAX Sync OK\n";
        } else {
            resp.status = -result.error().value();
            std::cerr << "[virtio-pmem C++ host] Sync Error: " << result.error().message() << "\n";
        }
    } else {
        resp.status = -EINVAL;
    }
    return resp;
}
