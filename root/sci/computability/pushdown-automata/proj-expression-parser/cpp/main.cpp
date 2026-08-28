#include <cctype>
#include <cmath>
#include <map>
#include <stack>
#include <stdexcept>
#include <string>

struct Op {
    int    prec;                          // пріоритет: більше — міцніше в'яже
    bool   left;                          // лівоасоціативний?
    double (*apply)(double, double);      // сама дія
};

// Таблиця операторів — ЄДИНЕ місце, де живе пріоритет.
static const std::map<char, Op> OPS = {
    {'+', {1, true,  [](double a, double b) { return a + b; }}},
    {'-', {1, true,  [](double a, double b) { return a - b; }}},
    {'*', {2, true,  [](double a, double b) { return a * b; }}},
    {'/', {2, true,  [](double a, double b) { return a / b; }}},
    {'^', {3, false, [](double a, double b) { return std::pow(a, b); }}},
};

// Зняти один оператор і два його операнди — покласти назад результат.
static void applyTop(std::stack<double>& vals, std::stack<char>& ops) {
    const char op = ops.top(); ops.pop();
    if (vals.size() < 2)
        throw std::runtime_error(std::string("оператору бракує операнда: ") + op);
    const double b = vals.top(); vals.pop();   // правий операнд зняли ПЕРШИМ…
    const double a = vals.top(); vals.pop();   // …лівий другим
    vals.push(OPS.at(op).apply(a, b));
}

double evaluate(const std::string& src) {
    std::stack<double> vals;               // порахувати вже можна
    std::stack<char>   ops;                // ще ні — чекає

    for (std::size_t i = 0; i < src.size(); ) {
        const char c = src[i];

        if (std::isspace(static_cast<unsigned char>(c))) { ++i; continue; }

        if (std::isdigit(static_cast<unsigned char>(c))) {   // число цілком, не по цифрі
            std::size_t len = 0;
            vals.push(std::stod(src.substr(i), &len));       // len — де число скінчилося
            i += len;
            continue;
        }

        if (c == '(') { ops.push(c); ++i; continue; }        // бар'єр

        if (c == ')') {                                      // згорнути все до бар'єра
            while (!ops.empty() && ops.top() != '(') applyTop(vals, ops);
            if (ops.empty()) throw std::runtime_error("зайва закривна дужка");
            ops.pop();                                       // сам бар'єр геть
            ++i;
            continue;
        }

        const auto it = OPS.find(c);                         // оператор
        if (it == OPS.end())
            throw std::runtime_error(std::string("невідомий символ: ") + c);
        const Op& cur = it->second;
        while (!ops.empty() && ops.top() != '(') {           // бар'єр зупиняє порівняння
            const Op& top = OPS.at(ops.top());
            // ось воно, все правило — в одному if:
            if (top.prec > cur.prec || (top.prec == cur.prec && cur.left))
                applyTop(vals, ops);                         // вершині вже ніхто не завадить
            else
                break;                                       // вершина чекає далі
        }
        ops.push(c);
        ++i;
    }

    while (!ops.empty()) {                 // вхід скінчився — доганяємо відкладене
        if (ops.top() == '(') throw std::runtime_error("незакрита дужка");
        applyTop(vals, ops);
    }
    if (vals.size() != 1) throw std::runtime_error("вираз не склався");
    return vals.top();
}
