#include <iostream>
#include <string_view>
#include <expected>
#include <system_error>
#include <vector>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/ptp_clock.h>

class PtpDevice {
    int fd_{-1};
public:
    explicit PtpDevice(std::string_view path) {
        fd_ = ::open(path.data(), O_RDONLY);
    }
    ~PtpDevice() {
        if (fd_ >= 0) ::close(fd_);
    }
    [[nodiscard]] bool is_open() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

struct PreciseTimestampPair {
    int64_t phc_time_ns{0};
    int64_t sys_realtime_ns{0};
    int64_t sys_monoraw_ns{0};
    int64_t offset_ns{0};
};

struct SampledOffset {
    int64_t phc_time_ns{0};
    int64_t sys_midpoint_ns{0};
    int64_t bus_delay_ns{0};
    int64_t offset_ns{0};
};

class CrossTimestampReader {
    PtpDevice dev_;

public:
    explicit CrossTimestampReader(std::string_view path) : dev_(path) {}

    [[nodiscard]] bool is_valid() const noexcept { return dev_.is_open(); }

    std::expected<PreciseTimestampPair, std::error_code> read_precise() {
        if (!dev_.is_open()) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }

        struct ptp_sys_offset_precise offset{};
        if (::ioctl(dev_.get(), PTP_SYS_OFFSET_PRECISE, &offset) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        PreciseTimestampPair pair{};
        pair.phc_time_ns = static_cast<int64_t>(offset.device.sec) * 1'000'000'000LL + offset.device.nsec;
        pair.sys_realtime_ns = static_cast<int64_t>(offset.sys_realtime.sec) * 1'000'000'000LL + offset.sys_realtime.nsec;
        pair.sys_monoraw_ns = static_cast<int64_t>(offset.sys_monoraw.sec) * 1'000'000'000LL + offset.sys_monoraw.nsec;
        pair.offset_ns = pair.sys_realtime_ns - pair.phc_time_ns;

        return pair;
    }

    std::expected<std::vector<SampledOffset>, std::error_code> read_software_sandwich(unsigned int samples = 5) {
        if (!dev_.is_open()) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }

        struct ptp_sys_offset sysoff{};
        sysoff.n_samples = samples;

        if (::ioctl(dev_.get(), PTP_SYS_OFFSET, &sysoff) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::vector<SampledOffset> results;
        results.reserve(samples);

        for (unsigned int i = 0; i < sysoff.n_samples; ++i) {
            int64_t t_cpu1 = static_cast<int64_t>(sysoff.ts[2 * i].sec) * 1'000'000'000LL + sysoff.ts[2 * i].nsec;
            int64_t t_phc  = static_cast<int64_t>(sysoff.ts[2 * i + 1].sec) * 1'000'000'000LL + sysoff.ts[2 * i + 1].nsec;
            int64_t t_cpu2 = static_cast<int64_t>(sysoff.ts[2 * i + 2].sec) * 1'000'000'000LL + sysoff.ts[2 * i + 2].nsec;

            int64_t cpu_mid = (t_cpu1 + t_cpu2) / 2;
            int64_t delay = t_cpu2 - t_cpu1;
            int64_t offset = cpu_mid - t_phc;

            results.push_back(SampledOffset{
                .phc_time_ns = t_phc,
                .sys_midpoint_ns = cpu_mid,
                .bus_delay_ns = delay,
                .offset_ns = offset
            });
        }
        return results;
    }
};

int main(int argc, char* argv[]) {
    std::string_view ptp_path = (argc > 1) ? argv[1] : "/dev/ptp0";
    CrossTimestampReader reader(ptp_path);

    if (!reader.is_valid()) {
        std::cerr << "Не вдалося відкрити пристрій " << ptp_path << "\n";
        return 1;
    }

    if (auto precise_res = reader.read_precise(); precise_res) {
        const auto& p = *precise_res;
        std::cout << "Апаратний Cross-Timestamping (PTP_SYS_OFFSET_PRECISE):\n"
                  << "  Час PHC:      " << p.phc_time_ns << " нс\n"
                  << "  Час Realtime: " << p.sys_realtime_ns << " нс\n"
                  << "  Зсув (Offset):" << p.offset_ns << " нс\n";
    } else {
        std::cout << "PTP_SYS_OFFSET_PRECISE недоступний (" << precise_res.error().message()
                  << "). Спроба програмного вимірювання PTP_SYS_OFFSET...\n";

        auto sw_res = reader.read_software_sandwich(5);
        if (!sw_res) {
            std::cerr << "Помилка PTP_SYS_OFFSET: " << sw_res.error().message() << "\n";
            return 1;
        }

        std::cout << "Результати програмного опитування:\n";
        for (size_t i = 0; i < sw_res->size(); ++i) {
            const auto& s = (*sw_res)[i];
            std::cout << "  Вибірка " << i << ": PHC=" << s.phc_time_ns
                      << " нс, CPU_mid=" << s.sys_midpoint_ns
                      << " нс, Затримка шини=" << s.bus_delay_ns
                      << " нс, Зсув=" << s.offset_ns << " нс\n";
        }
    }
    return 0;
}
