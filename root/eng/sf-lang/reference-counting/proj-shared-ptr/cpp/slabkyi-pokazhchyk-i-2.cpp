#include <cstdio>

struct Node {
    int          value;
    Shared<Node> next;      // сильне ребро (тут причаїться цикл)
    Weak<Node>   parent;    // слабке ребро (навмисно розірваний цикл)
    explicit Node(int v) : value(v) {}
    ~Node() { std::printf("  ~Node(%d)\n", value); }
};

int main() {
    Shared<Node> a(new Node(1));                 // strong = 1
    Shared<Node> b = a;                          // strong = 2  (копія)
    Weak<Node>   w = a;                          // strong = 2, weak = 1
    std::printf("use = %ld\n", a.use_count());   // 2

    if (Shared<Node> s = w.lock())               // підвищення: strong = 3
        std::printf("живий: %d\n", s->value);    // 1
    // s гине тут → strong = 2

    b = Shared<Node>();                          // release → strong = 1
    a = Shared<Node>();                          // release → strong = 0 → ~Node(1)
    std::printf("expired = %d\n", w.expired());  // 1  (true)
    return 0;                                    // w гине → блок звільнено
}
