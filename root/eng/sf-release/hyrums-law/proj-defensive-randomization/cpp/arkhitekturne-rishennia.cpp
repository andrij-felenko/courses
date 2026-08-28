#include <algorithm>
#include <chrono>
#include <cstdint>
#include <random>
#include <span>
#include <string>
#include <string_view>
#include <vector>

struct ClusterNode {
    std::string name;
    int         load_percent{0};
    uint32_t    node_id{0};
};

class NodeRegistry {
public:
    explicit NodeRegistry(bool defensive_mode = true, uint32_t custom_seed = 0)
        : defensive_mode_{defensive_mode},
          rng_{custom_seed != 0 ? custom_seed : static_cast<std::mt19937::result_type>(
              std::chrono::steady_clock::now().time_since_epoch().count())} {}

    bool add_node(std::string_view name, int load, uint32_t id) {
        nodes_.push_back(ClusterNode{std::string(name), load, id});
        return true;
    }

    /* Повертає знімок вузлів. Якщо увімкнено захисний режим,
       порядок свідомо тасується для унеможливлення неявного зв'язування */
    [[nodiscard]] std::vector<ClusterNode> get_active_nodes() {
        std::vector<ClusterNode> snapshot = nodes_;
        if (defensive_mode_ && snapshot.size() > 1) {
            std::shuffle(snapshot.begin(), snapshot.end(), rng_);
        }
        return snapshot;
    }

    [[nodiscard]] size_t size() const noexcept {
        return nodes_.size();
    }

private:
    std::vector<ClusterNode> nodes_;
    bool                     defensive_mode_{true};
    std::mt19937             rng_;
};
