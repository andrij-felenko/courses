class ScuttlebuttEngine {
public:
    explicit ScuttlebuttEngine(std::string local_id, uint64_t initial_generation)
        : local_node_id_(std::move(local_id)) {
        cluster_state_[local_node_id_].generation = initial_generation;
    }

    void mutate_local_key(std::string_view key, std::string_view val) {
        cluster_state_[local_node_id_].update_attribute(key, val);
    }

    std::vector<GossipDigest> make_syn_digest() const {
        std::vector<GossipDigest> digests;
        digests.reserve(cluster_state_.size());
        for (const auto& [id, state] : cluster_state_) {
            digests.push_back(GossipDigest{id, state.generation, state.max_version});
        }
        return digests;
    }

    std::vector<GossipDelta> collect_deltas_for_peer(std::span<const GossipDigest> peer_digests) const {
        std::vector<GossipDelta> result;
        size_t approx_bytes = 0;

        // Швидка таблиця для пошуку знань партнера
        std::unordered_map<std::string_view, GossipDigest> peer_map;
        for (const auto& d : peer_digests) {
            peer_map[d.node_id] = d;
        }

        for (const auto& [node_id, state] : cluster_state_) {
            auto it = peer_map.find(node_id);
            std::vector<GossipDelta> node_deltas;

            if (it == peer_map.end() || state.generation > it->second.generation) {
                // Партнер не має стану взагалі або його покоління застаріло
                for (const auto& [k, v] : state.attributes) {
                    node_deltas.push_back(GossipDelta{node_id, state.generation, k, v.value, v.version});
                }
            } else if (state.generation == it->second.generation && state.max_version > it->second.max_version) {
                // Віддаємо тільки дельти, новіші за відому партнеру max_version
                for (const auto& [k, v] : state.attributes) {
                    if (v.version > it->second.max_version) {
                        node_deltas.push_back(GossipDelta{node_id, state.generation, k, v.value, v.version});
                    }
                }
            }

            // Обов'язкове сортування за зростанням версій (Prefix Invariance)
            std::sort(node_deltas.begin(), node_deltas.end(),
                      [](const GossipDelta& a, const GossipDelta& b) {
                          return a.version < b.version;
                      });

            // Пакування в межах MTU
            for (auto&& delta : node_deltas) {
                size_t item_size = sizeof(GossipDelta) + delta.key.size() + delta.value.size();
                if (approx_bytes + item_size > MTU_PAYLOAD_LIMIT) {
                    return result; // Зупиняємося на цілісній межі версії
                }
                approx_bytes += item_size;
                result.push_back(std::move(delta));
            }
        }

        return result;
    }

    void apply_deltas(std::span<const GossipDelta> deltas) {
        for (const auto& d : deltas) {
            auto& state = cluster_state_[d.node_id];
            
            if (d.generation > state.generation) {
                // Нова епоха: старий стан вузла повністю очищується
                state.generation = d.generation;
                state.max_version = d.version;
                state.attributes.clear();
                state.attributes[d.key] = VersionedValue{d.value, d.version};
            } else if (d.generation == state.generation) {
                // Оновлюємо атрибут, якщо його версія свіжіша
                auto attr_it = state.attributes.find(d.key);
                if (attr_it == state.attributes.end() || d.version > attr_it->second.version) {
                    state.attributes[d.key] = VersionedValue{d.value, d.version};
                    if (d.version > state.max_version) {
                        state.max_version = d.version;
                    }
                }
            }
        }
    }

    [[nodiscard]] uint64_t get_node_max_version(const std::string& node_id) const {
        auto it = cluster_state_.find(node_id);
        return (it != cluster_state_.end()) ? it->second.max_version : 0;
    }

private:
    std::string local_node_id_;
    std::unordered_map<std::string, EndpointState> cluster_state_;
};
