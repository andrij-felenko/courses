#include <iostream>
#include <vector>
#include <random>
#include <memory>
#include <cstdint>
#include <iomanip>
#include <string_view>
#include <algorithm>

enum class StationState {
    Idle,
    Sensing,
    Transmitting,
    Jamming,
    Backoff
};

struct StationMetrics {
    uint64_t framesSentOk{0};
    uint64_t framesDropped{0};
    uint64_t collisionsTotal{0};
    uint64_t totalWaitSlots{0};
};

class Station {
public:
    explicit Station(uint32_t id) : id_(id) {}

    [[nodiscard]] uint32_t id() const noexcept { return id_; }
    [[nodiscard]] StationState state() const noexcept { return state_; }
    [[nodiscard]] const StationMetrics& metrics() const noexcept { return metrics_; }

    void triggerNewFrame(uint32_t lengthSlots) noexcept {
        if (state_ == StationState::Idle) {
            state_ = StationState::Sensing;
            attempts_ = 0;
            currentFrameLenSlots_ = lengthSlots;
        }
    }

    void startTransmission() noexcept {
        state_ = StationState::Transmitting;
        frameSlotsLeft_ = currentFrameLenSlots_;
    }

    void handleCollisionDetected() noexcept {
        metrics_.collisionsTotal++;
        state_ = StationState::Jamming;
    }

    void processSlot(uint32_t activeTransmittersOnBus, std::mt19937& rng) {
        constexpr uint32_t MaxAttempts = 16;
        constexpr uint32_t MaxBackoffExp = 10;

        switch (state_) {
        case StationState::Idle:
            break;

        case StationState::Sensing:
            metrics_.totalWaitSlots++;
            break;

        case StationState::Transmitting:
            if (activeTransmittersOnBus > 1) {
                handleCollisionDetected();
            } else {
                if (--frameSlotsLeft_ == 0) {
                    metrics_.framesSentOk++;
                    state_ = StationState::Idle;
                    attempts_ = 0;
                }
            }
            break;

        case StationState::Jamming: {
            attempts_++;
            if (attempts_ > MaxAttempts) {
                metrics_.framesDropped++;
                state_ = StationState::Idle;
                attempts_ = 0;
            } else {
                const uint32_t k = std::min(attempts_, MaxBackoffExp);
                const uint32_t maxRange = (1U << k) - 1;
                std::uniform_int_distribution<uint32_t> dist(0, maxRange);
                backoffSlotsLeft_ = dist(rng);
                state_ = StationState::Backoff;
            }
            break;
        }

        case StationState::Backoff:
            metrics_.totalWaitSlots++;
            if (backoffSlotsLeft_ == 0) {
                state_ = StationState::Sensing;
            } else {
                backoffSlotsLeft_--;
            }
            break;
        }
    }

private:
    uint32_t id_;
    StationState state_{StationState::Idle};
    uint32_t attempts_{0};
    uint32_t backoffSlotsLeft_{0};
    uint32_t frameSlotsLeft_{0};
    uint32_t currentFrameLenSlots_{1};
    StationMetrics metrics_;
};

class EthernetBusSimulator {
public:
    EthernetBusSimulator(uint32_t numStations, double loadProb, uint64_t totalSlots, uint32_t seed = 42)
        : totalSlots_(totalSlots), loadProb_(loadProb), rng_(seed), distArrival_(0.0, 1.0), distFrameLen_(1, 24) {
        stations_.reserve(numStations);
        for (uint32_t i = 0; i < numStations; ++i) {
            stations_.push_back(std::make_unique<Station>(i));
        }
    }

    void run() {
        for (uint64_t slot = 0; slot < totalSlots_; ++slot) {
            stepSlot();
        }
    }

    void printReport() const {
        const double total = static_cast<double>(totalSlots_);
        const double util = (static_cast<double>(busSuccessSlots_) / total) * 100.0;
        const double collRate = (static_cast<double>(busCollisionSlots_) / total) * 100.0;
        const double idleRate = (static_cast<double>(busIdleSlots_) / total) * 100.0;

        std::cout << "=== ЗВІТ СИМУЛЯЦІЇ СЕРЕДОВИЩА CSMA/CD (C++20) ===\n";
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Загальна кількість слотів:  " << totalSlots_ << " ("
                  << (totalSlots_ * 51.2) / 1'000'000.0 << " с ефірного часу)\n";
        std::cout << "Кількість станцій:          " << stations_.size() << "\n";
        std::cout << "Корисна утилізація шини:    " << util << "%\n";
        std::cout << "Частка колізійних слотів:   " << collRate << "%\n";
        std::cout << "Частка слотів простою:      " << idleRate << "%\n";
        std::cout << "--------------------------------------------------\n";
        std::cout << "ID   | Успішно  | Скинуто  | Колізій  | Сер. очікування\n";

        for (const auto& st : stations_) {
            const auto& m = st->metrics();
            const double avgWait = m.framesSentOk ? (static_cast<double>(m.totalWaitSlots) / m.framesSentOk) : 0.0;
            std::cout << "#" << std::setw(2) << std::setfill('0') << st->id() << "  | "
                      << std::setfill(' ') << std::setw(8) << m.framesSentOk << " | "
                      << std::setw(8) << m.framesDropped << " | "
                      << std::setw(8) << m.collisionsTotal << " | "
                      << avgWait << " слотів\n";
        }
    }

private:
    void stepSlot() {
        /* 1. Генерація трафіку для станцій Idle */
        for (auto& st : stations_) {
            if (st->state() == StationState::Idle && distArrival_(rng_) < loadProb_) {
                st->triggerNewFrame(distFrameLen_(rng_));
            }
        }

        /* 2. Визначення кандидатів на передачу (1-persistent) */
        uint32_t transmittingNow = 0;
        for (auto& st : stations_) {
            if (st->state() == StationState::Transmitting || st->state() == StationState::Jamming) {
                transmittingNow++;
            } else if (st->state() == StationState::Sensing && prevActiveTransmitters_ == 0) {
                st->startTransmission();
                transmittingNow++;
            }
        }

        /* 3. Статистика шини */
        if (transmittingNow == 0) {
            busIdleSlots_++;
        } else if (transmittingNow == 1) {
            busSuccessSlots_++;
        } else {
            busCollisionSlots_++;
        }
        prevActiveTransmitters_ = transmittingNow;

        /* 4. Оновлення стану кожної станції */
        for (auto& st : stations_) {
            st->processSlot(transmittingNow, rng_);
        }
    }

    uint64_t totalSlots_{0};
    double loadProb_{0.0};
    std::mt19937 rng_;
    std::uniform_real_distribution<double> distArrival_;
    std::uniform_int_distribution<uint32_t> distFrameLen_;
    std::vector<std::unique_ptr<Station>> stations_;

    uint32_t prevActiveTransmitters_{0};
    uint64_t busIdleSlots_{0};
    uint64_t busSuccessSlots_{0};
    uint64_t busCollisionSlots_{0};
};

int main() {
    constexpr uint32_t Stations = 10;
    constexpr double LoadProbability = 0.05;
    constexpr uint64_t SimulationSlots = 100'000;

    EthernetBusSimulator sim(Stations, LoadProbability, SimulationSlots);
    sim.run();
    sim.printReport();

    return 0;
}
