#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>
#include <span>
#include <numeric>

struct VectorEntry {
    int id{0};
    std::vector<float> data;
};

struct Cluster {
    std::vector<float> centroid;
    std::vector<VectorEntry> entries;
};

class IvfFlatIndex {
public:
    explicit IvfFlatIndex(int dimension, size_t num_clusters)
        : dim_(dimension), clusters_(num_clusters) {
        for (auto& cl : clusters_) {
            cl.centroid.resize(dim_, 0.0f);
        }
    }

    void set_centroid(size_t cluster_idx, std::span<const float> centroid_coords) {
        if (cluster_idx < clusters_.size() && centroid_coords.size() == static_cast<size_t>(dim_)) {
            std::copy(centroid_coords.begin(), centroid_coords.end(), clusters_[cluster_idx].centroid.begin());
        }
    }

    void add_vector(int id, std::span<const float> vec, size_t cluster_idx) {
        if (cluster_idx < clusters_.size()) {
            clusters_[cluster_idx].entries.push_back(VectorEntry{id, {vec.begin(), vec.end()}});
        }
    }

    [[nodiscard]] std::pair<int, float> search_nearest(std::span<const float> query, size_t n_probe) const {
        if (clusters_.empty()) return {-1, std::numeric_limits<float>::infinity()};
        n_probe = std::min(n_probe, clusters_.size());

        // 1. Обчислюємо відстані до всіх центроїдів
        std::vector<std::pair<float, size_t>> centroid_dists;
        centroid_dists.reserve(clusters_.size());

        for (size_t i = 0; i < clusters_.size(); ++i) {
            centroid_dists.emplace_back(l2_sq(query, clusters_[i].centroid), i);
        }

        // 2. Часткове сортування: знаходимо n_probe найкращих кластерів
        std::nth_element(centroid_dists.begin(), centroid_dists.begin() + n_probe, centroid_dists.end());

        // 3. Скануємо вектори лише відібраних кластерів
        int best_id = -1;
        float best_dist_sq = std::numeric_limits<float>::max();

        for (size_t p = 0; p < n_probe; ++p) {
            const auto& cluster = clusters_[centroid_dists[p].second];
            for (const auto& entry : cluster.entries) {
                float d = l2_sq(query, entry.data);
                if (d < best_dist_sq) {
                    best_dist_sq = d;
                    best_id = entry.id;
                }
            }
        }

        return {best_id, std::sqrt(best_dist_sq)};
    }

private:
    int dim_{0};
    std::vector<Cluster> clusters_;

    [[nodiscard]] static float l2_sq(std::span<const float> a, std::span<const float> b) noexcept {
        float sum = 0.0f;
        for (size_t i = 0; i < a.size(); ++i) {
            float diff = a[i] - b[i];
            sum += diff * diff;
        }
        return sum;
    }
};
