#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <memory>
#include <cstdint>
#include <algorithm>

namespace alerting {

using Clock = std::chrono::steady_clock;
using TimePoint = Clock::time_point;
using Seconds = std::chrono::seconds;

enum class AlertState {
    Inactive,
    Pending,
    Firing,
    Resolved
};

std::string_view stateToString(AlertState state) {
    switch (state) {
        case AlertState::Inactive: return "INACTIVE";
        case AlertState::Pending:  return "PENDING";
        case AlertState::Firing:   return "FIRING";
        case AlertState::Resolved: return "RESOLVED";
    }
    return "UNKNOWN";
}

// 64-бітне детерміноване FNV-1a хешування міток (Fingerprint)
uint64_t computeFingerprint(const std::unordered_map<std::string, std::string>& labels) {
    std::vector<std::pair<std::string_view, std::string_view>> sortedLabels;
    sortedLabels.reserve(labels.size());
    for (const auto& [k, v] : labels) {
        sortedLabels.emplace_back(k, v);
    }
    // Лексикографічне сортування обов'язкове для стабільності хешу
    std::sort(sortedLabels.begin(), sortedLabels.end());

    uint64_t hash = 0xcbf29ce484222325ULL;
    constexpr uint64_t prime = 0x100000001b3ULL;

    for (const auto& [k, v] : sortedLabels) {
        for (char c : k) { hash ^= static_cast<uint8_t>(c); hash *= prime; }
        hash ^= 0xff; hash *= prime; // байт-розділювач між ключем і значенням
        for (char c : v) { hash ^= static_cast<uint8_t>(c); hash *= prime; }
        hash ^= 0xfe; hash *= prime; // байт-розділювач між парами
    }
    return hash;
}

struct AlertRule {
    std::string name;
    std::unordered_map<std::string, std::string> labels;
    std::unordered_map<std::string, std::string> annotations;
    Seconds forDuration;
    AlertState state{AlertState::Inactive};
    TimePoint stateChangeTime{};
    uint64_t fingerprint{0};

    AlertRule(std::string ruleName, 
              std::unordered_map<std::string, std::string> lbls,
              std::unordered_map<std::string, std::string> annos,
              Seconds duration)
        : name(std::move(ruleName)),
          labels(std::move(lbls)),
          annotations(std::move(annos)),
          forDuration(duration) {
        labels["alertname"] = name;
        fingerprint = computeFingerprint(labels);
    }

    void evaluate(bool conditionMet, TimePoint now, const auto& notifyCallback) {
        switch (state) {
            case AlertState::Inactive:
                if (conditionMet) {
                    if (forDuration == Seconds(0)) {
                        state = AlertState::Firing;
                        stateChangeTime = now;
                        notifyCallback(*this, "Alert triggered immediately (for = 0)");
                    } else {
                        state = AlertState::Pending;
                        stateChangeTime = now;
                    }
                }
                break;

            case AlertState::Pending:
                if (!conditionMet) {
                    state = AlertState::Inactive;
                    stateChangeTime = now;
                } else if (now - stateChangeTime >= forDuration) {
                    state = AlertState::Firing;
                    stateChangeTime = now;
                    notifyCallback(*this, "Condition sustained across for-duration");
                }
                break;

            case AlertState::Firing:
                if (!conditionMet) {
                    state = AlertState::Resolved;
                    stateChangeTime = now;
                    notifyCallback(*this, "Metric recovered to normal state");
                    state = AlertState::Inactive;
                }
                break;

            case AlertState::Resolved:
                state = conditionMet ? AlertState::Pending : AlertState::Inactive;
                stateChangeTime = now;
                break;
        }
    }
};

struct InhibitionRule {
    std::string sourceAlertName;
    std::string targetAlertName;
    std::vector<std::string> equalLabels; // мітки, які мають збігатися

    bool suppresses(const AlertRule& source, const AlertRule& target) const {
        if (source.state != AlertState::Firing) return false;
        if (source.name != sourceAlertName || target.name != targetAlertName) return false;

        for (const auto& lbl : equalLabels) {
            auto itSrc = source.labels.find(lbl);
            auto itTgt = target.labels.find(lbl);
            if (itSrc == source.labels.end() || itTgt == target.labels.end()) return false;
            if (itSrc->second != itTgt->second) return false;
        }
        return true;
    }
};

class AlertEngine {
private:
    std::vector<std::unique_ptr<AlertRule>> rules_;
    std::vector<InhibitionRule> inhibitionRules_;

public:
    void addRule(std::unique_ptr<AlertRule> rule) {
        rules_.push_back(std::move(rule));
    }

    void addInhibition(InhibitionRule rule) {
        inhibitionRules_.push_back(std::move(rule));
    }

    void process(const std::unordered_map<std::string, bool>& conditions, TimePoint now) {
        auto notify = [this](const AlertRule& firingRule, std::string_view reason) {
            // Перевірка правил інгібування перед відправкою сповіщення
            for (const auto& inh : inhibitionRules_) {
                for (const auto& other : rules_) {
                    if (inh.suppresses(*other, firingRule)) {
                        std::cout << "[SUPPRESSED] Alert '" << firingRule.name 
                                  << "' inhibited by parent '" << other->name << "'\n";
                        return;
                    }
                }
            }

            std::cout << "[DISPATCH] Alert: " << firingRule.name 
                      << " | State: " << stateToString(firingRule.state)
                      << " | Fingerprint: " << std::hex << firingRule.fingerprint << std::dec
                      << " | Reason: " << reason << "\n";
        };

        for (auto& rule : rules_) {
            auto it = conditions.find(rule->name);
            bool isMet = (it != conditions.end() && it->second);
            rule->evaluate(isMet, now, notify);
        }
    }
};

} // namespace alerting

int main() {
    using namespace alerting;
    AlertEngine engine;

    // Реєструємо батьківське правило (NodeDown) та дочірнє (InstanceHighLatency)
    engine.addRule(std::make_unique<AlertRule>(
        "NodeDown",
        std::unordered_map<std::string, std::string>{{"cluster", "prod-eu"}, {"node", "node-01"}},
        std::unordered_map<std::string, std::string>{{"summary", "Host is unreachable"}},
        Seconds(2)
    ));

    engine.addRule(std::make_unique<AlertRule>(
        "InstanceHighLatency",
        std::unordered_map<std::string, std::string>{{"cluster", "prod-eu"}, {"node", "node-01"}},
        std::unordered_map<std::string, std::string>{{"summary", "API latency p99 > 500ms"}},
        Seconds(2)
    ));

    // Правило інгібування: NodeDown глушить InstanceHighLatency на тому ж вузлі
    engine.addInhibition(InhibitionRule{
        .sourceAlertName = "NodeDown",
        .targetAlertName = "InstanceHighLatency",
        .equalLabels = {"cluster", "node"}
    });

    auto now = Clock::now();
    std::cout << "--- Крок 1: Початок збою (Latency + NodeDown у стані PENDING) ---\n";
    engine.process({{"NodeDown", true}, {"InstanceHighLatency", true}}, now);

    now += Seconds(3);
    std::cout << "\n--- Крок 2: Час минув (Обидва перейшли в FIRING, але Latency інгібовано) ---\n";
    engine.process({{"NodeDown", true}, {"InstanceHighLatency", true}}, now);

    now += Seconds(5);
    std::cout << "\n--- Крок 3: Вузол відновився (NodeDown RESOLVED) ---\n";
    engine.process({{"NodeDown", false}, {"InstanceHighLatency", false}}, now);

    return 0;
}
