#include <algorithm>
#include <chrono>
#include <cstdint>
#include <random>
#include <span>
#include <string>
#include <string_view>
#include <vector>

struct ServiceEndpoint {
    std::string name;
    uint32_t    priority{0};
};

class EndpointRegistry {
public:
    explicit EndpointRegistry(bool randomize_order = true)
        : randomize_order_{randomize_order},
          rng_{static_cast<std::mt19937::result_type>(
              std::chrono::steady_clock::now().time_since_epoch().count())} {}

    bool add_endpoint(std::string_view name, uint32_t priority) {
        endpoints_.push_back(ServiceEndpoint{std::string(name), priority});
        return true;
    }

    /* Повертає список точок доступу. Якщо увімкнено randomize_order,
       порядок свідомо тасується, унеможливлюючи неявне зв'язування клієнта */
    [[nodiscard]] std::vector<ServiceEndpoint> fetch_endpoints() {
        std::vector<ServiceEndpoint> snapshot = endpoints_;
        if (randomize_order_ && snapshot.size() > 1) {
            std::shuffle(snapshot.begin(), snapshot.end(), rng_);
        }
        return snapshot;
    }

private:
    std::vector<ServiceEndpoint> endpoints_;
    bool                         randomize_order_{true};
    std::mt19937                 rng_;
};
