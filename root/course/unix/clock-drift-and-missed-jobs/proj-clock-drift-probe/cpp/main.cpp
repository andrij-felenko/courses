#include <iostream>
#include <iomanip>
#include <chrono>
#include <string_view>
#include <system_error>
#include <thread>
#include <cstdint>
#include <cstring>
#include <sys/timex.h>
#include <unistd.h>

namespace timeprobe {

using nanoseconds = std::chrono::nanoseconds;

struct ClockSnapshot {
    std::chrono::system_clock::time_point realtime;
    std::chrono::steady_clock::time_point monotonic;
    nanoseconds monotonic_raw{0};
    nanoseconds boottime{0};
};

class KernelTimeInspector {
public:
    static void print_diagnostics() {
        timex tx{};
        tx.modes = 0; // Суто читання

        int state = ::adjtimex(&tx);
        if (state == -1) {
            throw std::system_error(errno, std::generic_category(), "Помилка виклику adjtimex");
        }

        std::cout << "=== СТАН ЯДЕРНОГО СИНХРОНІЗАТОРА TIMEKEEPING ===\n";
        std::cout << "  Код повернення Leap State : " << state << " " << decode_leap_state(state) << "\n";

        double freq_ppm = static_cast<double>(tx.freq) / 65536.0;
        double max_err_ms = static_cast<double>(tx.maxerror) / 1000.0;
        double est_err_ms = static_cast<double>(tx.esterror) / 1000.0;

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "  Частотна корекція (freq)  : " << freq_ppm << " ppm (сире: " << tx.freq << ")\n";
        std::cout << "  Фазовий зсув (offset)     : " << tx.offset << " " << ((tx.status & STA_NANO) ? "нс" : "мкс") << "\n";
        std::cout << std::setprecision(3);
        std::cout << "  Максимальна похибка       : " << max_err_ms << " мс\n";
        std::cout << "  Оцінена похибка           : " << est_err_ms << " мс\n";
        std::cout << "  Постійна часу контуру PLL : " << tx.constant << "\n";
        std::cout << "  Тривалість тика ядра      : " << tx.tick << " мкс\n";

        print_flags(tx.status);
    }

    static ClockSnapshot capture_snapshot() {
        timespec ts_real{}, ts_mono{}, ts_raw{}, ts_boot{};
        ::clock_gettime(CLOCK_REALTIME, &ts_real);
        ::clock_gettime(CLOCK_MONOTONIC, &ts_mono);
        ::clock_gettime(CLOCK_MONOTONIC_RAW, &ts_raw);
        ::clock_gettime(CLOCK_BOOTTIME, &ts_boot);

        ClockSnapshot snap{};
        snap.realtime = std::chrono::system_clock::time_point(
            std::chrono::seconds(ts_real.tv_sec) + std::chrono::nanoseconds(ts_real.tv_nsec));
        snap.monotonic = std::chrono::steady_clock::time_point(
            std::chrono::seconds(ts_mono.tv_sec) + std::chrono::nanoseconds(ts_mono.tv_nsec));
        snap.monotonic_raw = std::chrono::seconds(ts_raw.tv_sec) + std::chrono::nanoseconds(ts_raw.tv_nsec);
        snap.boottime = std::chrono::seconds(ts_boot.tv_sec) + std::chrono::nanoseconds(ts_boot.tv_nsec);
        return snap;
    }

private:
    static std::string_view decode_leap_state(int state) noexcept {
        switch (state) {
            case TIME_OK:    return "(TIME_OK: час синхронізовано)";
            case TIME_INS:   return "(TIME_INS: вставка leap second)";
            case TIME_DEL:   return "(TIME_DEL: видалення leap second)";
            case TIME_OOP:   return "(TIME_OOP: leap second у процесі)";
            case TIME_WAIT:  return "(TIME_WAIT: leap second завершено)";
            case TIME_ERROR: return "(TIME_ERROR: помилка синхронізації / STA_UNSYNC)";
            default:         return "(невідомий стан)";
        }
    }

    static void print_flags(int status) {
        std::cout << "  Прапорці стану (status=0x" << std::hex << std::uppercase
                  << std::setw(4) << std::setfill('0') << status << std::dec << std::setfill(' ') << "):\n";
        if (status & STA_PLL)       std::cout << "    [+] STA_PLL       (контур фазового автопідстроювання активний)\n";
        if (status & STA_FLL)       std::cout << "    [+] STA_FLL       (контур частотного автопідстроювання активний)\n";
        if (status & STA_UNSYNC)    std::cout << "    [!] STA_UNSYNC    (ГОДИННИК НЕ СИНХРОНІЗОВАНО! Запис у RTC вимкнено)\n";
        if (status & STA_PPSSIGNAL) std::cout << "    [+] STA_PPSSIGNAL (сигнал точного часу PPS виявлено)\n";
        if (status & STA_NANO)      std::cout << "    [+] STA_NANO      (роздільність зсуву в наносекундах)\n";
        if (status & STA_INS)       std::cout << "    [!] STA_INS       (заплановано додавання секунди координації)\n";
        if (status & STA_DEL)       std::cout << "    [!] STA_DEL       (заплановано віднімання секунди координації)\n";
    }
};

} // namespace timeprobe

int main(int argc, char **argv) {
    try {
        int duration_sec = 2;
        if (argc > 1) {
            duration_sec = std::max(1, std::atoi(argv[1]));
        }

        timeprobe::KernelTimeInspector::print_diagnostics();

        auto snap = timeprobe::KernelTimeInspector::capture_snapshot();
        auto mono_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(snap.monotonic.time_since_epoch()).count();
        auto raw_ns = snap.monotonic_raw.count();
        auto boot_ns = snap.boottime.count();

        std::cout << "\n=== ЗРІЗ СИСТЕМНИХ ГОДИННИКІВ ===\n";
        std::cout << "  CLOCK_MONOTONIC     : " << mono_ns << " нс\n";
        std::cout << "  CLOCK_MONOTONIC_RAW : " << raw_ns << " нс\n";
        std::cout << "  CLOCK_BOOTTIME      : " << boot_ns << " нс\n";

        auto raw_vs_mono = mono_ns - raw_ns;
        auto boot_vs_mono = boot_ns - mono_ns;

        std::cout << std::fixed << std::setprecision(3);
        std::cout << "  Різниця NTP Slew (MONO - RAW)     : " << raw_vs_mono << " нс ("
                  << (static_cast<double>(raw_vs_mono) / 1e6) << " мс)\n";
        std::cout << "  Час у сні/гібернації (BOOT - MONO): " << boot_vs_mono << " нс ("
                  << (static_cast<double>(boot_vs_mono) / 1e9) << " с)\n";

        std::cout << "\n=== ВИМІРЮВАННЯ ВЛАСНОГО АПАРАТНОГО ДРЕЙФУ (" << duration_sec << " с) ===\n";
        timespec m_start{}, r_start{};
        ::clock_gettime(CLOCK_MONOTONIC, &m_start);
        ::clock_gettime(CLOCK_MONOTONIC_RAW, &r_start);

        std::this_thread::sleep_for(std::chrono::seconds(duration_sec));

        timespec m_end{}, r_end{};
        ::clock_gettime(CLOCK_MONOTONIC, &m_end);
        ::clock_gettime(CLOCK_MONOTONIC_RAW, &r_end);

        int64_t d_mono = (static_cast<int64_t>(m_end.tv_sec - m_start.tv_sec) * 1000000000LL) + (m_end.tv_nsec - m_start.tv_nsec);
        int64_t d_raw  = (static_cast<int64_t>(r_end.tv_sec - r_start.tv_sec) * 1000000000LL) + (r_end.tv_nsec - r_start.tv_nsec);

        int64_t drift_ns = d_mono - d_raw;
        double drift_ppm = (static_cast<double>(drift_ns) / static_cast<double>(d_raw)) * 1e6;

        std::cout << "  Тривалість за CLOCK_MONOTONIC     : " << (static_cast<double>(d_mono) / 1e9) << " с\n";
        std::cout << "  Тривалість за CLOCK_MONOTONIC_RAW : " << (static_cast<double>(d_raw) / 1e9) << " с\n";
        std::cout << "  Накопичений зсув контуру NTP      : " << drift_ns << " нс\n";
        std::cout << std::setprecision(4);
        std::cout << "  Миттєва швидкість компенсації     : " << drift_ppm << " ppm\n";

    } catch (const std::exception &ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
