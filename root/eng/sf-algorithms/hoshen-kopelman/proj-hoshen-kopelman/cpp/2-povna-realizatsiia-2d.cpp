#include <vector>
#include <span>
#include <cstdint>
#include <algorithm>
#include <memory>
#include <stdexcept>

/* Результат роботи алгоритму Гошена–Копельмана */
struct ClusterResult2D {
    std::vector<int> grid;            // Розмічена ґратка L x L (мітка 0 - порожньо, 1..K - кластери)
    std::vector<int> cluster_sizes;   // Розміри кластерів (індекси 1..K)
    int num_clusters{0};              // Загальна кількість кластерів
    int max_cluster_size{0};          // Розмір максимального кластера
    bool has_spanning_cluster{false}; // Наявність протікання між протилежними границями
};

/* Клас системи неперетинних множин з від'ємними коренями */
class HoshenKopelmanDSU {
public:
    explicit HoshenKopelmanDSU(size_t initial_capacity = 2048) {
        labels_.resize(std::max(initial_capacity, size_t{1024}), 0);
    }

    // Створення нового кластера розміру 1
    int make_cluster() {
        ++max_label_;
        if (max_label_ >= static_cast<int>(labels_.size())) {
            labels_.resize(labels_.size() * 2, 0);
        }
        labels_[max_label_] = -1; // -1 кодує розмір кластера 1
        return max_label_;
    }

    // Пошук кореня з двопрохідним стисненням шляхів
    int find_root(int x) {
        int root = x;
        while (labels_[root] > 0) {
            root = labels_[root];
        }
        int curr = x;
        while (curr != root) {
            int next = labels_[curr];
            labels_[curr] = root;
            curr = next;
        }
        return root;
    }

    // Злиття двох кластерів
    int union_roots(int root1, int root2) {
        if (root1 == root2) return root1;

        if (root1 > root2) {
            std::swap(root1, root2);
        }

        labels_[root1] += labels_[root2]; // Додаємо розміри
        labels_[root2] = root1;           // root2 підпорядковується root1
        return root1;
    }

    // Додавання одного сайту до кластера
    void add_site_to_root(int root) {
        labels_[root]--;
    }

    [[nodiscard]] int max_label() const noexcept { return max_label_; }
    [[nodiscard]] int raw_value(int k) const { return labels_[k]; }
    [[nodiscard]] bool is_root(int k) const { return labels_[k] < 0; }

private:
    std::vector<int> labels_;
    int max_label_{0};
};

/* Сучасна C++20 функція маркування кластерів на регулярній ґратці */
ClusterResult2D run_hoshen_kopelman_2d(std::span<const uint8_t> binary_grid, int width, int height) {
    if (static_cast<size_t>(width * height) != binary_grid.size() || width <= 0 || height <= 0) {
        throw std::invalid_argument("Некоректні розміри вхідної ґратки");
    }

    ClusterResult2D result;
    result.grid.resize(width * height, 0);

    HoshenKopelmanDSU dsu(static_cast<size_t>((width * height) / 4 + 32));

    std::vector<int> prev_row(width, 0);
    std::vector<int> curr_row(width, 0);

    // ПРОХІД 1: Растрове сканування з буфером O(W)
    for (int r = 0; r < height; ++r) {
        for (int c = 0; c < width; ++c) {
            uint8_t occupied = binary_grid[r * width + c];
            if (!occupied) {
                curr_row[c] = 0;
                result.grid[r * width + c] = 0;
                continue;
            }

            int top_label = (r > 0) ? prev_row[c] : 0;
            int left_label = (c > 0) ? curr_row[c - 1] : 0;

            if (top_label == 0 && left_label == 0) {
                // Випадок 1: Новий кластер
                int new_lbl = dsu.make_cluster();
                curr_row[c] = new_lbl;
                result.grid[r * width + c] = new_lbl;
            } else if (top_label > 0 && left_label == 0) {
                // Випадок 2: Успадкування Top
                int root = dsu.find_root(top_label);
                dsu.add_site_to_root(root);
                curr_row[c] = root;
                result.grid[r * width + c] = root;
            } else if (top_label == 0 && left_label > 0) {
                // Випадок 3: Успадкування Left
                int root = dsu.find_root(left_label);
                dsu.add_site_to_root(root);
                curr_row[c] = root;
                result.grid[r * width + c] = root;
            } else {
                // Випадок 4: Колізія міток
                int root_top = dsu.find_root(top_label);
                int root_left = dsu.find_root(left_label);

                if (root_top == root_left) {
                    dsu.add_site_to_root(root_top);
                    curr_row[c] = root_top;
                    result.grid[r * width + c] = root_top;
                } else {
                    int merged = dsu.union_roots(root_top, root_left);
                    dsu.add_site_to_root(merged);
                    curr_row[c] = merged;
                    result.grid[r * width + c] = merged;
                }
            }
        }
        prev_row = curr_row;
    }

    // ПРОХІД 2: Канонічна перенумерація та оцінка протікання
    std::vector<int> canonical_map(dsu.max_label() + 1, 0);
    int canonical_counter = 0;

    for (int k = 1; k <= dsu.max_label(); ++k) {
        if (dsu.is_root(k)) {
            canonical_map[k] = ++canonical_counter;
        }
    }

    result.num_clusters = canonical_counter;
    result.cluster_sizes.resize(canonical_counter + 1, 0);

    for (int k = 1; k <= dsu.max_label(); ++k) {
        if (dsu.is_root(k)) {
            int canon = canonical_map[k];
            int size = -dsu.raw_value(k);
            result.cluster_sizes[canon] = size;
            result.max_cluster_size = std::max(result.max_cluster_size, size);
        }
    }

    std::vector<bool> top_touch(canonical_counter + 1, false);
    std::vector<bool> bottom_touch(canonical_counter + 1, false);

    for (int r = 0; r < height; ++r) {
        for (int c = 0; c < width; ++c) {
            int raw_lbl = result.grid[r * width + c];
            if (raw_lbl > 0) {
                int root = dsu.find_root(raw_lbl);
                int canon = canonical_map[root];
                result.grid[r * width + c] = canon;

                if (r == 0) top_touch[canon] = true;
                if (r == height - 1) bottom_touch[canon] = true;
            }
        }
    }

    result.has_spanning_cluster = false;
    for (int i = 1; i <= canonical_counter; ++i) {
        if (top_touch[i] && bottom_touch[i]) {
            result.has_spanning_cluster = true;
            break;
        }
    }

    return result;
}
