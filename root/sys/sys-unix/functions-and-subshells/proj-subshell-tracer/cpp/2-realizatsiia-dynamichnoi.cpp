#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <optional>
#include <memory>

class DynamicScopeStack {
    struct CallFrame {
        std::string function_name;
        std::unordered_map<std::string, std::string> locals;
    };
    std::vector<CallFrame> frames_;

public:
    DynamicScopeStack() {
        frames_.push_back(CallFrame{"global", {}});
    }

    void push_frame(const std::string& func_name) {
        frames_.push_back(CallFrame{func_name, {}});
        std::cout << "──► Entering function: " << func_name 
                  << " (Depth: " << frames_.size() - 1 << ")\n";
    }

    void pop_frame() {
        if (frames_.size() > 1) {
            std::cout << "◄── Exiting function: " << frames_.back().function_name << "\n";
            frames_.pop_back();
        }
    }

    void set_local(const std::string& name, const std::string& value) {
        frames_.back().locals[name] = value;
    }

    // Динамічний пошук змінної від вершини стека вниз
    std::optional<std::string> resolve(const std::string& name) const {
        for (auto it = frames_.rbegin(); it != frames_.rend(); ++it) {
            auto found = it->locals.find(name);
            if (found != it->locals.end()) {
                return found->second;
            }
        }
        return std::nullopt;
    }
};

void run_inner(DynamicScopeStack& scope) {
    scope.push_frame("run_inner");
    auto token = scope.resolve("auth_token");
    std::cout << "  [run_inner] Resolved 'auth_token': " 
              << token.value_or("<undefined>") << "\n";
    scope.pop_frame();
}

void run_outer(DynamicScopeStack& scope) {
    scope.push_frame("run_outer");
    scope.set_local("auth_token", "MODERN_CPP_SECRET_999");
    run_inner(scope);
    scope.pop_frame();
}

int main() {
    DynamicScopeStack scope;
    scope.set_local("auth_token", "GLOBAL_CPP_DEFAULT");

    std::cout << "[Main] Initial token: " << scope.resolve("auth_token").value() << "\n";
    run_outer(scope);
    std::cout << "[Main] Final token: " << scope.resolve("auth_token").value() << "\n";

    return 0;
}
