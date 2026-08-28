#include <iostream>
#include <string>
#include <memory>
#include <variant>
#include <unordered_map>
#include <stdexcept>

// 1. AST для типів (Base та Func)
struct TypeBase { std::string name; };
struct TypeFunc;
using Type = std::variant<TypeBase, std::shared_ptr<TypeFunc>>;
struct TypeFunc {
    Type arg_type;
    Type ret_type;
};

// Функція для порівняння типів
bool types_equal(const Type& t1, const Type& t2) {
    if (t1.index() != t2.index()) return false;
    if (std::holds_alternative<TypeBase>(t1)) {
        return std::get<TypeBase>(t1).name == std::get<TypeBase>(t2).name;
    } else {
        auto f1 = std::get<std::shared_ptr<TypeFunc>>(t1);
        auto f2 = std::get<std::shared_ptr<TypeFunc>>(t2);
        return types_equal(f1->arg_type, f2->arg_type) && 
               types_equal(f1->ret_type, f2->ret_type);
    }
}

// 2. AST для термів
struct Var { std::string name; };
struct Abs;
struct App;
using Term = std::variant<Var, std::shared_ptr<Abs>, std::shared_ptr<App>>;
struct Abs {
    std::string param_name;
    Type param_type;
    Term body;
};
struct App {
    Term func;
    Term arg;
};

// 3. Контекст типізації (Γ)
using Context = std::unordered_map<std::string, Type>;

// 4. Ядро системи: Виведення типів
struct TypeError : std::runtime_error {
    using std::runtime_error::runtime_error;
};

Type infer_type(const Term& term, const Context& ctx) {
    return std::visit([&ctx](auto&& arg) -> Type {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, Var>) {
            auto it = ctx.find(arg.name);
            if (it == ctx.end()) throw TypeError("Undefined variable: " + arg.name);
            return it->second;
        } 
        else if constexpr (std::is_same_v<T, std::shared_ptr<Abs>>) {
            Context new_ctx = ctx;
            new_ctx[arg->param_name] = arg->param_type;
            Type body_type = infer_type(arg->body, new_ctx);
            return std::make_shared<TypeFunc>(TypeFunc{arg->param_type, body_type});
        } 
        else if constexpr (std::is_same_v<T, std::shared_ptr<App>>) {
            Type func_type = infer_type(arg->func, ctx);
            Type arg_type = infer_type(arg->arg, ctx);
            
            if (!std::holds_alternative<std::shared_ptr<TypeFunc>>(func_type)) {
                throw TypeError("Application of non-function");
            }
            auto f_type = std::get<std::shared_ptr<TypeFunc>>(func_type);
            if (!types_equal(f_type->arg_type, arg_type)) {
                throw TypeError("Type mismatch in application");
            }
            return f_type->ret_type;
        }
    }, term);
}
