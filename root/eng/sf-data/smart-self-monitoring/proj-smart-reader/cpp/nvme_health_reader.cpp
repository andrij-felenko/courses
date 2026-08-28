// nvme_health_reader.cpp — Ідіоматична C++ реалізація зчитування NVMe Health Log
#include <iostream>
#include <iomanip>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>

namespace storage::nvme {

#pragma pack(push, 1)
struct SmartLogPage {
    uint8_t  critical_warning;
    uint16_t temperature;
    uint8_t  avail_spare;
    uint8_t  spare_thresh;
    uint8_t  percent_used;
    uint8_t  endu_grp_crit_warn_sumry;
    uint8_t  rsvd6[25];
    uint8_t  data_units_read[16];
    uint8_t  data_units_written[16];
    uint8_t  host_reads[16];
    uint8_t  host_writes[16];
    uint8_t  ctrl_busy_time[16];
    uint8_t  power_cycles[16];
    uint8_t  power_on_hours[16];
    uint8_t  unsafe_shutdowns[16];
    uint8_t  media_errors[16];
    uint8_t  num_err_log_entries[16];
    uint32_t warning_temp_time;
    uint32_t critical_comp_time;
    uint16_t temp_sensor[8];
    uint8_t  rsvd232[280];
};
#pragma pack(pop)

struct HealthReport {
    uint8_t  critical_warning_raw;
    bool     spare_below_threshold;
    bool     temperature_exceeded;
    bool     reliability_degraded;
    bool     read_only_mode;
    bool     backup_device_failed;
    double   temperature_celsius;
    uint8_t  available_spare_pct;
    uint8_t  spare_threshold_pct;
    uint8_t  percentage_used_pct;
    uint64_t data_units_written_gb;
    uint64_t data_units_read_gb;
    uint64_t media_integrity_errors;
    uint64_t unsafe_shutdowns;
    uint64_t power_on_hours;
};

class NvmeHealthScanner {
    static uint64_t unpack_u128_low(const uint8_t buf[16]) noexcept {
        uint64_t val = 0;
        for (int i = 0; i < 8; ++i) {
            val |= static_cast<uint64_t>(buf[i]) << (i * 8);
        }
        return val;
    }

public:
    static std::expected<HealthReport, std::error_code>
    query_controller(std::string_view controller_path) {
        int fd = ::open(controller_path.data(), O_RDONLY);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        SmartLogPage log{};
        nvme_admin_cmd cmd{};
        cmd.opcode   = 0x02;        // Get Log Page
        cmd.nsid     = 0xFFFFFFFF;  // Global Controller
        cmd.addr     = reinterpret_cast<uint64_t>(&log);
        cmd.data_len = sizeof(log);
        cmd.cdw10    = 0x02 | (127 << 16); // Log ID 0x02, 127 dwords

        int ioctl_res = ::ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd);
        ::close(fd);

        if (ioctl_res < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        uint64_t wr_units = unpack_u128_low(log.data_units_written);
        uint64_t rd_units = unpack_u128_low(log.data_units_read);

        return HealthReport{
            .critical_warning_raw   = log.critical_warning,
            .spare_below_threshold  = (log.critical_warning & (1 << 0)) != 0,
            .temperature_exceeded   = (log.critical_warning & (1 << 1)) != 0,
            .reliability_degraded   = (log.critical_warning & (1 << 2)) != 0,
            .read_only_mode         = (log.critical_warning & (1 << 3)) != 0,
            .backup_device_failed   = (log.critical_warning & (1 << 4)) != 0,
            .temperature_celsius    = static_cast<double>(log.temperature) - 273.15,
            .available_spare_pct    = log.avail_spare,
            .spare_threshold_pct    = log.spare_thresh,
            .percentage_used_pct    = log.percent_used,
            .data_units_written_gb  = (wr_units * 512000) / (1024 * 1024 * 1024),
            .data_units_read_gb     = (rd_units * 512000) / (1024 * 1024 * 1024),
            .media_integrity_errors = unpack_u128_low(log.media_errors),
            .unsafe_shutdowns       = unpack_u128_low(log.unsafe_shutdowns),
            .power_on_hours         = unpack_u128_low(log.power_on_hours)
        };
    }
};

} // namespace storage::nvme

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " /dev/nvme0\n";
        return EXIT_FAILURE;
    }

    auto report = storage::nvme::NvmeHealthScanner::query_controller(argv[1]);
    if (!report) {
        std::cerr << "Помилка опитування контролера: " << report.error().message() << "\n";
        return EXIT_FAILURE;
    }

    std::cout << "=== Стан здоров'я NVMe пристрою " << argv[1] << " ===\n";
    std::cout << "Температура:             " << std::fixed << std::setprecision(1)
              << report->temperature_celsius << " °C\n";
    std::cout << "Залишок резерву (Spare): " << static_cast<int>(report->available_spare_pct)
              << "% (Поріг: " << static_cast<int>(report->spare_threshold_pct) << "%)\n";
    std::cout << "Знос ресурсу (Used):     " << static_cast<int>(report->percentage_used_pct) << "%\n";
    std::cout << "Записано даних:          " << report->data_units_written_gb << " ГБ\n";
    std::cout << "Прочитано даних:         " << report->data_units_read_gb << " ГБ\n";
    std::cout << "Помилки медіа/ECC:       " << report->media_integrity_errors << "\n";
    std::cout << "Аварійні вимкнення:      " << report->unsafe_shutdowns << "\n";
    std::cout << "Години роботи:           " << report->power_on_hours << " год\n";

    if (report->critical_warning_raw != 0) {
        std::cout << "\n[!] КРИТИЧНІ ПОПЕРЕДЖЕННЯ:\n";
        if (report->spare_below_threshold) std::cout << "  - Резервні блоки вичерпано!\n";
        if (report->temperature_exceeded)  std::cout << "  - Критичний перегрів пристрою!\n";
        if (report->reliability_degraded)  std::cout << "  - Надійність масиву деградувала!\n";
        if (report->read_only_mode)        std::cout << "  - Диск заблоковано в режимі Read-Only!\n";
        if (report->backup_device_failed)  std::cout << "  - Відмовила батарея/конденсатор кешу!\n";
    }

    return EXIT_SUCCESS;
}
