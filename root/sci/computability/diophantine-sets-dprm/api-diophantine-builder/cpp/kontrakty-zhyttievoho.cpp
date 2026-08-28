#include <string>
#include <vector>
#include <memory>
#include <optional>

class DiophantineContext {
public:
    ExprPtr make_const(int64_t val) {
        return std::make_shared<ExprNode>(ExprNode{ExprKind::Const, val});
    }

    ExprPtr make_var(std::string_view name) {
        for (const auto& v : vars_) {
            if (v.name == name) {
                return std::make_shared<ExprNode>(ExprNode{ExprKind::Var, v.id});
            }
        }
        const auto id = static_cast<uint32_t>(vars_.size());
        vars_.push_back(VariableInfo{std::string(name), id, false});
        return std::make_shared<ExprNode>(ExprNode{ExprKind::Var, id});
    }

    ExprPtr make_fresh_existential(std::string_view prefix) {
        const auto id = static_cast<uint32_t>(vars_.size());
        std::string name = std::string(prefix) + "_" + std::to_string(id);
        vars_.push_back(VariableInfo{name, id, true});
        return std::make_shared<ExprNode>(ExprNode{ExprKind::Var, id});
    }

    [[nodiscard]] const std::vector<VariableInfo>& variables() const noexcept {
        return vars_;
    }

private:
    std::vector<VariableInfo> vars_;
};

// Перевантаження операторів для виразної C++ нотації
inline ExprPtr operator+(ExprPtr lhs, ExprPtr rhs) {
    return std::make_shared<ExprNode>(ExprNode{ExprKind::Add, BinaryExprPayload{std::move(lhs), std::move(rhs)}});
}

inline ExprPtr operator-(ExprPtr lhs, ExprPtr rhs) {
    return std::make_shared<ExprNode>(ExprNode{ExprKind::Sub, BinaryExprPayload{std::move(lhs), std::move(rhs)}});
}

inline ExprPtr operator*(ExprPtr lhs, ExprPtr rhs) {
    return std::make_shared<ExprNode>(ExprNode{ExprKind::Mul, BinaryExprPayload{std::move(lhs), std::move(rhs)}});
}

inline PredPtr operator==(ExprPtr lhs, ExprPtr rhs) {
    auto diff = std::move(lhs) - std::move(rhs);
    return std::make_shared<PredNode>(PredNode{PredKind::EqualZero, std::move(diff)});
}

inline PredPtr operator&&(PredPtr lhs, PredPtr rhs) {
    return std::make_shared<PredNode>(PredNode{PredKind::And, BinaryPredPayload{std::move(lhs), std::move(rhs)}});
}

inline PredPtr operator||(PredPtr lhs, PredPtr rhs) {
    return std::make_shared<PredNode>(PredNode{PredKind::Or, BinaryPredPayload{std::move(lhs), std::move(rhs)}});
}
