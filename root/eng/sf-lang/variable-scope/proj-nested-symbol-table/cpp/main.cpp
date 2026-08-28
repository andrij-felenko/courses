#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <optional>

class Environment : public std::enable_shared_from_this<Environment> {
public:
    using Ptr = std::shared_ptr<Environment>;

    explicit Environment(Ptr parent = nullptr) : parent_(std::move(parent)) {}

    // Оголошення в поточному кадрі (затінення зовнішніх імен)
    void define(std::string_view name, int value) {
        bindings_[std::string(name)] = value;
    }

    // Лексичний пошук ідентифікатора вгору по дереву
    [[nodiscard]] std::optional<int> lookup(std::string_view name) const noexcept {
        const auto it = bindings_.find(std::string(name));
        if (it != bindings_.end()) {
            return it->second;
        }
        if (parent_) {
            return parent_->lookup(name); // Рекурсивний підйом до предка
        }
        return std::nullopt;
    }

    // Зміна значення у найближчому видимому кадрі
    bool assign(std::string_view name, int value) noexcept {
        const auto it = bindings_.find(std::string(name));
        if (it != bindings_.end()) {
            it->second = value;
            return true;
        }
        if (parent_) {
            return parent_->assign(name, value);
        }
        return false;
    }

    [[nodiscard]] Ptr parent() const noexcept { return parent_; }

private:
    std::unordered_map<std::string, int> bindings_;
    Ptr parent_;
};

// RAII Scope Guard для автоматичного керування межами блоків
class ScopeGuard {
public:
    explicit ScopeGuard(Environment::Ptr& current)
        : current_ref_(current), previous_(current) {
        current_ref_ = std::make_shared<Environment>(previous_);
    }

    ~ScopeGuard() noexcept {
        current_ref_ = previous_; // Відновлюємо попередній кадр при виході з блоку
    }

    ScopeGuard(const ScopeGuard&) = delete;
    ScopeGuard& operator=(const ScopeGuard&) = delete;

private:
    Environment::Ptr& current_ref_;
    Environment::Ptr previous_;
};

int main() {
    auto current_env = std::make_shared<Environment>();
    current_env->define("x", 10);
    current_env->define("g_flag", 1);

    {
        // Вхід у блок функції через RAII
        ScopeGuard func_scope(current_env);
        current_env->define("x", 20); // Затінення

        {
            // Вхід у вкладений блок if/for
            ScopeGuard block_scope(current_env);
            current_env->define("y", 30);

            std::cout << "Block sees x = " << *current_env->lookup("x") << " (expected 20)\n";
            std::cout << "Block sees g_flag = " << *current_env->lookup("g_flag") << " (expected 1)\n";

            current_env->assign("g_flag", 99);
        } // block_scope автоматично знищується тут

        std::cout << "Func sees x = " << *current_env->lookup("x") << " (expected 20)\n";
        std::cout << "Func sees y = " 
                  << (current_env->lookup("y").has_value() ? "found" : "nullopt") << "\n";
    } // func_scope автоматично знищується тут

    std::cout << "Global sees x = " << *current_env->lookup("x") << " (expected 10)\n";
    std::cout << "Global g_flag = " << *current_env->lookup("g_flag") << " (expected 99)\n";

    return 0;
}
