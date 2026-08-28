#include <string>
#include <vector>
#include <chrono>
#include <cstdint>
#include <optional>

namespace fleet::release {

enum class CampaignStatus {
    Draft,
    Scheduled,
    InProgress,
    Soaking,
    PausedStopTheLine,
    Aborted,
    Completed
};

enum class BreachAction {
    PauseAndAlert,
    EmergencyRollback,
    Abort
};

struct TargetPackageSpec {
    std::string version;
    std::string artifactUrl;
    std::string sha256;
    std::string signature;
    std::string minSourceVersion;
    std::string maxSourceVersion;
    uint32_t securityPatchLevel{0};
};

struct EligibilitySpec {
    std::vector<std::string> hardwareRevisions;
    uint32_t minBatteryPct{50};
    bool requireExternalPower{false};
    uint64_t minFreeStorageBytes{64 * 1024 * 1024};
    std::vector<std::string> allowedNetworks;
};

struct StopTheLinePolicy {
    uint32_t minSampleSize{100};
    std::chrono::seconds heartbeatTimeout{3600};
    std::chrono::seconds evaluationWindow{7200};
    double maxFailureRatePct{1.0};
    double maxRollbackRatePct{0.5};
    double maxSilenceRatePct{0.2};
    BreachAction actionOnBreach{BreachAction::PauseAndAlert};
};

struct WaveSpec {
    std::string name;
    double targetPercentage{0.0};
    uint32_t maxInFlight{100};
    std::chrono::seconds soakDuration{0};
    uint8_t utcHourStart{0};
    uint8_t utcHourEnd{24};
};

struct FleetCampaignSpec {
    std::string campaignId;
    std::string title;
    std::chrono::system_clock::time_point createdAt;
    TargetPackageSpec package;
    EligibilitySpec eligibility;
    StopTheLinePolicy stopPolicy;
    std::vector<WaveSpec> waves;
    uint32_t globalMaxInFlight{1000};
    double tokenBucketRatePerSec{50.0};
    std::chrono::seconds leaseTimeout{1800};
};

} // namespace fleet::release
