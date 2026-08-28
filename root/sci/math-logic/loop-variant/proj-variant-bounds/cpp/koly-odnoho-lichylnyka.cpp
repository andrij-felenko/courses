#include <vector>
#include <utility>
#include <cassert>
#include <cstddef>

enum class Kind { Num, Op, LPar, RPar };
struct Tok { Kind kind; long num = 0; char op = 0; };

int prec(char c) {
    switch (c) { case '+': case '-': return 1;
                 case '*': case '/': return 2; default: return 0; }
}
int tok_prec(const Tok& t) { return t.kind == Kind::Op ? prec(t.op) : 0; }

// Інфікс → постфікс. Один прохід = одна дія.
std::vector<Tok> to_rpn(const std::vector<Tok>& tokens) {
    std::vector<Tok> out, ops;
    std::size_t i = 0;

    while (i < tokens.size() || !ops.empty()) {
        // варіант — ПАРА; std::pair порівнюється словниково «з коробки»
        std::pair<std::size_t, std::size_t> v{tokens.size() - i, ops.size()};
        bool have = i < tokens.size();

        if (have && tokens[i].kind == Kind::Num) {
            out.push_back(tokens[i]); ++i;                   // число — одразу у вихід
        } else if (have && tokens[i].kind == Kind::LPar) {
            ops.push_back(tokens[i]); ++i;
        } else if (have && tokens[i].kind == Kind::RPar
                   && !ops.empty() && ops.back().kind == Kind::LPar) {
            ops.pop_back(); ++i;                             // дужка закрилася
        } else if (have && tokens[i].kind == Kind::Op
                   && (ops.empty() || ops.back().kind == Kind::LPar
                       || tok_prec(ops.back()) < prec(tokens[i].op))) {
            ops.push_back(tokens[i]); ++i;                   // оператор іде вгору
        } else {
            out.push_back(ops.back()); ops.pop_back();       // старший оператор — у вихід
        }

        // пара впала словниково (подвійні дужки — щоб коми не розбили макрос assert)
        assert((std::pair<std::size_t, std::size_t>{tokens.size() - i, ops.size()} < v));
    }
    return out;
}
