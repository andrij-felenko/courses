#include <set>
#include <string>
#include <utility>

struct TaggedElement {
    std::string value;
    std::string tag;

    auto operator<=>(const TaggedElement&) const = default;
};

class ORSet {
public:
    explicit ORSet(std::string node_id) : node_id_(std::move(node_id)), counter_(0) {}

    void add(const std::string& value) {
        std::string tag = node_id_ + ":" + std::to_string(++counter_);
        add_set_.insert({value, tag});
    }

    void remove(const std::string& value) {
        // Додаємо всі спостережувані на даний момент теги цього значення до множини видалення
        for (const auto& item : add_set_) {
            if (item.value == value) {
                remove_set_.insert(item.tag);
            }
        }
    }

    [[nodiscard]] bool contains(const std::string& value) const {
        for (const auto& item : add_set_) {
            if (item.value == value && !remove_set_.contains(item.tag)) {
                return true;
            }
        }
        return false;
    }

    [[nodiscard]] std::set<std::string> read() const {
        std::set<std::string> result;
        for (const auto& item : add_set_) {
            if (!remove_set_.contains(item.tag)) {
                result.insert(item.value);
            }
        }
        return result;
    }

    // Злиття над напіврешіткою: теоретико-множинне об'єднання множин додавання і видалення
    void merge(const ORSet& other) {
        add_set_.insert(other.add_set_.begin(), other.add_set_.end());
        remove_set_.insert(other.remove_set_.begin(), other.remove_set_.end());
    }

private:
    std::string node_id_;
    uint64_t counter_;
    std::set<TaggedElement> add_set_;
    std::set<std::string> remove_set_;
};
