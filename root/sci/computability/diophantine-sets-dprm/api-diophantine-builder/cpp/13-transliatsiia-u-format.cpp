#include <string>
#include <sstream>

class DiophantineSmtLib {
public:
    static std::string to_smt2(const DiophantineContext& ctx, const ExprPtr& expr) {
        std::ostringstream ss;
        ss << "(set-logic QF_NIA)\n";
        for (const auto& var : ctx.variables()) {
            ss << "(declare-const " << var.name << " Int)\n";
            ss << "(assert (>= " << var.name << " 0))\n";
        }
        ss << "(assert (= " << DiophantinePrinter::to_string(ctx, expr) << " 0))\n";
        ss << "(check-sat)\n(get-model)\n";
        return ss.str();
    }
};
