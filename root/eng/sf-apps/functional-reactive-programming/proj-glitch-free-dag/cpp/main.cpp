// C++20: Типобезпечний двоетапний реактивний граф без глітчів із RAII та batch

#include <iostream>
#include <memory>
#include <vector>
#include <functional>
#include <unordered_set>
#include <stdexcept>
#include <cassert>

class IDependency;

class ISubscriber {
public:
    virtual ~ISubscriber() = default;
    virtual void mark_dirty() = 0;
    virtual void run() = 0;
    virtual void add_dependency(std::shared_ptr<IDependency> dep) = 0;
};

class IDependency {
public:
    virtual ~IDependency() = default;
    virtual void remove_subscriber(ISubscriber* sub) = 0;
};

// ── Глобальний контекст активного підписника ──────────────────────────────────
inline ISubscriber* g_active_subscriber = nullptr;
inline int g_batch_depth = 0;
inline std::unordered_set<ISubscriber*> g_pending_effects;

struct ContextGuard {
    ISubscriber* prev;
    explicit ContextGuard(ISubscriber* next) : prev(g_active_subscriber) {
        g_active_subscriber = next;
    }
    ~ContextGuard() {
        g_active_subscriber = prev;
    }
};

template <typename Func>
auto batch(Func&& fn) {
    g_batch_depth++;
    try {
        if constexpr (std::is_void_v<std::invoke_result_t<Func>>) {
            fn();
            g_batch_depth--;
            if (g_batch_depth == 0) {
                auto effects = g_pending_effects;
                g_pending_effects.clear();
                for (auto* eff : effects) {
                    eff->run();
                }
            }
        } else {
            auto res = fn();
            g_batch_depth--;
            if (g_batch_depth == 0) {
                auto effects = g_pending_effects;
                g_pending_effects.clear();
                for (auto* eff : effects) {
                    eff->run();
                }
            }
            return res;
        }
    } catch (...) {
        g_batch_depth--;
        throw;
    }
}

// ── 1. Signal (Джерело даних) ────────────────────────────────────────────────
template <typename T>
class Signal : public IDependency, public std::enable_shared_from_this<Signal<T>> {
private:
    T value_;
    std::unordered_set<ISubscriber*> subscribers_;

public:
    explicit Signal(T initial) : value_(std::move(initial)) {}

    const T& get() {
        if (g_active_subscriber) {
            subscribers_.insert(g_active_subscriber);
            g_active_subscriber->add_dependency(this->shared_from_this());
        }
        return value_;
    }

    void set(T new_value) {
        if (value_ == new_value) return;
        value_ = std::move(new_value);

        auto subs = subscribers_;
        // Фаза 1: Push Dirty
        for (auto* sub : subs) {
            sub->mark_dirty();
        }
        // Фаза 2: Pull / Run
        for (auto* sub : subs) {
            if (g_batch_depth > 0) {
                g_pending_effects.insert(sub);
            } else {
                sub->run();
            }
        }
    }

    void remove_subscriber(ISubscriber* sub) override {
        subscribers_.erase(sub);
    }
};

// ── 2. Computed (Мемоізоване похідне обчислення) ─────────────────────────────
template <typename T>
class Computed : public ISubscriber, public IDependency, public std::enable_shared_from_this<Computed<T>> {
private:
    std::function<T()> fn_;
    T cached_value_{};
    bool is_dirty_{true};
    bool is_evaluating_{false};
    std::unordered_set<ISubscriber*> subscribers_;
    std::unordered_set<std::shared_ptr<IDependency>> dependencies_;

public:
    explicit Computed(std::function<T()> fn) : fn_(std::move(fn)) {}

    void add_dependency(std::shared_ptr<IDependency> dep) override {
        dependencies_.insert(std::move(dep));
    }

    void remove_subscriber(ISubscriber* sub) override {
        subscribers_.erase(sub);
    }

    void mark_dirty() override {
        if (!is_dirty_) {
            is_dirty_ = true;
            for (auto* sub : subscribers_) {
                sub->mark_dirty();
            }
        }
    }

    void run() override {
        auto subs = subscribers_;
        for (auto* sub : subs) {
            if (g_batch_depth > 0) {
                g_pending_effects.insert(sub);
            } else {
                sub->run();
            }
        }
    }

    const T& get() {
        if (is_evaluating_) {
            throw std::runtime_error("Виявлено циклічну залежність у реактивному графі!");
        }

        if (g_active_subscriber) {
            subscribers_.insert(g_active_subscriber);
            g_active_subscriber->add_dependency(this->shared_from_this());
        }

        if (is_dirty_) {
            // Очищення старих залежностей перед перерахунком
            for (auto& dep : dependencies_) {
                dep->remove_subscriber(this);
            }
            dependencies_.clear();

            is_evaluating_ = true;
            ContextGuard guard(this);
            try {
                cached_value_ = fn_();
                is_dirty_ = false;
                is_evaluating_ = false;
            } catch (...) {
                is_evaluating_ = false;
                throw;
            }
        }
        return cached_value_;
    }
};

// ── 3. Effect (Кінцевий споживач) ────────────────────────────────────────────
class Effect : public ISubscriber {
private:
    std::function<void()> fn_;
    bool is_dirty_{true};
    bool is_running_{false};
    std::unordered_set<std::shared_ptr<IDependency>> dependencies_;

public:
    explicit Effect(std::function<void()> fn) : fn_(std::move(fn)) {
        run();
    }

    ~Effect() override {
        dispose();
    }

    void add_dependency(std::shared_ptr<IDependency> dep) override {
        dependencies_.insert(std::move(dep));
    }

    void mark_dirty() override {
        is_dirty_ = true;
    }

    void run() override {
        if (!is_dirty_ || is_running_) return;

        for (auto& dep : dependencies_) {
            dep->remove_subscriber(this);
        }
        dependencies_.clear();

        is_dirty_ = false;
        is_running_ = true;
        ContextGuard guard(this);
        try {
            fn_();
            is_running_ = false;
        } catch (...) {
            is_running_ = false;
            throw;
        }
    }

    void dispose() {
        for (auto& dep : dependencies_) {
            dep->remove_subscriber(this);
        }
        dependencies_.clear();
    }
};

// ── Демонстрація роботи ──────────────────────────────────────────────────────
int main() {
    auto a = std::make_shared<Signal<int>>(1);

    auto b = std::make_shared<Computed<int>>([a]() {
        int v = a->get();
        std::cout << "  [C++ B] a + 1 = " << (v + 1) << "\n";
        return v + 1;
    });

    auto c = std::make_shared<Computed<int>>([a]() {
        int v = a->get();
        std::cout << "  [C++ C] a * 2 = " << (v * 2) << "\n";
        return v * 2;
    });

    auto d = std::make_shared<Computed<int>>([b, c]() {
        int bv = b->get();
        int cv = c->get();
        std::cout << "  [C++ D] B(" << bv << ") + C(" << cv << ") = " << (bv + cv) << "\n";
        return bv + cv;
    });

    std::cout << "=== Створення Effect ===\n";
    auto effect = std::make_unique<Effect>([d]() {
        std::cout << "-> ГОЛОВНИЙ РЕЗУЛЬТАТ D = " << d->get() << "\n";
    });

    std::cout << "\n=== Зміна a: 1 -> 2 (без глітчів) ===\n";
    a->set(2);

    std::cout << "\n=== Пакетне оновлення (batch) ===\n";
    batch([&]() {
        a->set(3);
        a->set(5);
    });

    return 0;
}
