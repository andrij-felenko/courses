#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <variant>
#include <optional>
#include <span>
#include <memory>
#include <stdexcept>
#include <format>

// ── Модель даних: Userset, Subject, Tuple ───────────────────────────────────

struct Userset {
    std::string object;
    std::string relation;

    [[nodiscard]] std::string key() const {
        return object + "#" + relation;
    }

    bool operator==(const Userset& other) const = default;
};

struct UsersetHash {
    std::size_t operator()(const Userset& u) const noexcept {
        return std::hash<std::string>{}(u.key());
    }
};

struct Subject {
    std::variant<std::string, Userset> value;

    [[nodiscard]] bool is_user() const noexcept {
        return std::holds_alternative<std::string>(value);
    }
    [[nodiscard]] const std::string& user() const {
        return std::get<std::string>(value);
    }
    [[nodiscard]] const Userset& userset() const {
        return std::get<Userset>(value);
    }
};

struct Tuple {
    std::string object;
    std::string relation;
    Subject subject;
};

// ── Правила авторизації ─────────────────────────────────────────────────────

enum class RuleKind { This, Computed, Walk };

struct Rule {
    RuleKind kind;
    std::string rel{};
    std::string via{};
    std::string then{};

    static Rule make_this() { return {RuleKind::This}; }
    static Rule make_computed(std::string r) { return {RuleKind::Computed, std::move(r)}; }
    static Rule make_walk(std::string via, std::string then) {
        return {RuleKind::Walk, {}, std::move(via), std::move(then)};
    }
};

using Config = std::unordered_map<std::string, std::unordered_map<std::string, std::vector<Rule>>>;

inline Config default_config() {
    Config cfg;
    cfg["group"]["member"] = {Rule::make_this()};
    cfg["folder"]["parent"] = {Rule::make_this()};
    cfg["folder"]["editor"] = {Rule::make_this(), Rule::make_walk("parent", "editor")};
    cfg["folder"]["viewer"] = {Rule::make_this(), Rule::make_computed("editor"),
                               Rule::make_walk("parent", "viewer")};
    cfg["doc"]["parent"] = {Rule::make_this()};
    cfg["doc"]["editor"] = {Rule::make_this(), Rule::make_walk("parent", "editor")};
    cfg["doc"]["viewer"] = {Rule::make_this(), Rule::make_computed("editor"),
                            Rule::make_walk("parent", "viewer")};
    return cfg;
}

// ── Сховище кортежів ────────────────────────────────────────────────────────

class Store {
public:
    virtual ~Store() = default;
    virtual std::unordered_map<std::string, std::vector<Subject>> read_many(
        std::span<const Userset> keys) = 0;
};

class MemoryStore final : public Store {
private:
    std::unordered_map<std::string, std::vector<Subject>> idx_;
public:
    int trips{0};

    explicit MemoryStore(std::span<const Tuple> tuples) {
        for (const auto& t : tuples) {
            idx_[t.object + "#" + t.relation].push_back(t.subject);
        }
    }

    std::unordered_map<std::string, std::vector<Subject>> read_many(
        std::span<const Userset> keys) override {
        ++trips;
        std::unordered_map<std::string, std::vector<Subject>> result;
        for (const auto& k : keys) {
            const auto key_str = k.key();
            if (auto it = idx_.find(key_str); it != idx_.end()) {
                result[key_str] = it->second;
            } else {
                result[key_str] = {};
            }
        }
        return result;
    }
};

// ── Движок перевірки ReBAC ──────────────────────────────────────────────────

class DepthExceededException : public std::runtime_error {
public:
    explicit DepthExceededException(const std::string& msg) : std::runtime_error(msg) {}
};

struct CheckResult {
    bool allowed{false};
    int depth{0};
    int trips{0};
};

class Checker {
private:
    Config config_;
    std::shared_ptr<Store> store_;
    int max_depth_{16};
    bool memo_{true};

    [[nodiscard]] std::span<const Rule> get_rules(const Userset& u) const {
        const auto colon_pos = u.object.find(':');
        const std::string ns = (colon_pos != std::string::npos) ? u.object.substr(0, colon_pos) : u.object;
        if (auto it_ns = config_.find(ns); it_ns != config_.end()) {
            if (auto it_rel = it_ns->second.find(u.relation); it_rel != it_ns->second.end()) {
                return it_rel->second;
            }
        }
        return {};
    }

    [[nodiscard]] std::vector<Userset> close_computed(std::span<const Userset> frontier) const {
        std::unordered_set<std::string> local_seen;
        std::vector<Userset> out;
        std::vector<Userset> stack(frontier.begin(), frontier.end());

        while (!stack.empty()) {
            Userset curr = stack.back();
            stack.pop_back();

            if (local_seen.contains(curr.key())) continue;
            local_seen.insert(curr.key());
            out.push_back(curr);

            for (const auto& r : get_rules(curr)) {
                if (r.kind == RuleKind::Computed) {
                    stack.push_back(Userset{curr.object, r.rel});
                }
            }
        }
        return out;
    }

public:
    Checker(Config cfg, std::shared_ptr<Store> store, int max_depth = 16, bool memo = true)
        : config_(std::move(cfg)), store_(std::move(store)), max_depth_(max_depth), memo_(memo) {}

    [[nodiscard]] CheckResult check(std::string_view user, const Userset& start) {
        std::unordered_set<std::string> seen{start.key()};
        std::vector<Userset> frontier{start};
        int trips = 0;

        for (int depth = 0; depth < max_depth_; ++depth) {
            if (frontier.empty()) {
                return CheckResult{.allowed = false, .depth = depth, .trips = trips};
            }

            const auto nodes = close_computed(frontier);

            // (1) Зібрати всі ключі для читання
            std::vector<Userset> want;
            std::unordered_set<std::string> wanted;
            auto add_want = [&](const Userset& u) {
                if (!wanted.contains(u.key())) {
                    wanted.insert(u.key());
                    want.push_back(u);
                }
            };

            for (const auto& n : nodes) {
                for (const auto& r : get_rules(n)) {
                    if (r.kind == RuleKind::This) add_want(n);
                    if (r.kind == RuleKind::Walk) add_want(Userset{n.object, r.via});
                }
            }

            // (2) Один батч-запит у сховище
            auto rows = store_->read_many(want);
            ++trips;

            // (3) Обхід і розкриття наступного рівня
            std::vector<Userset> next_frontier;
            auto enqueue = [&](const Userset& u) {
                if (memo_) {
                    if (seen.contains(u.key())) return;
                    seen.insert(u.key());
                }
                next_frontier.push_back(u);
            };

            for (const auto& n : nodes) {
                for (const auto& r : get_rules(n)) {
                    if (r.kind == RuleKind::This) {
                        for (const auto& s : rows[n.key()]) {
                            if (s.is_user()) {
                                if (s.user() == user) {
                                    return CheckResult{.allowed = true, .depth = depth, .trips = trips};
                                }
                            } else {
                                enqueue(s.userset());
                            }
                        }
                    } else if (r.kind == RuleKind::Walk) {
                        const Userset via{n.object, r.via};
                        for (const auto& s : rows[via.key()]) {
                            if (!s.is_user()) {
                                enqueue(Userset{s.userset().object, r.then});
                            }
                        }
                    }
                }
            }

            frontier = std::move(next_frontier);
        }

        throw DepthExceededException(
            std::format("{}: обхід не вклався в {} рівнів", start.key(), max_depth_));
    }
};
