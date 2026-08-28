#include <iostream>
#include <string>
#include <chrono>
#include <optional>
#include <memory>
#include <functional>
#include <unordered_map>

// Стан свіжості об'єкта в кеші
enum class FreshnessState {
    Fresh,              // Дані абсолютно актуальні (age <= ttl)
    StaleRevalidating,  // Застаріли, але у вікні грації: віддати кеш + оновити у фоні
    StaleDegraded,      // Застаріли понад грацію: показати UI деградації
    Expired             // Протухли остаточно, віддача заборонена
};

// Конверт даних із метаданими свіжості
template <typename T>
struct FreshnessEnvelope {
    T data;
    std::chrono::system_clock::time_point dataTimestamp;
    std::chrono::system_clock::time_point fetchedAt;
    std::chrono::milliseconds ttl;
    std::chrono::milliseconds staleGraceWindow;

    // Оцінити стан свіжості на поточний момент часу
    FreshnessState evaluateState(std::chrono::system_clock::time_point now) const {
        auto age = std::chrono::duration_cast<std::chrono::milliseconds>(now - fetchedAt);
        if (age <= ttl) {
            return FreshnessState::Fresh;
        } else if (age <= (ttl + staleGraceWindow)) {
            return FreshnessState::StaleRevalidating;
        } else if (age <= (ttl + staleGraceWindow * 5)) {
            return FreshnessState::StaleDegraded;
        }
        return FreshnessState::Expired;
    }

    int64_t getLagMs(std::chrono::system_clock::time_point now) const {
        return std::chrono::duration_cast<std::chrono::milliseconds>(now - dataTimestamp).count();
    }
};

// Структура телеметрії пристрою Digital Homes
struct DeviceTelemetry {
    std::string deviceId;
    double temperatureC;
    bool isOnline;
};

// Менеджер оптимістичного стану (Desired vs Reported)
class OptimisticStateEngine {
public:
    using RollbackCallback = std::function<void(const std::string& errorReason)>;

    struct DeviceState {
        bool reportedPowerState; // Підтверджений стан із БД/хаба
        std::optional<bool> desiredPowerState; // Оптимістичний намір користувача
        bool isPending{false};
    };

    void applyOptimisticChange(const std::string& deviceId, bool desiredState) {
        auto& state = m_states[deviceId];
        state.desiredPowerState = desiredState;
        state.isPending = true;
        std::cout << "[OptimisticUI] Device " << deviceId << " set pending desired: "
                  << (desiredState ? "ON" : "OFF") << std::endl;
    }

    void confirmState(const std::string& deviceId, bool confirmedState) {
        auto& state = m_states[deviceId];
        state.reportedPowerState = confirmedState;
        state.desiredPowerState.reset();
        state.isPending = false;
        std::cout << "[OptimisticUI] Device " << deviceId << " confirmed state: "
                  << (confirmedState ? "ON" : "OFF") << std::endl;
    }

    void rollbackChange(const std::string& deviceId, const std::string& reason) {
        auto& state = m_states[deviceId];
        state.desiredPowerState.reset();
        state.isPending = false;
        std::cout << "[OptimisticUI ROLLBACK] Device " << deviceId
                  << " reverted due to: " << reason << std::endl;
    }

    DeviceState getState(const std::string& deviceId) const {
        auto it = m_states.find(deviceId);
        if (it != m_states.end()) return it->second;
        return {false, std::nullopt, false};
    }

private:
    std::unordered_map<std::string, DeviceState> m_states;
};

int main() {
    using namespace std::chrono;
    auto now = system_clock::now();

    // Створюємо конверт застарілих даних (лаг 45 секунд при TTL 10 секунд)
    FreshnessEnvelope<DeviceTelemetry> env{
        DeviceTelemetry{"sensor-living-room", 22.4, true},
        now - seconds(45), // dataTimestamp
        now - seconds(25), // fetchedAt
        milliseconds(10000), // ttl: 10s
        milliseconds(30000)  // staleGraceWindow: 30s
    };

    FreshnessState state = env.evaluateState(now);
    std::cout << "Data Lag: " << env.getLagMs(now) << " ms" << std::endl;

    switch (state) {
        case FreshnessState::Fresh:
            std::cout << "UI Mode: STANDARD (Data is fresh)" << std::endl;
            break;
        case FreshnessState::StaleRevalidating:
            std::cout << "UI Mode: SWR (Show cache + trigger async revalidate)" << std::endl;
            break;
        case FreshnessState::StaleDegraded:
            std::cout << "UI Mode: DEGRADED (Show badge 'Updated 25s ago')" << std::endl;
            break;
        case FreshnessState::Expired:
            std::cout << "UI Mode: EXPIRED (Show error / placeholder)" << std::endl;
            break;
    }

    // Демонстрація оптимістичного оновлення та відкату
    OptimisticStateEngine optEngine;
    optEngine.applyOptimisticChange("light-kitchen", true);

    // Імітація збою сервера
    optEngine.rollbackChange("light-kitchen", "503 Gateway Timeout");

    return 0;
}
