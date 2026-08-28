// C++20: Оптимістичне сховище стану клієнта з механізмом відкату (Rollback & Rebase)

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <future>
#include <algorithm>
#include <expected>

struct Task {
    std::string id;
    std::string title;
    bool completed{false};
};

struct AppState {
    std::vector<Task> tasks;
};

template <typename State>
struct Mutation {
    std::string id;
    std::function<State(const State&)> apply;
    std::function<State(const State&)> rollback;
    std::function<std::expected<void, std::string>()> execute;
};

template <typename State>
class OptimisticStore {
public:
    explicit OptimisticStore(State initial)
        : committedState_(std::move(initial)), optimisticState_(committedState_) {}

    const State& getState() const noexcept {
        return optimisticState_;
    }

    void subscribe(std::function<void(const State&)> listener) {
        listeners_.push_back(std::move(listener));
    }

    // Синхронно мутує оптимістичний стан (<1 мс) та повертає результат асинхронного комміту
    std::future<bool> dispatch(Mutation<State> mutation) {
        // 1. Миттєве локальне оновлення
        optimisticState_ = mutation.apply(optimisticState_);
        pendingMutations_.push_back(mutation);
        notify();

        // 2. Асинхронний комміт на сервер
        return std::async(std::launch::async, [this, id = mutation.id]() {
            // Знаходимо мутацію за ідентифікатором
            auto it = std::find_if(pendingMutations_.begin(), pendingMutations_.end(),
                                   [&](const auto& m) { return m.id == id; });
            if (it == pendingMutations_.end()) {
                return false;
            }
            auto currentMutation = *it;

            auto result = currentMutation.execute();
            if (result.has_value()) {
                // Успіх: фіксуємо в підтвердженому стані
                committedState_ = currentMutation.apply(committedState_);
                removeMutation(id);
                return true;
            } else {
                // Помилка: вилучаємо з черги та виконуємо rebase
                removeMutation(id);
                rebase();
                notify();
                return false;
            }
        });
    }

private:
    void notify() {
        for (const auto& listener : listeners_) {
            listener(optimisticState_);
        }
    }

    void removeMutation(const std::string& id) {
        pendingMutations_.erase(
            std::remove_if(pendingMutations_.begin(), pendingMutations_.end(),
                           [&](const auto& m) { return m.id == id; }),
            pendingMutations_.end()
        );
    }

    void rebase() {
        State state = committedState_;
        for (const auto& pending : pendingMutations_) {
            state = pending.apply(state);
        }
        optimisticState_ = std::move(state);
    }

    State committedState_;
    State optimisticState_;
    std::vector<Mutation<State>> pendingMutations_;
    std::vector<std::function<void(const State&)>> listeners_;
};
