#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <string_view>
#include <algorithm>
#include <stdexcept>

namespace regex {

enum class Opcode { Literal, Split, Match };

/* Структура вузла НКА з використанням ідіом C++20 */
struct State {
    Opcode op;
    char symbol{'\0'};
    State* out{nullptr};
    State* out1{nullptr};
    mutable int last_step{0};

    explicit State(char c) : op(Opcode::Literal), symbol(c) {}
    explicit State(Opcode op_type, State* o0 = nullptr, State* o1 = nullptr)
        : op(op_type), out(o0), out1(o1) {}
};

class ThompsonEngine {
public:
    explicit ThompsonEngine(std::string_view infix_pattern) {
        std::string postfix = re2post(infix_pattern);
        build_nfa(postfix);
    }

    /* Симуляція Pike VM над текстовим зрізом std::string_view */
    [[nodiscard]] bool match(std::string_view text) const {
        if (!start_state_) return false;

        std::vector<State*> current_states;
        std::vector<State*> next_states;
        current_states.reserve(arena_.size());
        next_states.reserve(arena_.size());

        int step = 1;
        add_state(current_states, start_state_, step);

        for (char ch : text) {
            step++;
            next_states.clear();

            for (State* s : current_states) {
                if (s->op == Opcode::Literal && s->symbol == ch) {
                    add_state(next_states, s->out, step);
                }
            }

            std::swap(current_states, next_states);
            if (current_states.empty()) break;
        }

        return std::any_of(current_states.begin(), current_states.end(),
            [](const State* s) { return s->op == Opcode::Match; });
    }

private:
    struct Fragment {
        State* start;
        std::vector<State**> out_list;
    };

    std::vector<std::unique_ptr<State>> arena_;
    State* start_state_{nullptr};

    /* Препроцесор Shunting-Yard для перетворення інфіксного виразу у постфіксний */
    static std::string re2post(std::string_view re) {
        int nalt = 0, natom = 0;
        std::string dst;
        dst.reserve(re.size() * 2);

        struct ParenFrame {
            int nalt;
            int natom;
        };
        std::vector<ParenFrame> paren;

        for (char c : re) {
            switch (c) {
                case '(':
                    if (natom > 1) {
                        natom--;
                        dst.push_back('.');
                    }
                    paren.push_back({nalt, natom});
                    nalt = 0;
                    natom = 0;
                    break;
                case '|':
                    if (natom == 0) throw std::invalid_argument("Некоректний шаблон синтаксису '|'");
                    while (--natom > 0) dst.push_back('.');
                    nalt++;
                    break;
                case ')':
                    if (paren.empty() || natom == 0) throw std::invalid_argument("Незбалансовані дужки");
                    while (--natom > 0) dst.push_back('.');
                    for (; nalt > 0; nalt--) dst.push_back('|');
                    nalt = paren.back().nalt;
                    natom = paren.back().natom;
                    paren.pop_back();
                    natom++;
                    break;
                case '*':
                    if (natom == 0) throw std::invalid_argument("Операнд '*' відсутній");
                    dst.push_back('*');
                    break;
                default:
                    if (natom > 1) {
                        natom--;
                        dst.push_back('.');
                    }
                    dst.push_back(c);
                    natom++;
                    break;
            }
        }
        while (--natom > 0) dst.push_back('.');
        for (; nalt > 0; nalt--) dst.push_back('|');

        return dst;
    }

    State* make_state(char c) {
        arena_.push_back(std::make_unique<State>(c));
        return arena_.back().get();
    }

    State* make_state(Opcode op, State* o0 = nullptr, State* o1 = nullptr) {
        arena_.push_back(std::make_unique<State>(op, o0, o1));
        return arena_.back().get();
    }

    static void patch(const std::vector<State**>& list, State* target) {
        for (State** ptr : list) {
            *ptr = target;
        }
    }

    static std::vector<State**> append_lists(std::vector<State**> v1, const std::vector<State**>& v2) {
        v1.insert(v1.end(), v2.begin(), v2.end());
        return v1;
    }

    void add_state(std::vector<State*>& list, State* s, int step) const {
        if (!s || s->last_step == step) return;
        s->last_step = step;

        if (s->op == Opcode::Split) {
            add_state(list, s->out, step);
            add_state(list, s->out1, step);
            return;
        }

        list.push_back(s);
    }

    void build_nfa(std::string_view pattern) {
        std::vector<Fragment> stack;

        for (char c : pattern) {
            switch (c) {
                case '|': {
                    auto e2 = stack.back(); stack.pop_back();
                    auto e1 = stack.back(); stack.pop_back();
                    State* s = make_state(Opcode::Split, e1.start, e2.start);
                    stack.push_back({s, append_lists(e1.out_list, e2.out_list)});
                    break;
                }
                case '*': {
                    auto e = stack.back(); stack.pop_back();
                    State* s = make_state(Opcode::Split, e.start, nullptr);
                    patch(e.out_list, s);
                    stack.push_back({s, {&s->out1}});
                    break;
                }
                case '.': {
                    auto e2 = stack.back(); stack.pop_back();
                    auto e1 = stack.back(); stack.pop_back();
                    patch(e1.out_list, e2.start);
                    stack.push_back({e1.start, e2.out_list});
                    break;
                }
                default: {
                    State* s = make_state(c);
                    stack.push_back({s, {&s->out}});
                    break;
                }
            }
        }

        if (!stack.empty()) {
            auto e = stack.back();
            State* match_state = make_state(Opcode::Match);
            patch(e.out_list, match_state);
            start_state_ = e.start;
        }
    }
};

} // namespace regex

int main() {
    try {
        regex::ThompsonEngine engine("(a|b)*abb");

        std::cout << "Тест 1 ('ababb'): " << (engine.match("ababb") ? "ЗБІГ" : "НЕМАЄ ЗБІГУ") << "\n";
        std::cout << "Тест 2 ('ababa'): " << (engine.match("ababa") ? "ЗБІГ" : "НЕМАЄ ЗБІГУ") << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
    }

    return 0;
}
