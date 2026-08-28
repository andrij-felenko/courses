#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <variant>
#include <unordered_map>
#include <sstream>

struct Value;
using ValuePtr = std::shared_ptr<Value>;
struct Env;
using EnvPtr = std::shared_ptr<Env>;

using PrimFn = ValuePtr(*)(const std::vector<ValuePtr>&, EnvPtr);

struct Nil {};
struct Pair { ValuePtr car; ValuePtr cdr; };
struct Closure {
    std::vector<std::string> params;
    std::vector<ValuePtr> body;
    EnvPtr env;
};

struct Value {
    std::variant<Nil, long, std::string, Pair, PrimFn, Closure> data;

    bool is_nil() const { return std::holds_alternative<Nil>(data); }
    bool is_num() const { return std::holds_alternative<long>(data); }
    bool is_sym() const { return std::holds_alternative<std::string>(data); }
    bool is_pair() const { return std::holds_alternative<Pair>(data); }
};

ValuePtr make_nil() { return std::make_shared<Value>(Value{Nil{}}); }
ValuePtr make_num(long n) { return std::make_shared<Value>(Value{n}); }
ValuePtr make_sym(std::string s) { return std::make_shared<Value>(Value{std::move(s)}); }
ValuePtr make_pair(ValuePtr car, ValuePtr cdr) { return std::make_shared<Value>(Value{Pair{std::move(car), std::move(cdr)}}); }

struct Env : std::enable_shared_from_this<Env> {
    std::unordered_map<std::string, ValuePtr> bindings;
    EnvPtr parent;

    Env(EnvPtr p = nullptr) : parent(std::move(p)) {}

    ValuePtr get(const std::string& name) const {
        auto it = bindings.find(name);
        if (it != bindings.end()) return it->second;
        if (parent) return parent->get(name);
        throw std::runtime_error("Невідома змінна: " + name);
    }

    void set(const std::string& name, ValuePtr val) {
        bindings[name] = std::move(val);
    }
};

/* Токенізатор та парсер */
std::vector<std::string> tokenize(const std::string& input) {
    std::vector<std::string> tokens;
    std::string cur;
    for (size_t i = 0; i < input.size(); ++i) {
        char ch = input[i];
        if (std::isspace(ch)) continue;
        if (ch == ';') {
            while (i < input.size() && input[i] != '\n') ++i;
            continue;
        }
        if (ch == '(' || ch == ')' || ch == '\'') {
            tokens.push_back(std::string(1, ch));
        } else {
            cur.clear();
            while (i < input.size() && !std::isspace(input[i]) &&
                   input[i] != '(' && input[i] != ')' && input[i] != ';') {
                cur += input[i++];
            }
            --i;
            tokens.push_back(cur);
        }
    }
    return tokens;
}

ValuePtr parse_tokens(const std::vector<std::string>& tokens, size_t& pos) {
    if (pos >= tokens.size()) return make_nil();
    const auto& tok = tokens[pos++];
    if (tok == "(") {
        std::vector<ValuePtr> list;
        while (pos < tokens.size() && tokens[pos] != ")") {
            list.push_back(parse_tokens(tokens, pos));
        }
        if (pos < tokens.size() && tokens[pos] == ")") ++pos;
        ValuePtr tail = make_nil();
        for (auto it = list.rbegin(); it != list.rend(); ++it) {
            tail = make_pair(*it, tail);
        }
        return tail;
    }
    if (tok == "'") {
        return make_pair(make_sym("quote"), make_pair(parse_tokens(tokens, pos), make_nil()));
    }
    try {
        size_t idx = 0;
        long num = std::stol(tok, &idx);
        if (idx == tok.size()) return make_num(num);
    } catch (...) {}
    return make_sym(tok);
}

/* Обчислення: eval та apply */
ValuePtr eval(ValuePtr exp, EnvPtr env);

std::vector<ValuePtr> pair_to_vec(ValuePtr p) {
    std::vector<ValuePtr> res;
    while (p && p->is_pair()) {
        const auto& pr = std::get<Pair>(p->data);
        res.push_back(pr.car);
        p = pr.cdr;
    }
    return res;
}

ValuePtr apply(ValuePtr fn, const std::vector<ValuePtr>& args, EnvPtr env) {
    if (std::holds_alternative<PrimFn>(fn->data)) {
        return std::get<PrimFn>(fn->data)(args, env);
    }
    if (std::holds_alternative<Closure>(fn->data)) {
        const auto& cl = std::get<Closure>(fn->data);
        auto call_env = std::make_shared<Env>(cl.env);
        for (size_t i = 0; i < cl.params.size() && i < args.size(); ++i) {
            call_env->set(cl.params[i], args[i]);
        }
        ValuePtr res = make_nil();
        for (const auto& b : cl.body) {
            res = eval(b, call_env);
        }
        return res;
    }
    throw std::runtime_error("Спроба виклику не-функціонального значення");
}

ValuePtr eval(ValuePtr exp, EnvPtr env) {
    if (exp->is_nil() || exp->is_num()) return exp;
    if (exp->is_sym()) return env->get(std::get<std::string>(exp->data));

    if (exp->is_pair()) {
        auto elements = pair_to_vec(exp);
        if (elements.empty()) return exp;

        auto op = elements[0];
        if (op->is_sym()) {
            const auto& sym = std::get<std::string>(op->data);
            if (sym == "quote") return elements.at(1);
            if (sym == "if") {
                auto cond = eval(elements.at(1), env);
                bool truthy = !cond->is_nil() && (!cond->is_num() || std::get<long>(cond->data) != 0);
                return truthy ? eval(elements.at(2), env) : (elements.size() > 3 ? eval(elements.at(3), env) : make_nil());
            }
            if (sym == "define") {
                auto val = eval(elements.at(2), env);
                env->set(std::get<std::string>(elements.at(1)->data), val);
                return val;
            }
            if (sym == "lambda") {
                auto param_nodes = pair_to_vec(elements.at(1));
                std::vector<std::string> params;
                for (const auto& p : param_nodes) params.push_back(std::get<std::string>(p->data));
                std::vector<ValuePtr> body(elements.begin() + 2, elements.end());
                return std::make_shared<Value>(Value{Closure{std::move(params), std::move(body), env}});
            }
        }

        auto fn = eval(op, env);
        std::vector<ValuePtr> evaled_args;
        for (size_t i = 1; i < elements.size(); ++i) {
            evaled_args.push_back(eval(elements[i], env));
        }
        return apply(fn, evaled_args, env);
    }
    return exp;
}
