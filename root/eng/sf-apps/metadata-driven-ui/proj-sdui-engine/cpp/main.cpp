// C++20: Нативний рушій інтерпретації метаданих Metadata-Driven UI

#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <variant>
#include <regex>
#include <functional>

// 1. Представлення універсального JSON-значення
struct Value;
using Object = std::unordered_map<std::string, Value>;
using Array = std::vector<Value>;

struct Value {
    std::variant<std::nullptr_t, bool, double, std::string, Object, Array> data;

    Value() : data(nullptr) {}
    Value(bool b) : data(b) {}
    Value(double d) : data(d) {}
    Value(std::string s) : data(std::move(s)) {}
    Value(const char* s) : data(std::string(s)) {}
    Value(Object o) : data(std::move(o)) {}
    Value(Array a) : data(std::move(a)) {}

    bool as_bool() const {
        if (auto p = std::get_if<bool>(&data)) return *p;
        if (auto p = std::get_if<double>(&data)) return *p != 0.0;
        if (auto p = std::get_if<std::string>(&data)) return !p->empty();
        return false;
    }

    std::string as_string() const {
        if (auto p = std::get_if<std::string>(&data)) return *p;
        if (auto p = std::get_if<double>(&data)) return std::to_string(*p);
        if (auto p = std::get_if<bool>(&data)) return *p ? "true" : "false";
        return "";
    }
};

// 2. Реактивне сховище стану
class StateStore {
public:
    explicit StateStore(Object initial) : state_(std::move(initial)) {}

    Value get(std::string_view path) const {
        if (path.empty()) return Value();
        std::string p(path.starts_with('/') ? path.substr(1) : path);
        size_t start = 0;
        const Object* cur = &state_;

        while (start < p.size()) {
            size_t end = p.find('/', start);
            std::string key = (end == std::string::npos) ? p.substr(start) : p.substr(start, end - start);
            auto it = cur->find(key);
            if (it == cur->end()) return Value();

            if (end == std::string::npos) {
                return it->second;
            }
            if (auto obj = std::get_if<Object>(&it->second.data)) {
                cur = obj;
            } else {
                return Value();
            }
            start = end + 1;
        }
        return Value();
    }

    void set(std::string_view path, Value val) {
        std::string p(path.starts_with('/') ? path.substr(1) : path);
        state_[p] = std::move(val);
        for (auto& cb : listeners_) cb(p);
    }

    void subscribe(std::function<void(const std::string&)> cb) {
        listeners_.push_back(std::move(cb));
    }

private:
    Object state_;
    std::vector<std::function<void(const std::string&)>> listeners_;
};

// 3. Безпечний обчислювач логічних виразів AST
struct ExprNode;
using ExprPtr = std::shared_ptr<ExprNode>;

struct ExprNode {
    enum class Type { Literal, Var, Equal, NotEqual, And, Or, Not, Regex } type;
    Value literal_val;
    std::string var_path;
    std::string pattern;
    std::vector<ExprPtr> children;
};

class SafeEvaluator {
public:
    static Value evaluate(const ExprPtr& expr, const StateStore& store) {
        if (!expr) return Value(true);

        switch (expr->type) {
            case ExprNode::Type::Literal:
                return expr->literal_val;
            case ExprNode::Type::Var:
                return store.get(expr->var_path);
            case ExprNode::Type::Equal: {
                if (expr->children.size() < 2) return Value(false);
                auto l = evaluate(expr->children[0], store);
                auto r = evaluate(expr->children[1], store);
                return Value(l.as_string() == r.as_string());
            }
            case ExprNode::Type::NotEqual: {
                if (expr->children.size() < 2) return Value(false);
                auto l = evaluate(expr->children[0], store);
                auto r = evaluate(expr->children[1], store);
                return Value(l.as_string() != r.as_string());
            }
            case ExprNode::Type::And: {
                for (const auto& child : expr->children) {
                    if (!evaluate(child, store).as_bool()) return Value(false);
                }
                return Value(true);
            }
            case ExprNode::Type::Or: {
                for (const auto& child : expr->children) {
                    if (evaluate(child, store).as_bool()) return Value(true);
                }
                return Value(false);
            }
            case ExprNode::Type::Not: {
                if (expr->children.empty()) return Value(false);
                return Value(!evaluate(expr->children[0], store).as_bool());
            }
            case ExprNode::Type::Regex: {
                if (expr->children.empty()) return Value(false);
                std::string target = evaluate(expr->children[0], store).as_string();
                try {
                    std::regex re(expr->pattern);
                    return Value(std::regex_search(target, re));
                } catch (...) {
                    return Value(false);
                }
            }
        }
        return Value(false);
    }
};

// 4. Структура візуального вузла та реєстр рендерерів
struct UINode {
    std::string id;
    std::string type;
    std::unordered_map<std::string, std::string> props;
    std::string bind_path;
    ExprPtr visibility;
    std::vector<std::unique_ptr<UINode>> children;
    std::unique_ptr<UINode> fallback;
};

class SDUIEngine {
public:
    using Renderer = std::function<void(const UINode&, const StateStore&, SDUIEngine&)>;

    explicit SDUIEngine(Object init_state) : store_(std::move(init_state)) {}

    void register_component(const std::string& type, Renderer r) {
        registry_[type] = std::move(r);
    }

    void render_tree(const UINode& node) {
        // 1. Перевірка видимості
        if (node.visibility && !SafeEvaluator::evaluate(node.visibility, store_).as_bool()) {
            return;
        }

        // 2. Диспетчеризація за типом
        auto it = registry_.find(node.type);
        if (it != registry_.end()) {
            it->second(node, store_, *this);
            return;
        }

        // 3. Fallback-деградація
        if (node.fallback) {
            render_tree(*node.fallback);
        }
    }

    StateStore& store() { return store_; }

private:
    StateStore store_;
    std::unordered_map<std::string, Renderer> registry_;
};
