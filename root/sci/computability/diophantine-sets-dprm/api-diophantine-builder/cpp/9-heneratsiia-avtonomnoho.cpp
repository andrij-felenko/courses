#include <string>
#include <sstream>

class DiophantineCodeGen {
public:
    static std::string generate_c_function(const DiophantineContext& ctx, const ExprPtr& expr) {
        std::ostringstream ss;
        ss << "int64_t eval_dioph_poly(const int64_t* v) {\n";
        for (const auto& var : ctx.variables()) {
            ss << "    const int64_t " << var.name << " = v[" << var.id << "];\n";
        }
        ss << "    return " << DiophantinePrinter::to_string(ctx, expr) << ";\n}\n";
        return ss.str();
    }
};
