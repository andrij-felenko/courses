#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>
#include <cstdint>
#include <memory>

namespace fleet::engine {

enum class DeviceState {
    Idle,
    Assigned,
    InFlight,
    Rebooting,
    Succeeded,
    Failed,
    RolledBack,
    Silenced
};

enum class EngineStatus {
    Running,
    Soaking,
    PausedStopTheLine,
    Completed
};

struct DeviceRecord {
    uint32_t deviceId{0};
    DeviceState state{DeviceState::Idle};
    std::chrono::system_clock::time_point stateUpdatedAt;
    std::chrono::system_clock::time_point leaseExpiresAt;
    size_t waveIndex{0};
};

struct WaveConfig {
    std::string name;
    double targetPct{0.0};
    uint32_t targetCount{0};
    uint32_t maxInFlight{100};
    std::chrono::seconds soakDuration{0};
    std::chrono::system_clock::time_point soakStartedAt{};
};

struct SafetyThresholds {
    double maxFailureRatePct{1.0};
    double maxRollbackRatePct{0.5};
    double maxSilenceRatePct{0.2};
    uint32_t minSampleSize{100};
    std::chrono::seconds heartbeatTimeout{3600};
};

class CampaignEngine {
public:
    CampaignEngine(uint32_t totalDevices, SafetyThresholds safety)
        : safety_(safety),
          status_(EngineStatus::Running),
          lastTokenRefill_(std::chrono::system_clock::now()) {
        
        devices_.reserve(totalDevices);
        auto now = std::chrono::system_clock::now();
        for (uint32_t i = 0; i < totalDevices; ++i) {
            devices_.push_back(DeviceRecord{
                .deviceId = 100000 + i,
                .state = DeviceState::Idle,
                .stateUpdatedAt = now,
                .leaseExpiresAt = now,
                .waveIndex = 0
            });
        }
    }

    void addWave(std::string name, double targetPct, uint32_t maxInFlight, std::chrono::seconds soakSec) {
        uint32_t targetCount = static_cast<uint32_t>(devices_.size() * (targetPct / 100.0));
        waves_.push_back(WaveConfig{
            .name = std::move(name),
            .targetPct = targetPct,
            .targetCount = targetCount,
            .maxInFlight = maxInFlight,
            .soakDuration = soakSec
        });
    }

    void reportDeviceEvent(size_t deviceIndex, DeviceState newState) {
        if (deviceIndex >= devices_.size()) return;
        auto& dev = devices_[deviceIndex];
        auto now = std::chrono::system_clock::now();

        if (dev.state == DeviceState::InFlight || dev.state == DeviceState::Rebooting) {
            if (inFlightCount_ > 0) inFlightCount_--;
        }

        dev.state = newState;
        dev.stateUpdatedAt = now;

        switch (newState) {
            case DeviceState::Succeeded:  succeededCount_++; break;
            case DeviceState::Failed:     failedCount_++; break;
            case DeviceState::RolledBack: rolledBackCount_++; break;
            default: break;
        }

        evaluateSafetyAndStopTheLine();
    }

    void tick() {
        if (status_ == EngineStatus::PausedStopTheLine || status_ == EngineStatus::Completed) {
            return;
        }

        auto now = std::chrono::system_clock::now();
        checkSilencedDevices(now);
        refillTokens(now);

        if (currentWave_ >= waves_.size()) return;
        auto& wave = waves_[currentWave_];

        uint32_t assignedInWave = 0;
        for (size_t i = 0; i < wave.targetCount && i < devices_.size(); ++i) {
            if (devices_[i].state == DeviceState::Idle) {
                tryAcquireToken(i, now);
            }
            if (devices_[i].state != DeviceState::Idle) {
                assignedInWave++;
            }
        }

        if (assignedInWave >= wave.targetCount && inFlightCount_ == 0) {
            if (status_ == EngineStatus::Running) {
                status_ = EngineStatus::Soaking;
                wave.soakStartedAt = now;
                std::cout << "[ХВИЛЯ] Хвиля '" << wave.name << "' перейшла у витримку.\n";
            } else if (status_ == EngineStatus::Soaking) {
                if (now - wave.soakStartedAt >= wave.soakDuration) {
                    if (currentWave_ + 1 < waves_.size()) {
                        currentWave_++;
                        status_ = EngineStatus::Running;
                        std::cout << "[ХВИЛЯ] Перехід на хвилю: " << waves_[currentWave_].name << "\n";
                    } else {
                        status_ = EngineStatus::Completed;
                        std::cout << "[ФІНІШ] Кампанію успішно завершено на 100% парку!\n";
                    }
                }
            }
        }
    }

    EngineStatus status() const noexcept { return status_; }

private:
    void refillTokens(std::chrono::system_clock::time_point now) {
        std::chrono::duration<double> elapsed = now - lastTokenRefill_;
        double delta = elapsed.count();
        if (delta > 0.0) {
            tokens_ = std::min(tokenCapacity_, tokens_ + delta * tokenFillRate_);
            lastTokenRefill_ = now;
        }
    }

    bool tryAcquireToken(size_t deviceIndex, std::chrono::system_clock::time_point now) {
        if (status_ != EngineStatus::Running) return false;
        const auto& wave = waves_[currentWave_];
        if (inFlightCount_ >= wave.maxInFlight || tokens_ < 1.0) return false;

        tokens_ -= 1.0;
        inFlightCount_++;
        devices_[deviceIndex].state = DeviceState::InFlight;
        devices_[deviceIndex].stateUpdatedAt = now;
        devices_[deviceIndex].leaseExpiresAt = now + std::chrono::seconds(1800);
        devices_[deviceIndex].waveIndex = currentWave_;
        return true;
    }

    void checkSilencedDevices(std::chrono::system_clock::time_point now) {
        for (auto& dev : devices_) {
            if (dev.state == DeviceState::Rebooting) {
                if (now - dev.stateUpdatedAt > safety_.heartbeatTimeout) {
                    dev.state = DeviceState::Silenced;
                    dev.stateUpdatedAt = now;
                    silencedCount_++;
                    if (inFlightCount_ > 0) inFlightCount_--;
                    evaluateSafetyAndStopTheLine();
                }
            }
        }
    }

    void evaluateSafetyAndStopTheLine() {
        uint32_t evaluated = succeededCount_ + failedCount_ + rolledBackCount_ + silencedCount_;
        if (evaluated < safety_.minSampleSize) return;

        double failRate = (static_cast<double>(failedCount_) / evaluated) * 100.0;
        double rbRate = (static_cast<double>(rolledBackCount_) / evaluated) * 100.0;
        double silenceRate = (static_cast<double>(silencedCount_) / evaluated) * 100.0;

        if (failRate > safety_.maxFailureRatePct ||
            rbRate > safety_.maxRollbackRatePct ||
            silenceRate > safety_.maxSilenceRatePct) {
            
            status_ = EngineStatus::PausedStopTheLine;
            std::cerr << "[STOP-THE-LINE] Аварійна зупинка! Відмови: " << failRate
                      << "%, Відкоти: " << rbRate << "%, Мовчання: " << silenceRate << "%\n";
        }
    }

    std::vector<DeviceRecord> devices_;
    std::vector<WaveConfig> waves_;
    size_t currentWave_{0};
    SafetyThresholds safety_;
    EngineStatus status_{EngineStatus::Running};

    double tokens_{100.0};
    double tokenFillRate_{20.0};
    double tokenCapacity_{100.0};
    std::chrono::system_clock::time_point lastTokenRefill_;

    uint32_t inFlightCount_{0};
    uint32_t succeededCount_{0};
    uint32_t failedCount_{0};
    uint32_t rolledBackCount_{0};
    uint32_t silencedCount_{0};
};

} // namespace fleet::engine
