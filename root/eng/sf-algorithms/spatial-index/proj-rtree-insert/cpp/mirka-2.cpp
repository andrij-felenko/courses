static const int M = 4;      // максимум записів у вузлі (у житті — скільки влазить у сторінку)
static const int m = 2;      // мінімум; Гуттман радить 30–40 % від M

struct Node;
struct Entry { Rect box; Node* child; int id; };   // child або id — залежно від рівня

struct Node {
    bool leaf;
    Node* parent;
    std::vector<Entry> e;
    explicit Node(bool lf) : leaf(lf), parent(nullptr) { e.reserve(M + 1); }
};

static Rect cover(const Node* n) {                 // MBR усього вузла
    Rect r = n->e[0].box;
    for (size_t i = 1; i < n->e.size(); ++i) r = unite(r, n->e[i].box);
    return r;
}
