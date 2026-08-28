#include <iostream>
#include <vector>
#include <random>
#include <cstdint>
#include <iomanip>
#include <memory>
#include <numeric>
#include <algorithm>

class CsmaSimulator {
public:
    static constexpr int SlotTimeUs    = 9;
    static constexpr int SifsUs        = 16;
    static constexpr int DifsSlots     = 4;     // 34 мкс ≈ 4 слоти по 9 мкс
    static constexpr int PacketSlots   = 30;    // 1500 байтів на швидкості 54 Мбіт/с
    static constexpr int AckSlots      = 3;     // ACK + SIFS
    static constexpr int CwMin         = 15;
    static constexpr int CwMax         = 1023;
    static constexpr int MaxRetries    = 7;

    enum class State {
        WaitDifs,
        Backoff,
        Transmitting
    };

    struct Node {
        int id;
        State state{State::WaitDifs};
        int cw{CwMin};
        int backoffCounter{0};
        int difsCounter{DifsSlots};
        int retryCount{0};
        uint64_t successfulFrames{0};
        uint64_t collisionCount{0};

        Node(int nodeId, std::mt19937 &rng) : id(nodeId) {
            resetBackoff(rng);
        }

        void resetBackoff(std::mt19937 &rng) {
            std::uniform_int_distribution<int> dist(0, cw);
            backoffCounter = dist(rng);
            difsCounter = DifsSlots;
            state = State::WaitDifs;
        }

        void registerSuccess(std::mt19937 &rng) {
            successfulFrames++;
            cw = CwMin;
            retryCount = 0;
            resetBackoff(rng);
        }

        void registerCollision(std::mt19937 &rng) {
            collisionCount++;
            retryCount++;
            if (retryCount >= MaxRetries) {
                cw = CwMin;
                retryCount = 0;
            } else {
                cw = std::min(CwMax, (cw + 1) * 2 - 1);
            }
            resetBackoff(rng);
        }
    };

private:
    int numNodes_;
    uint64_t totalSlots_;
    std::mt19937 rng_;
    std::vector<Node> nodes_;

public:
    CsmaSimulator(int numNodes, uint64_t totalSlots, unsigned int seed = 42)
        : numNodes_(numNodes), totalSlots_(totalSlots), rng_(seed) {
        nodes_.reserve(numNodes_);
        for (int i = 0; i < numNodes_; ++i) {
            nodes_.emplace_back(i, rng_);
        }
    }

    void run() {
        uint64_t channelBusyUntilSlot = 0;
        uint64_t totalSuccessfulFrames = 0;
        uint64_t totalCollisions = 0;
        uint64_t channelBusySlots = 0;

        for (uint64_t currentSlot = 0; currentSlot < totalSlots_; ++currentSlot) {
            const bool channelBusy = (currentSlot < channelBusyUntilSlot);
            if (channelBusy) {
                channelBusySlots++;
            }

            std::vector<int> transmittingNodes;

            if (!channelBusy) {
                for (int i = 0; i < numNodes_; ++i) {
                    auto &n = nodes_[i];
                    if (n.state == State::WaitDifs) {
                        if (--n.difsCounter <= 0) {
                            n.state = State::Backoff;
                        }
                    } else if (n.state == State::Backoff) {
                        if (n.backoffCounter == 0) {
                            transmittingNodes.push_back(i);
                        } else {
                            n.backoffCounter--;
                        }
                    }
                }
            } else {
                // Канал зайнятий: станції скидають лічильник DIFS і заморожують backoff
                for (auto &n : nodes_) {
                    if (n.state == State::WaitDifs) {
                        n.difsCounter = DifsSlots;
                    }
                }
            }

            if (transmittingNodes.size() == 1) {
                // Успішна передача рівно однієї станції
                int winnerIdx = transmittingNodes.front();
                nodes_[winnerIdx].registerSuccess(rng_);
                totalSuccessfulFrames++;
                channelBusyUntilSlot = currentSlot + PacketSlots + AckSlots;
            } else if (transmittingNodes.size() > 1) {
                // Колізія між кількома станціями
                totalCollisions++;
                for (int idx : transmittingNodes) {
                    nodes_[idx].registerCollision(rng_);
                }
                channelBusyUntilSlot = currentSlot + PacketSlots;
            }
        }

        printReport(totalSuccessfulFrames, totalCollisions, channelBusySlots);
    }

private:
    double calculateJainsFairness() const {
        double sum = 0.0;
        double sumSq = 0.0;
        for (const auto &n : nodes_) {
            double x = static_cast<double>(n.successfulFrames);
            sum += x;
            sumSq += x * x;
        }
        if (sumSq == 0.0) return 1.0;
        return (sum * sum) / (nodes_.size() * sumSq);
    }

    void printReport(uint64_t success, uint64_t collisions, uint64_t busySlots) const {
        double busyRatio = (static_cast<double>(busySlots) / totalSlots_) * 100.0;
        double goodputRatio = (static_cast<double>(success * PacketSlots) / totalSlots_) * 100.0;
        double jainIndex = calculateJainsFairness();

        std::cout << "=== Результати симуляції CSMA/CA (C++) ===\n"
                  << "Кількість вузлів:        " << numNodes_ << "\n"
                  << "Загалом слотів:          " << totalSlots_ << "\n"
                  << "Успішних кадрів:         " << success << "\n"
                  << "Кількість колізій:       " << collisions << "\n"
                  << std::fixed << std::setprecision(2)
                  << "Зайнятість каналу:       " << busyRatio << "%\n"
                  << "Корисна ємність ефіру:   " << goodputRatio << "%\n"
                  << std::setprecision(4)
                  << "Індекс справедливості:   " << jainIndex << " (Jain's Index)\n";
    }
};

int main() {
    CsmaSimulator sim(10, 500'000);
    sim.run();
    return 0;
}
