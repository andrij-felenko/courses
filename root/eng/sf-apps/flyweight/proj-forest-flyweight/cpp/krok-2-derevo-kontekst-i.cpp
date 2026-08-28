struct Tree {
    float           x, y, z;      // де стоїть          12 Б
    float           scale;        // який завбільшки     4 Б
    const TreeKind* kind;         // вказівник на СПІЛЬНИЙ вид   8 Б
};                                // sizeof(Tree) == 24 Б

class Forest {
    std::vector<Tree> trees_;
public:
    void reserve(std::size_t n)   { trees_.reserve(n); }
    void plant(float x, float y, float z, float s, const TreeKind* k) {
        trees_.push_back({x, y, z, s, k});
    }
    std::size_t size() const      { return trees_.size(); }
    const std::vector<Tree>& all() const { return trees_; }
};
