#include <vector>
#include <cstdint>

template <typename FlowType = int64_t>
class EdmondsKarp {
public:
    struct Edge {
        int to;         // Індекс цільової вершини дуги (0 <= to < n)
        int rev;        // Позиція парного ребра у списку adj[to]
        FlowType cap;   // Початкова пропускна спроможність (cap >= 0)
        FlowType flow;  // Поточний потік через ребро (0 <= flow <= cap)
    };

    explicit EdmondsKarp(int vertices);
    // ... методи інтерфейсу
};
