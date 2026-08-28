// cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <expected>
#include <span>
#include <memory>

enum class LVal : int8_t { False = -1, Unassigned = 0, True = 1 };

class Literal {
    uint32_t code_;
public:
    constexpr Literal() : code_(0) {}
    constexpr Literal(uint32_t var, bool is_neg) : code_((var << 1) | (is_neg ? 1 : 0)) {}
    
    [[nodiscard]] constexpr uint32_t var() const noexcept { return code_ >> 1; }
    [[nodiscard]] constexpr bool is_neg() const noexcept { return (code_ & 1) != 0; }
    [[nodiscard]] constexpr Literal neg() const noexcept { Literal l; l.code_ = code_ ^ 1; return l; }
    [[nodiscard]] constexpr uint32_t code() const noexcept { return code_; }
    
    constexpr bool operator==(const Literal& o) const noexcept { return code_ == o.code_; }
};

struct Watcher {
    uint32_t clause_id;
    Literal  blocker;
};

class Clause {
    std::vector<Literal> lits_;
public:
    explicit Clause(std::span<const Literal> lits) : lits_(lits.begin(), lits.end()) {}
    
    [[nodiscard]] size_t size() const noexcept { return lits_.size(); }
    [[nodiscard]] Literal& operator[](size_t idx) noexcept { return lits_[idx]; }
    [[nodiscard]] const Literal& operator[](size_t idx) const noexcept { return lits_[idx]; }
    [[nodiscard]] std::span<Literal> literals() noexcept { return lits_; }
};

class WatchedLiteralsEngine {
    uint32_t num_vars_;
    std::vector<LVal> values_;
    std::vector<uint32_t> levels_;
    
    std::vector<Clause> clauses_;
    std::vector<std::vector<Watcher>> watches_;
    
    std::vector<Literal> trail_;
    size_t trail_head_{0};
    uint32_t current_level_{0};

public:
    explicit WatchedLiteralsEngine(uint32_t num_vars)
        : num_vars_(num_vars),
          values_(num_vars + 1, LVal::Unassigned),
          levels_(num_vars + 1, 0),
          watches_(2 * (num_vars + 1)) {}

    [[nodiscard]] LVal value(Literal lit) const noexcept {
        LVal v = values_[lit.var()];
        if (v == LVal::Unassigned) return LVal::Unassigned;
        return lit.is_neg() ? static_cast<LVal>(-static_cast<int8_t>(v)) : v;
    }

    void add_clause(std::span<const Literal> lits) {
        uint32_t cid = static_cast<uint32_t>(clauses_.size());
        clauses_.emplace_back(lits);
        
        if (lits.size() >= 2) {
            watches_[lits[0].code()].push_back({cid, lits[1]});
            watches_[lits[1].code()].push_back({cid, lits[0]});
        }
    }

    void enqueue(Literal lit) {
        values_[lit.var()] = lit.is_neg() ? LVal::False : LVal::True;
        levels_[lit.var()] = current_level_;
        trail_.push_back(lit);
    }

    void set_decision_level(uint32_t level) noexcept {
        current_level_ = level;
    }

    [[nodiscard]] std::expected<void, uint32_t> propagate() {
        while (trail_head_ < trail_.size()) {
            Literal p = trail_[trail_head_++];
            Literal false_lit = p.neg();
            auto& wl = watches_[false_lit.code()];
            
            size_t i = 0, j = 0;
            while (i < wl.size()) {
                Watcher w = wl[i];
                Clause& c = clauses_[w.clause_id];
                
                if (value(w.blocker) == LVal::True) {
                    wl[j++] = w;
                    i++;
                    continue;
                }
                
                if (c[1] == false_lit) {
                    std::swap(c[0], c[1]);
                }
                
                Literal second = c[1];
                if (value(second) == LVal::True) {
                    wl[j++] = Watcher{w.clause_id, second};
                    i++;
                    continue;
                }
                
                bool found_new = false;
                for (size_t k = 2; k < c.size(); ++k) {
                    if (value(c[k]) != LVal::False) {
                        c[0] = c[k];
                        c[k] = false_lit;
                        watches_[c[0].code()].push_back({w.clause_id, second});
                        found_new = true;
                        break;
                    }
                }
                
                if (found_new) {
                    i++;
                    continue;
                }
                
                wl[j++] = w;
                i++;
                
                if (value(second) == LVal::False) {
                    while (i < wl.size()) wl[j++] = wl[i++];
                    wl.resize(j);
                    return std::unexpected(w.clause_id);
                } else {
                    enqueue(second);
                }
            }
            wl.resize(j);
        }
        return {};
    }

    void backtrack(uint32_t target_level) {
        while (!trail_.empty()) {
            Literal lit = trail_.back();
            if (levels_[lit.var()] <= target_level) break;
            
            values_[lit.var()] = LVal::Unassigned;
            levels_[lit.var()] = 0;
            trail_.pop_back();
        }
        trail_head_ = trail_.size();
        current_level_ = target_level;
    }
};

int main() {
    WatchedLiteralsEngine engine(4);
    
    // (x1 v x2 v x3)
    Literal c1_lits[] = { Literal(1, false), Literal(2, false), Literal(3, false) };
    engine.add_clause(c1_lits);
    
    // (¬x1 v x4)
    Literal c2_lits[] = { Literal(1, true), Literal(4, false) };
    engine.add_clause(c2_lits);
    
    engine.set_decision_level(1);
    engine.enqueue(Literal(1, false)); // x1 := True
    
    auto res = engine.propagate();
    if (res.has_value()) {
        std::cout << "BCP Propagated successfully!\n";
    } else {
        std::cout << "Conflict in clause: " << res.error() << "\n";
    }
    
    engine.backtrack(0);
    std::cout << "Backtracked to level 0 without clause database writes.\n";
    return 0;
}
