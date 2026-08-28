#include <sstream>

class DiophantinePrinter {
public:
    static std::string to_string(const DiophantineContext& ctx, const ExprPtr& expr) {
        if (!expr) return "";
        std::ostringstream ss;
        print_node(ctx, expr, ss);
        return ss.str();
    }

private:
    static void print_node(const DiophantineContext& ctx, const ExprPtr& expr, std::ostringstream& ss) {
        switch (expr->kind) {
            case ExprKind::Const:
                ss << std::get<int64_t>(expr->payload);
                break;
            case ExprKind::Var:
                ss << ctx.variables()[std::get<uint32_t>(expr->payload)].name;
                break;
            case ExprKind::Add: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                ss << "(";
                print_node(ctx, b.lhs, ss);
                ss << " + ";
                print_node(ctx, b.rhs, ss);
                ss << ")";
                break;
            }
            case ExprKind::Sub: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                ss << "(";
                print_node(ctx, b.lhs, ss);
                ss << " - ";
                print_node(ctx, b.rhs, ss);
                ss << ")";
                break;
            }
            case ExprKind::Mul: {
                const auto& b = std::get<BinaryExprPayload>(expr->payload);
                ss << "(";
                print_node(ctx, b.lhs, ss);
                ss << " * ";
                print_node(ctx, b.rhs, ss);
                ss << ")";
                break;
            }
            case ExprKind::Sqr: {
                ss << "(";
                print_node(ctx, std::get<ExprPtr>(expr->payload), ss);
                ss << "^2)";
                break;
            }
        }
    }
};
