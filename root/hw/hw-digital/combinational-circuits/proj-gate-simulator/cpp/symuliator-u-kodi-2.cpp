// Вузол нетліста: який вентиль і звідки два його входи (за іменами)
struct Node {
    std::string name;   // ім'я вузла = підписаний проміжний дріт
    Op op;              // який вентиль
    std::string a, b;   // входи за іменами; b порожнє, якщо вхід один (NOT)
};

// Обчислити нетліст: signals відображає ім'я → його значення 0/1
std::map<std::string, int> evaluate(const std::vector<Node>& net,
                                    std::map<std::string, int> signals) {
    for (const Node& n : net) {                      // порядок — топологічний
        int va = signals.at(n.a);
        int vb = n.b.empty() ? 0 : signals.at(n.b);  // NOT має лише один вхід
        signals[n.name] = gate(n.op, va, vb);        // порахували — запам'ятали
    }
    return signals;
}
