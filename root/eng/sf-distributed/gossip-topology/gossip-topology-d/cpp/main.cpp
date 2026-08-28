#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <span>
#include <memory>
#include <algorithm>

struct Endpoint {
    std::string id;
    std::string datacenter;
    std::string rack;
};

class LocalityAwarePeerSelector {
public:
    LocalityAwarePeerSelector(Endpoint local_node, double p_rack, double p_dc, double p_remote)
        : self_(std::move(local_node)),
          p_rack_(p_rack),
          p_dc_(p_dc),
          p_remote_(p_remote),
          rng_(std::random_device{}()) {}

    void UpdatePeerList(std::vector<Endpoint> peers) {
        same_rack_.clear();
        same_dc_.clear();
        remote_dc_.clear();

        for (auto& peer : peers) {
            if (peer.id == self_.id) continue;

            if (peer.datacenter != self_.datacenter) {
                remote_dc_.push_back(peer);
            } else if (peer.rack != self_.rack) {
                same_dc_.push_back(peer);
            } else {
                same_rack_.push_back(peer);
            }
        }
    }

    std::vector<Endpoint> SelectTargets(size_t fanout) {
        std::vector<Endpoint> selected;
        selected.reserve(fanout);

        std::uniform_real_distribution<double> dist(0.0, 1.0);

        for (size_t i = 0; i < fanout; ++i) {
            double roll = dist(rng_);

            if (roll < p_rack_ && !same_rack_.empty()) {
                selected.push_back(pick_random(same_rack_));
            } else if (roll < (p_rack_ + p_dc_) && !same_dc_.empty()) {
                selected.push_back(pick_random(same_dc_));
            } else if (!remote_dc_.empty()) {
                selected.push_back(pick_random(remote_dc_));
            } else if (!same_dc_.empty()) {
                selected.push_back(pick_random(same_dc_));
            } else if (!same_rack_.empty()) {
                selected.push_back(pick_random(same_rack_));
            }
        }
        return selected;
    }

private:
    Endpoint pick_random(const std::vector<Endpoint>& pool) {
        std::uniform_int_distribution<size_t> idx_dist(0, pool.size() - 1);
        return pool[idx_dist(rng_)];
    }

    Endpoint self_;
    double p_rack_;
    double p_dc_;
    double p_remote_;
    std::mt19937 rng_;
    std::vector<Endpoint> same_rack_;
    std::vector<Endpoint> same_dc_;
    std::vector<Endpoint> remote_dc_;
};

int main() {
    Endpoint local{"node-1", "us-east-1", "rack-A"};
    LocalityAwarePeerSelector selector(local, 0.60, 0.35, 0.05);

    std::vector<Endpoint> cluster = {
        {"node-1", "us-east-1", "rack-A"},
        {"node-2", "us-east-1", "rack-A"},
        {"node-3", "us-east-1", "rack-B"},
        {"node-4", "eu-central-1", "rack-C"}
    };

    selector.UpdatePeerList(cluster);
    auto targets = selector.SelectTargets(2);

    for (const auto& t : targets) {
        std::cout << "Обрано партнера для пліток: " << t.id 
                  << " (" << t.datacenter << " / " << t.rack << ")\n";
    }
    return 0;
}
