// ── 1. Стан рушія, вузол, стеження ────────────────────────────────────
#include <algorithm>
#include <cstdio>
#include <functional>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace sg {

class Node;
class Derived;

inline long     epoch = 0;        // номер поточного поширення
inline Derived* frame = nullptr;  // вузол, який ЗАРАЗ обчислюється

void mark(Node& from);
void settleAll();
void settleNode(Derived& n);
void track(Node& n);

class Node {
public:
    virtual ~Node() = default;
    virtual Derived* asDerived() { return nullptr; }   // дешевше за dynamic_cast

    int  height    = 0;   // 0 у джерела; у похідного — 1 + max(висот входів)
    long changedAt = 0;   // епоха, у якій значення СПРАВДІ змінилося
    std::vector<Derived*> subs;                        // хто читає мене
};

inline void unlink(Node& from, Derived& who) {
    auto& v = from.subs;
    v.erase(std::remove(v.begin(), v.end(), &who), v.end());
}

// ── Джерело: єдине місце, куди пишуть ззовні ──────────────────────────
template <class T>
class Signal final : public Node {
public:
    using Eq = std::function<bool(const T&, const T&)>;

    explicit Signal(T v, Eq eq = std::equal_to<T>{})
        : value_(std::move(v)), eq_(std::move(eq)) {}

    const T& get() { track(*this); return value_; }

    void set(T next) {
        if (frame) throw std::logic_error("запис у джерело зсередини обчислення");
        if (eq_(next, value_)) return;      // відсічка: не змінилося — не сталося нічого
        value_ = std::move(next);
        changedAt = ++epoch;
        mark(*this);                        // ФАЗА 1
        settleAll();                        // ФАЗА 2
    }

private:
    T  value_;
    Eq eq_;
};
