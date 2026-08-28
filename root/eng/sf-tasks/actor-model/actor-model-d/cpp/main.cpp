#include <iostream>
#include <functional>
#include <variant>
#include <cstdint>

struct Deposit { int amount; };
struct Withdraw { int amount; };
struct Freeze {};
struct Unfreeze {};

using OrderCommand = std::variant<Deposit, Withdraw, Freeze, Unfreeze>;

class AccountActor {
public:
    using Behavior = std::function<void(const OrderCommand& cmd)>;

    explicit AccountActor(uint32_t id, int initial_balance = 0)
        : id_(id), balance_(initial_balance) {
        behavior_ = [this](const OrderCommand& cmd) { active_behavior(cmd); };
    }

    void receive(const OrderCommand& cmd) {
        if (behavior_) {
            behavior_(cmd);
        }
    }

private:
    void active_behavior(const OrderCommand& cmd) {
        std::visit([this](auto&& arg) {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, Deposit>) {
                balance_ += arg.amount;
                std::cout << "[C++ Актор " << id_ << "] Депозит +" << arg.amount << ". Баланс: " << balance_ << "\n";
            } else if constexpr (std::is_same_v<T, Withdraw>) {
                if (balance_ >= arg.amount) {
                    balance_ -= arg.amount;
                    std::cout << "[C++ Актор " << id_ << "] Зняття -" << arg.amount << ". Залишок: " << balance_ << "\n";
                } else {
                    std::cout << "[C++ Актор " << id_ << "] Відхилено: недостатньо коштів (" << balance_ << " < " << arg.amount << ")\n";
                }
            } else if constexpr (std::is_same_v<T, Freeze>) {
                std::cout << "[C++ Актор " << id_ << "] Рахунок заморожено! Зміна поведінки.\n";
                become([this](const OrderCommand& c) { frozen_behavior(c); });
            } else if constexpr (std::is_same_v<T, Unfreeze>) {
                std::cout << "[C++ Актор " << id_ << "] Рахунок уже активний.\n";
            }
        }, cmd);
    }

    void frozen_behavior(const OrderCommand& cmd) {
        std::visit([this](auto&& arg) {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, Unfreeze>) {
                std::cout << "[C++ Актор " << id_ << "] Рахунок розморожено. Повернення до активного стану.\n";
                become([this](const OrderCommand& c) { active_behavior(c); });
            } else {
                std::cout << "[C++ Актор " << id_ << "] ВІДХИЛЕНО: рахунок заблоковано!\n";
            }
        }, cmd);
    }

    void become(Behavior new_behavior) {
        behavior_ = std::move(new_behavior);
    }

    uint32_t id_;
    int balance_;
    Behavior behavior_;
};

int main() {
    AccountActor account(202, 1000);

    account.receive(Withdraw{300});
    account.receive(Freeze{});
    account.receive(Withdraw{100}); // Відхилено через заморозку
    account.receive(Unfreeze{});
    account.receive(Withdraw{100}); // Успішно

    return 0;
}
