#include <iostream>
#include <format>
#include <cstdint>
#include <cstring>
#include <expected>
#include <fcntl.h>
#include <unistd.h>

namespace sys {

constexpr uint32_t IA32_EFER_MSR = 0xC0000080;

class MsrReader {
public:
    explicit MsrReader(int cpu_id) {
        auto path = std::format("/dev/cpu/{}/msr", cpu_id);
        fd_ = ::open(path.c_str(), O_RDONLY);
    }

    ~MsrReader() {
        if (fd_ >= 0) ::close(fd_);
    }

    MsrReader(const MsrReader&) = delete;
    MsrReader& operator=(const MsrReader&) = delete;

    [[nodiscard]] std::expected<uint64_t, std::string> read(uint32_t msr_addr) const {
        if (fd_ < 0) return std::unexpected("Дескриптор MSR не відкрито");
        
        uint64_t val = 0;
        if (::pread(fd_, &val, sizeof(val), static_cast<off_t>(msr_addr)) != sizeof(val)) {
            return std::unexpected(std::strerror(errno));
        }
        return val;
    }

private:
    int fd_{-1};
};

} // namespace sys

int main() {
    sys::MsrReader msr(0);
    auto efer_res = msr.read(sys::IA32_EFER_MSR);
    if (!efer_res) {
        std::cerr << "Помилка: " << efer_res.error() << '\n';
        return 1;
    }

    uint64_t val = *efer_res;
    std::cout << std::format("IA32_EFER = 0x{:016X}\n", val);
    std::cout << std::format("  Long Mode Active (LMA): {}\n", (val & (1 << 10)) ? "Так" : "Ні");
    std::cout << std::format("  No-Execute Enable (NXE): {}\n", (val & (1 << 11)) ? "Так" : "Ні");
    std::cout << std::format("  Syscall Extensions (SCE): {}\n", (val & (1 << 0)) ? "Так" : "Ні");

    return 0;
}
