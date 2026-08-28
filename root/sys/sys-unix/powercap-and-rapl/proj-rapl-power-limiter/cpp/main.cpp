#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <atomic>
#include <system_error>
#include <csignal>
#include <fcntl.h>
#include <unistd.h>

namespace {
    std::atomic<bool> g_running{true};

    void signalHandler(int) noexcept {
        g_running.store(false);
    }
}

class RaplZone {
public:
    explicit RaplZone(std::string_view basePath) 
        : basePath_(basePath), fdEnergy_(-1), fdLimit_(-1), maxRangeUj_(0), prevEnergyUj_(0) {
        init();
    }

    ~RaplZone() {
        if (fdEnergy_ >= 0) ::close(fdEnergy_);
        if (fdLimit_ >= 0) ::close(fdLimit_);
    }

    RaplZone(const RaplZone&) = delete;
    RaplZone& operator=(const RaplZone&) = delete;

    RaplZone(RaplZone&& other) noexcept 
        : basePath_(std::move(other.basePath_)),
          fdEnergy_(other.fdEnergy_),
          fdLimit_(other.fdLimit_),
          maxRangeUj_(other.maxRangeUj_),
          prevEnergyUj_(other.prevEnergyUj_),
          prevTime_(other.prevTime_) {
        other.fdEnergy_ = -1;
        other.fdLimit_ = -1;
    }

    double readPowerWatts() {
        char buf[64];
        ssize_t bytes = ::pread(fdEnergy_, buf, sizeof(buf) - 1, 0);
        if (bytes <= 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка читання energy_uj");
        }
        buf[bytes] = '\0';
        
        auto now = std::chrono::steady_clock::now();
        uint64_t currEnergy = std::stoull(buf);

        uint64_t deltaEnergy = 0;
        if (currEnergy >= prevEnergyUj_) {
            deltaEnergy = currEnergy - prevEnergyUj_;
        } else {
            deltaEnergy = currEnergy + maxRangeUj_ - prevEnergyUj_;
        }

        auto deltaUs = std::chrono::duration_cast<std::chrono::microseconds>(now - prevTime_).count();
        prevEnergyUj_ = currEnergy;
        prevTime_ = now;

        if (deltaUs == 0) return 0.0;
        return static_cast<double>(deltaEnergy) / static_cast<double>(deltaUs);
    }

    void setPowerLimitWatts(double watts) {
        uint64_t limitUw = static_cast<uint64_t>(watts * 1'000'000.0);
        std::string payload = std::to_string(limitUw) + "\n";
        
        ssize_t bytes = ::pwrite(fdLimit_, payload.data(), payload.size(), 0);
        if (bytes != static_cast<ssize_t>(payload.size())) {
            throw std::system_error(errno, std::generic_category(), "Помилка запису ліміту потужності");
        }
    }

    [[nodiscard]] uint64_t maxRangeUj() const noexcept { return maxRangeUj_; }

private:
    void init() {
        std::string rangePath = basePath_ + "/max_energy_range_uj";
        std::ifstream rangeFile(rangePath);
        if (!rangeFile.is_open()) {
            throw std::runtime_error("Не вдалося відкрити " + rangePath);
        }
        rangeFile >> maxRangeUj_;

        std::string energyPath = basePath_ + "/energy_uj";
        fdEnergy_ = ::open(energyPath.c_str(), O_RDONLY);
        if (fdEnergy_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття " + energyPath);
        }

        std::string limitPath = basePath_ + "/constraint_0_power_limit_uw";
        fdLimit_ = ::open(limitPath.c_str(), O_WRONLY);
        if (fdLimit_ < 0) {
            ::close(fdEnergy_);
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття " + limitPath);
        }

        char buf[64];
        ssize_t bytes = ::pread(fdEnergy_, buf, sizeof(buf) - 1, 0);
        if (bytes > 0) {
            buf[bytes] = '\0';
            prevEnergyUj_ = std::stoull(buf);
        }
        prevTime_ = std::chrono::steady_clock::now();
    }

    std::string basePath_;
    int fdEnergy_;
    int fdLimit_;
    uint64_t maxRangeUj_;
    uint64_t prevEnergyUj_;
    std::chrono::steady_clock::time_point prevTime_;
};

int main() {
    std::signal(SIGINT, signalHandler);
    std::signal(SIGTERM, signalHandler);

    try {
        RaplZone zone("/sys/class/powercap/intel-rapl/intel-rapl:0");
        std::cout << "Ініціалізовано зону RAPL. Максимальний діапазон лічильника: " 
                  << (zone.maxRangeUj() / 1e6) << " Дж\n";

        zone.setPowerLimitWatts(45.0);
        std::cout << "Встановлено апаратний ліміт PL1 = 45.0 Вт\n";

        while (g_running.load()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
            double power = zone.readPowerWatts();
            std::cout << "Поточне споживання Package: " << power << " Вт\n";
        }
        std::cout << "Коректне завершення роботи.\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання сервісу: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
