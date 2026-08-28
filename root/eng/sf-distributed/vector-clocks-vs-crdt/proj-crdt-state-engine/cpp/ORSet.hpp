// ORSet.hpp
#pragma once
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <cstdint>

struct Dot {
    std::string actor;
    uint64_t counter{0};

    bool operator==(const Dot& other) const noexcept {
        return counter == other.counter && actor == other.actor;
    }
};

struct DotHash {
    size_t operator()(const Dot& d) const noexcept {
        return std::hash<std::string>{}(d.actor) ^ (std::hash<uint64_t>{}(d.counter) << 1);
    }
};

template <typename T>
class ORSet {
public:
    explicit ORSet(std::string actor_id) : actor_(std::move(actor_id)) {}

    // Додавання елемента: створюємо новий причинний Dot
    void add(const T& element) {
        Dot dot{ .actor = actor_, .counter = ++local_counter_ };
        elements_[element].insert(dot);
    }

    // Видалення елемента: додаємо всі поточні Dots у надгробки
    void remove(const T& element) {
        auto it = elements_.find(element);
        if (it != elements_.end()) {
            for (const auto& dot : it->second) {
                tombstones_.insert(dot);
            }
            elements_.erase(it);
        }
    }

    // Читання активних елементів
    [[nodiscard]] std::vector<T> read() const {
        std::vector<T> active;
        for (const auto& [elem, dots] : elements_) {
            bool has_alive_dot = false;
            for (const auto& dot : dots) {
                if (!tombstones_.contains(dot)) {
                    has_alive_dot = true;
                    break;
                }
            }
            if (has_alive_dot) {
                active.push_back(elem);
            }
        }
        return active;
    }

    // Злиття за законами напівґратки
    void merge(const ORSet<T>& other) {
        // 1. Об'єднуємо надгробки
        tombstones_.insert(other.tombstones_.begin(), other.tombstones_.end());

        // 2. Об'єднуємо елементи та їхні Dots
        for (const auto& [elem, remote_dots] : other.elements_) {
            elements_[elem].insert(remote_dots.begin(), remote_dots.end());
        }

        // 3. Локальний лічильник оновлюємо до максимуму
        local_counter_ = std::max(local_counter_, other.local_counter_);

        // 4. Очищення елементів, усі точки яких потрапили в надгробки
        for (auto it = elements_.begin(); it != elements_.end(); ) {
            std::erase_if(it->second, [this](const Dot& d) {
                return tombstones_.contains(d);
            });
            if (it->second.empty()) {
                it = elements_.erase(it);
            } else {
                ++it;
            }
        }
    }

private:
    std::string actor_;
    uint64_t local_counter_{0};
    std::unordered_map<T, std::unordered_set<Dot, DotHash>> elements_;
    std::unordered_set<Dot, DotHash> tombstones_;
};
