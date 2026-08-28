#include <iostream>
#include <vector>
#include <string_view>
#include <optional>

enum class LinkState {
    Disconnected,
    Searching,
    Connected,
    HandoffRequired
};

constexpr std::string_view to_string(LinkState state) noexcept {
    switch (state) {
        case LinkState::Disconnected:    return "DISCONNECTED";
        case LinkState::Searching:       return "SEARCHING";
        case LinkState::Connected:       return "CONNECTED";
        case LinkState::HandoffRequired: return "HANDOFF_REQUIRED";
    }
    return "UNKNOWN";
}

class RssiEvaluator {
public:
    struct Config {
        float alpha{0.2f};               // Коефіцієнт EMA (0.0 < alpha <= 1.0)
        float connectThresholdDbm{-80.0f};
        float disconnectThresholdDbm{-92.0f};
        float handoffMarginDbm{6.0f};
    };

    explicit RssiEvaluator(Config config) : config_(config) {}

    /**
     * @brief Обновити фільтр новим значенням RSSI
     * @return Поточне значення фільтрованого RSSI та оновлений стан
     */
    LinkState update(float rawRssiDbm, float neighborRssiDbm = -120.0f) noexcept {
        if (!filteredRssi_) {
            filteredRssi_ = rawRssiDbm;
        } else {
            *filteredRssi_ = (config_.alpha * rawRssiDbm) + ((1.0f - config_.alpha) * (*filteredRssi_));
        }

        const float currentRssi = *filteredRssi_;

        switch (currentState_) {
            case LinkState::Disconnected:
            case LinkState::Searching:
                if (currentRssi >= config_.connectThresholdDbm) {
                    currentState_ = LinkState::Connected;
                } else {
                    currentState_ = LinkState::Searching;
                }
                break;

            case LinkState::Connected:
                if (currentRssi < config_.disconnectThresholdDbm) {
                    currentState_ = LinkState::Disconnected;
                } else if (neighborRssiDbm > (currentRssi + config_.handoffMarginDbm)) {
                    currentState_ = LinkState::HandoffRequired;
                }
                break;

            case LinkState::HandoffRequired:
                if (neighborRssiDbm <= (currentRssi + config_.handoffMarginDbm)) {
                    currentState_ = LinkState::Connected;
                }
                break;
        }

        return currentState_;
    }

    [[nodiscard]] std::optional<float> filteredRssi() const noexcept {
        return filteredRssi_;
    }

    [[nodiscard]] LinkState state() const noexcept {
        return currentState_;
    }

private:
    Config config_;
    std::optional<float> filteredRssi_{std::nullopt};
    LinkState currentState_{LinkState::Disconnected};
};

int main() {
    RssiEvaluator evaluator({.alpha = 0.15f, .connectThresholdDbm = -80.0f, 
                             .disconnectThresholdDbm = -92.0f, .handoffMarginDbm = 6.0f});

    const std::vector<float> rawSamples = {
        -110.0f, -105.0f, -82.0f, -78.0f, -75.0f, -74.0f,
        -76.0f,  -90.0f,  -73.0f, -75.0f,
        -88.0f,  -94.0f,  -96.0f, -98.0f
    };

    std::cout << "Крок | Сирий (дБм) | Фільтрований (дБм) | Стан лінку\n";
    std::cout << "---------------------------------------------------\n";

    for (size_t i = 0; i < rawSamples.size(); ++i) {
        LinkState state = evaluator.update(rawSamples[i]);
        std::cout << " " << (i + 1) << "   | " 
                  << rawSamples[i] << "        | " 
                  << evaluator.filteredRssi().value_or(-120.0f) << "             | " 
                  << to_string(state) << "\n";
    }

    return 0;
}
