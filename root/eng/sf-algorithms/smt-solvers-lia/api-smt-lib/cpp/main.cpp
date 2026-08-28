#include <string_view>
#include <vector>
#include <optional>
#include <memory>
#include <stdexcept>

namespace smt {

class Context;
class Sort;
class Ast;
class Model;

enum class Result {
    Sat = 1,
    Unsat = -1,
    Unknown = 0
};

class Ast {
public:
    Ast(SmtContext ctx, SmtAst ast) : ctx_(ctx), ast_(ast) {}
    
    SmtAst raw() const noexcept { return ast_; }
    SmtContext ctx() const noexcept { return ctx_; }

    Ast operator+(const Ast& other) const;
    Ast operator-(const Ast& other) const;
    Ast operator*(int64_t constant) const;
    Ast operator<=(const Ast& other) const;
    Ast operator<(const Ast& other) const;
    Ast operator>=(const Ast& other) const;
    Ast operator>(const Ast& other) const;
    Ast operator==(const Ast& other) const;
    Ast operator&&(const Ast& other) const;
    Ast operator||(const Ast& other) const;
    Ast operator!() const;

private:
    SmtContext ctx_;
    SmtAst ast_;
};

class Solver {
public:
    explicit Solver(SmtContext ctx, std::string_view logic = "QF_LIA")
        : solver_(smt_solver_create(ctx, logic.data()), smt_solver_free) {
        if (!solver_) throw std::runtime_error("Failed to create SMT solver");
    }

    void add(const Ast& formula) {
        smt_solver_assert(solver_.get(), formula.raw());
    }

    void push() {
        smt_solver_push(solver_.get());
    }

    void pop(uint32_t levels = 1) {
        smt_solver_pop(solver_.get(), levels);
    }

    void interrupt() {
        smt_solver_interrupt(solver_.get());
    }

    Result check() {
        return static_cast<Result>(smt_solver_check(solver_.get()));
    }

    std::optional<int64_t> eval_int(const Ast& var) {
        auto* model = smt_solver_get_model(solver_.get());
        if (!model) return std::nullopt;
        
        int64_t val = 0;
        bool ok = smt_model_eval_int(model, var.raw(), &val);
        smt_model_free(model);
        
        if (!ok) return std::nullopt;
        return val;
    }

private:
    std::unique_ptr<SmtSolver_T, void(*)(SmtSolver)> solver_;
};

class Context {
public:
    Context() : ctx_(smt_context_create(), smt_context_free) {
        if (!ctx_) throw std::runtime_error("Failed to create SMT context");
    }

    SmtContext raw() const noexcept { return ctx_.get(); }

    Ast mk_int_const(std::string_view name) {
        auto sort = smt_sort_int(ctx_.get());
        return Ast(ctx_.get(), smt_mk_const(ctx_.get(), name.data(), sort));
    }

    Ast mk_numeral(int64_t val) {
        return Ast(ctx_.get(), smt_mk_int_num(ctx_.get(), val));
    }

    Solver mk_solver(std::string_view logic = "QF_LIA") {
        return Solver(ctx_.get(), logic);
    }

private:
    std::unique_ptr<SmtContext_T, void(*)(SmtContext)> ctx_;
};

} // namespace smt
