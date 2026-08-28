#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <optional>
#include <memory>
#include <stdexcept>

enum class ActionType {
    NOOP,
    CREATE,
    UPDATE,
    REPLACE,
    DESTROY
};

struct Resource {
    std::string type;
    std::string name;
    std::unordered_map<std::string, std::string> props;
    std::vector<std::string> deps;
    std::unordered_set<std::string> immutable_keys;

    [[nodiscard]] std::string urn() const {
        return type + "." + name;
    }
};

struct ResourceState {
    std::string urn;
    std::string physical_id;
    std::unordered_map<std::string, std::string> props;
};

struct PlanItem {
    std::string urn;
    ActionType action;
    std::unordered_map<std::string, std::string> old_props;
    std::unordered_map<std::string, std::string> new_props;
    std::string physical_id;
};

class MockCloudProvider {
private:
    std::unordered_map<std::string, std::unordered_map<std::string, std::string>> resources_;
    int id_counter_{1000};

public:
    std::string create_resource(const std::string& type, const std::unordered_map<std::string, std::string>& props) {
        id_counter_++;
        std::string id = type + "-" + std::to_string(id_counter_);
        resources_[id] = props;
        return id;
    }

    void update_resource(const std::string& id, const std::unordered_map<std::string, std::string>& props) {
        auto it = resources_.find(id);
        if (it == resources_.end()) {
            throw std::runtime_error("Хмарний ресурс " + id + " не знайдено");
        }
        for (const auto& [k, v] : props) {
            it->second[k] = v;
        }
    }

    void delete_resource(const std::string& id) {
        resources_.erase(id);
    }

    std::optional<std::unordered_map<std::string, std::string>> read_resource(const std::string& id) const {
        auto it = resources_.find(id);
        if (it != resources_.end()) {
            return it->second;
        }
        return std::nullopt;
    }
};

class StateStore {
private:
    std::unordered_map<std::string, ResourceState> resources_;
    bool locked_{false};

public:
    bool acquire_lock() {
        if (locked_) return false;
        locked_ = true;
        return true;
    }

    void release_lock() {
        locked_ = false;
    }

    std::optional<ResourceState> get(const std::string& urn) const {
        auto it = resources_.find(urn);
        if (it != resources_.end()) return it->second;
        return std::nullopt;
    }

    void set(const ResourceState& state) {
        resources_[state.urn] = state;
    }

    void remove(const std::string& urn) {
        resources_.erase(urn);
    }

    const std::unordered_map<std::string, ResourceState>& all() const {
        return resources_;
    }
};

class IaCEngine {
private:
    std::shared_ptr<MockCloudProvider> provider_;
    std::shared_ptr<StateStore> state_;

public:
    IaCEngine(std::shared_ptr<MockCloudProvider> provider, std::shared_ptr<StateStore> state)
        : provider_(std::move(provider)), state_(std::move(state)) {}

    std::vector<std::string> build_dag_and_sort(const std::unordered_map<std::string, Resource>& desired) {
        std::unordered_map<std::string, int> in_degree;
        std::unordered_map<std::string, std::vector<std::string>> adj;

        for (const auto& [urn, _] : desired) {
            in_degree[urn] = 0;
            adj[urn] = {};
        }

        for (const auto& [urn, res] : desired) {
            for (const auto& dep : res.deps) {
                if (desired.find(dep) == desired.end()) {
                    throw std::runtime_error("Невідома залежність " + dep + " у " + urn);
                }
                adj[dep].push_back(urn);
                in_degree[urn]++;
            }
        }

        std::queue<std::string> queue;
        for (const auto& [urn, deg] : in_degree) {
            if (deg == 0) queue.push(urn);
        }

        std::vector<std::string> order;
        while (!queue.empty()) {
            std::string node = queue.front();
            queue.pop();
            order.push_back(node);

            for (const auto& neighbor : adj[node]) {
                in_degree[neighbor]--;
                if (in_degree[neighbor] == 0) {
                    queue.push(neighbor);
                }
            }
        }

        if (order.size() != desired.size()) {
            throw std::runtime_error("Виявлено циклічну залежність в графі (Circular Dependency)!");
        }

        return order;
    }
};
