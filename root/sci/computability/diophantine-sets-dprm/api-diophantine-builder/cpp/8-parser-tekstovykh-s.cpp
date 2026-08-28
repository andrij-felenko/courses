#include <string_view>
#include <sstream>

class DiophantineParser {
public:
    static ExprPtr parse_sexpr(DiophantineContext& ctx, std::string_view text) {
        std::istringstream iss{std::string(text)};
        return parse_stream(ctx, iss);
    }

private:
    static ExprPtr parse_stream(DiophantineContext& ctx, std::istringstream& iss) {
        char ch;
        if (!(iss >> ch)) return nullptr;

        if (ch == '(') {
            std::string op;
            iss >> op;
            ExprPtr res = nullptr;
            if (op == "add") {
                auto l = parse_stream(ctx, iss);
                auto r = parse_stream(ctx, iss);
                res = l + r;
            } else if (op == "mul") {
                auto l = parse_stream(ctx, iss);
                auto r = parse_stream(ctx, iss);
                res = l * r;
            } else if (op == "const") {
                int64_t val;
                iss >> val;
                res = ctx.make_const(val);
            }
            iss >> ch; // ')'
            return res;
        } else {
            iss.putback(ch);
            std::string name;
            iss >> name;
            return ctx.make_var(name);
        }
    }
};
