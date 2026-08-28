#include <iostream>
#include <iomanip>
#include <array>
#include <span>
#include <vector>
#include <system_error>
#include <expected>
#include <memory>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/random.h>
#include <linux/types.h>

namespace confidential_compute {

#ifndef SNP_GET_REPORT
struct snp_report_req {
    __u8 user_data[64];
    __u32 vmpl;
    __u8 rsvd[28];
};

struct snp_report_resp {
    __u8 data[4000];
};

struct snp_guest_request_ioctl {
    __u8 msg_version;
    __u64 req_data;
    __u64 resp_data;
    __u64 fw_error;
};

#define SNP_GUEST_REQ_IOC_TYPE 'S'
#define SNP_GET_REPORT _IOWR(SNP_GUEST_REQ_IOC_TYPE, 0x0, struct snp_guest_request_ioctl)
#endif

// RAII класу-обгортки для файлового дескриптора POSIX
class SafeFileDescriptor {
    int fd_{-1};
public:
    explicit SafeFileDescriptor(const char* path, int flags) noexcept
        : fd_{::open(path, flags)} {}
    
    ~SafeFileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SafeFileDescriptor(const SafeFileDescriptor&) = delete;
    SafeFileDescriptor& operator=(const SafeFileDescriptor&) = delete;
    
    SafeFileDescriptor(SafeFileDescriptor&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
};

struct SevAttestationData {
    std::array<uint8_t, 48> launch_measurement{};
    uint64_t firmware_error_code{0};
};

enum class AttestationError {
    DeviceOpenFailed,
    RandomGenerationFailed,
    IoctlFailed,
    NonceMismatch,
    FirmwareError
};

class AttestationService {
public:
    [[nodiscard]] static auto generate_nonce() 
        -> std::expected<std::array<uint8_t, 64>, AttestationError> 
    {
        std::array<uint8_t, 64> nonce{};
        if (::getrandom(nonce.data(), nonce.size(), 0) != static_cast<ssize_t>(nonce.size())) {
            return std::unexpected(AttestationError::RandomGenerationFailed);
        }
        return nonce;
    }

    [[nodiscard]] static auto request_snp_report(std::span<const uint8_t, 64> nonce) 
        -> std::expected<SevAttestationData, AttestationError> 
    {
        SafeFileDescriptor dev("/dev/sev-guest", O_RDWR);
        if (!dev.is_valid()) {
            std::cerr << "[C++ Driver] Не вдалося відкрити /dev/sev-guest (errno: " << errno << ")\n";
            return std::unexpected(AttestationError::DeviceOpenFailed);
        }

        snp_report_req req{};
        snp_report_resp resp{};
        snp_guest_request_ioctl ioctl_req{};

        std::memcpy(req.user_data, nonce.data(), nonce.size());
        req.vmpl = 0; // VMPL0

        ioctl_req.msg_version = 1;
        ioctl_req.req_data = reinterpret_cast<uint64_t>(&req);
        ioctl_req.resp_data = reinterpret_cast<uint64_t>(&resp);

        if (::ioctl(dev.get(), SNP_GET_REPORT, &ioctl_req) < 0) {
            if (ioctl_req.fw_error != 0) {
                std::cerr << "[C++ Driver] Помилка прошивки ASP: 0x" 
                          << std::hex << ioctl_req.fw_error << std::dec << "\n";
            }
            return std::unexpected(AttestationError::IoctlFailed);
        }

        // Перевірка ехо Nonce у вихідній структурі (зсув 0x50)
        if (std::memcmp(&resp.data[0x50], nonce.data(), 64) != 0) {
            return std::unexpected(AttestationError::NonceMismatch);
        }

        SevAttestationData result{};
        result.firmware_error_code = ioctl_req.fw_error;
        std::memcpy(result.launch_measurement.data(), &resp.data[0x90], result.launch_measurement.size());

        return result;
    }
};

} // namespace confidential_compute

int main() {
    using namespace confidential_compute;
    std::cout << "=== Демон атестації AMD SEV-SNP (Мова C++23/RAII) ===\n";

    auto nonce_res = AttestationService::generate_nonce();
    if (!nonce_res) {            std::cerr << "Не вдалося згенерувати безпечний nonce.\n";
        return EXIT_FAILURE;
    }

    auto report_res = AttestationService::request_snp_report(*nonce_res);
    if (report_res) {
        std::cout << "Успішно завантажено та перевірено Measurement Digest (SHA-384):\n";
        std::cout << std::hex << std::setfill('0');
        for (uint8_t byte : report_res->launch_measurement) {
            std::cout << std::setw(2) << static_cast<int>(byte);
        }
        std::cout << std::dec << "\n";
        return EXIT_SUCCESS;
    } else {
        std::cerr << "Помилка отримання атестаційного звіту.\n";
        return EXIT_FAILURE;
    }
}
