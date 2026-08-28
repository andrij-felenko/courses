#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <memory>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/kvm.h>

class KvmDevice {
public:
    static std::expected<KvmDevice, std::error_code> open_default() {
        int fd = ::open("/dev/kvm", O_RDWR | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return KvmDevice(fd);
    }

    ~KvmDevice() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    KvmDevice(const KvmDevice&) = delete;
    KvmDevice& operator=(const KvmDevice&) = delete;

    KvmDevice(KvmDevice&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    KvmDevice& operator=(KvmDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    std::expected<int, std::error_code> get_api_version() const {
        int ver = ::ioctl(fd_, KVM_GET_API_VERSION, 0);
        if (ver < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return ver;
    }

    struct CpuFlags {
        bool vmx{false};
        bool svm{false};
    };

    std::expected<CpuFlags, std::error_code> get_supported_cpu_flags() const {
        constexpr uint32_t nent = 64;
        const size_t alloc_size = sizeof(struct kvm_cpuid2) + nent * sizeof(struct kvm_cpuid_entry2);
        
        std::vector<uint8_t> buffer(alloc_size, 0);
        auto* cpuid = reinterpret_cast<struct kvm_cpuid2*>(buffer.data());
        cpuid->nent = nent;

        if (::ioctl(fd_, KVM_GET_SUPPORTED_CPUID, cpuid) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        CpuFlags flags{};
        constexpr uint32_t vmx_bit = 1 << 5;
        constexpr uint32_t svm_bit = 1 << 2;

        for (uint32_t i = 0; i < cpuid->nent; ++i) {
            const auto& entry = cpuid->entries[i];
            if (entry.function == 0x01) {
                if (entry.ecx & vmx_bit) flags.vmx = true;
            } else if (entry.function == 0x80000001) {
                if (entry.ecx & svm_bit) flags.svm = true;
            }
        }
        return flags;
    }

private:
    explicit KvmDevice(int fd) : fd_(fd) {}
    int fd_{-1};
};

static std::expected<bool, std::error_code> check_sysfs_parameter(const std::string& module_name) {
    std::string path = "/sys/module/" + module_name + "/parameters/nested";
    std::ifstream file(path);
    if (!file.is_open()) {
        return std::unexpected(std::error_code(ENOENT, std::generic_category()));
    }
    char val = 0;
    file >> val;
    return (val == 'Y' || val == 'y' || val == '1');
}

int main() {
    auto kvm_res = KvmDevice::open_default();
    if (!kvm_res) {
        std::cerr << "Не вдалося відкрити /dev/kvm: " << kvm_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    const auto& kvm = *kvm_res;
    auto api_ver = kvm.get_api_version();
    if (!api_ver || *api_ver != KVM_API_VERSION) {
        std::cerr << "Невідповідність KVM API\n";
        return EXIT_FAILURE;
    }

    auto flags_res = kvm.get_supported_cpu_flags();
    if (!flags_res) {
        std::cerr << "Помилка читання CPUID прапорців: " << flags_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    const auto& flags = *flags_res;
    std::cout << "=== Перевірка апаратних розширень (C++ RAII) ===\n";
    std::cout << "Intel VT-x (VMX): " << (flags.vmx ? "ПІДТРИМУЄТЬСЯ" : "ВІДСУТНІЙ") << '\n';
    std::cout << "AMD-V (SVM):     " << (flags.svm ? "ПІДТРИМУЄТЬСЯ" : "ВІДСУТНІЙ") << '\n';

    std::cout << "\n=== Стан sysfs parameters ===\n";
    if (auto intel_nested = check_sysfs_parameter("kvm_intel")) {
        std::cout << "kvm_intel.nested: " << (*intel_nested ? "УВІМКНЕНО" : "ВИМКНЕНО") << '\n';
    }
    if (auto amd_nested = check_sysfs_parameter("kvm_amd")) {
        std::cout << "kvm_amd.nested:   " << (*amd_nested ? "УВІМКНЕНО" : "ВИМКНЕНО") << '\n';
    }

    return EXIT_SUCCESS;
}
